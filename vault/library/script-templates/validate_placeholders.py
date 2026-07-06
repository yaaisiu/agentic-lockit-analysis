#!/usr/bin/env python3
# vault/library/script-templates/validate_placeholders.py
# TEMPLATE — reusable cross-locale checker for any lockit. first_seen: wesnoth (session 001).
"""
PURPOSE: compare a TRANSLATION against its SOURCE and flag the structure that must survive
translation but frequently doesn't — invented/dropped placeholders, extra printf specifiers,
broken markup, wrong plural arity. Deterministic, no LLM, runs per-locale over a whole corpus.

WHY (rationale a less-capable agent can follow and reproduce):
- These defects are **game-breaking and invisible** to a human reviewer at scale: a
  misspelled `$num`→`$number` renders literally; a dropped `{count}` loses information; an
  unbalanced `<b>` corrupts the text engine. A machine check catches them all, cheaply.
- Embodies convention [[cross-locale-invariants]] (what must survive) and heuristic
  [[markup-families]] (validate markup per family). Reads with [[po_parse_template]].
- **Match by identity, compare against DISPLAY.** Entries pair by the natural key; a
  translation never carries an inline context prefix, so compare against the source's
  post-prefix display form (strip caret/`msgctxt`-inline before diffing).
- **Do not over-constrain.** Plural forms legitimately omit a variable the other form needs,
  and some strings legitimately add/drop whole words → flag those softly / for review, not as
  hard "bugs". The hard cases (placeholder invent, extra printf, broken markup, arity) are
  almost always real. See the convention's "legitimate divergence" note.

HOW TO PARAMETERISE for a new lockit:
- `NAMED`  : list of regexes for named placeholders ($var, {brace}, %(x)s, {0}, …).
- `PRINTF` : regex for positional/printf specifiers (or None to skip).
- `display(msgid)` : strip any inline context prefix (identity function if none).
- `check_markup(s)` : callback returning [(severity, msg)] — plug your validate_markup here
  (or `lambda s: []` to skip). Reuse the per-family checker from [[markup-families]].
- `key(rec)` : identity tuple; default = (msgctxt, msgid, msgid_plural).
- Reader: swap in your project's parse_file (this template calls po_parse_template).

CLI: python validate_placeholders.py <source> <translation> [--json]
Exit: non-zero if any hard ERROR (WARNs alone keep exit 0).
"""
import sys, os, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from po_parse_template import parse_file, strings   # sibling template reader
except ImportError:                                      # or point at your project reader
    parse_file = strings = None

# --- PARAMETERS (override per lockit) ----------------------------------------
NAMED = [re.compile(r'\$[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\[\d+\])?\|?'),  # $var / $obj.attr
         re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*\}')]                        # {brace}
PRINTF = re.compile(r'%[-#0-9.]*\d*\$?[sdiouxXeEfFgGcp%]')

def display(msgid):
    """Strip an inline context prefix if the project uses one (Wesnoth: text up to 1st '^')."""
    m = re.match(r'^[^\^]{1,40}?\^', msgid)
    return msgid[m.end():] if m else msgid

def check_markup(s):
    """Return [(severity, message)] for markup defects in `s`. Plug your validate_markup in."""
    return []

def key(r):
    return (r.get("msgctxt") or "", r["msgid"], r.get("msgid_plural") or "")
# -----------------------------------------------------------------------------


def named(text):
    out = set()
    for pat in NAMED:
        for t in pat.findall(text):
            out.add(t.rstrip("|"))
    return out


def printf_counts(text):
    return collections.Counter(PRINTF.findall(text)) if PRINTF else collections.Counter()


def nplurals_of(records):
    for r in records:
        if r.get("is_header"):
            hdr = r["msgstr"][0] if r.get("msgstr") else ""
            m = re.search(r"nplurals\s*=\s*(\d+)", hdr)
            return int(m.group(1)) if m else None
    return None


def check_pair(src_path, tr_path):
    src_recs, tr_recs = parse_file(src_path), parse_file(tr_path)
    src_by = {key(r): r for r in strings(src_recs)}
    nplurals = nplurals_of(tr_recs)
    findings = []                       # (severity, id, line, msg)
    stats = collections.Counter()

    def add(sev, r, msg):
        findings.append((sev, r.get("internal_id"), r.get("lineno"), msg)); stats[sev] += 1

    for tr in strings(tr_recs):
        if not any(tr.get("msgstr") or []):
            stats["untranslated"] += 1; continue
        stats["translated"] += 1
        src = src_by.get(key(tr))
        if src is None:
            add("ERROR", tr, "orphan: no matching source entry (stale msgid?)"); continue
        is_plural = src.get("msgid_plural") is not None
        src_names = named(display(src["msgid"]))
        src_pf = printf_counts(display(src["msgid"]))
        if is_plural:
            src_names |= named(src["msgid_plural"])
            src_pf = src_pf | printf_counts(src["msgid_plural"])
        if is_plural and nplurals is not None:
            nonempty = sum(1 for s in tr["msgstr"] if s != "")
            if len(tr["msgstr"]) < nplurals or nonempty < nplurals:
                add("WARN", tr, f"plural arity: expected {nplurals}, got {len(tr['msgstr'])}"
                                f" ({nonempty} non-empty)")
        for i, s in enumerate(tr["msgstr"]):
            if s == "":
                continue
            tag = f"[{i}] " if is_plural else ""
            invented = named(s) - src_names
            if invented:
                add("ERROR", tr, f"{tag}invented placeholder(s): {sorted(invented)}")
            if not is_plural:
                missing = src_names - named(s)
                if missing:
                    add("ERROR", tr, f"dropped placeholder(s): {sorted(missing)}")
            extra_pf = printf_counts(s) - src_pf
            if extra_pf:
                add("ERROR", tr, f"{tag}printf not in source: {sorted(extra_pf.elements())}")
            for sev, msg in check_markup(s):
                add(sev, tr, f"{tag}markup: {msg}")
    return findings, stats, nplurals


def main(argv):
    as_json = "--json" in argv
    if as_json: argv.remove("--json")
    if len(argv) < 2 or parse_file is None:
        print(__doc__); return 0
    findings, stats, nplurals = check_pair(argv[0], argv[1])
    errors = [f for f in findings if f[0] == "ERROR"]
    if as_json:
        print(json.dumps({"stats": dict(stats), "nplurals": nplurals,
                          "findings": [{"sev": s, "id": i, "line": l, "msg": m}
                                       for s, i, l, m in findings]}, ensure_ascii=False, indent=2))
    else:
        print(f"# translated={stats['translated']} untranslated={stats['untranslated']} "
              f"ERROR={stats['ERROR']} WARN={stats['WARN']} (nplurals={nplurals})")
        for sev, iid, ln, msg in findings:
            print(f"  {sev:5} {iid}@L{ln}: {msg}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
