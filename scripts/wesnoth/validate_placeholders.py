#!/usr/bin/env python3
# scripts/wesnoth/validate_placeholders.py
# source: profile wesnoth — Phase 6 (multi-language). The first cross-locale check.
"""
WHY (the multi-language goal): the English .pot is the source of truth for STRUCTURE — every
$variable, {brace} placeholder, %printf specifier, and markup tag it contains must survive
translation intact. A translator who drops `$gold`, invents `$glod`, unbalances `<b>…</b>`,
or gives too few plural forms ships a string that renders wrong or crashes the text engine.
This script compares a translation .po against its English .pot and flags exactly those
defects — deterministically, no LLM, so it can run per-locale over the whole corpus.

============================  WHAT IT CHECKS (and the reasoning)  ============================
Entries are matched by their natural gettext key (msgctxt, msgid, msgid_plural) — identical
between .pot and .po because the translation keeps the English msgid as the key. For every
TRANSLATED entry (non-empty msgstr) we compare tokens against the SOURCE side:

  * ^-context is STRIPPED for display, so the source reference is the msgid's `display`
    (post-caret) part, never the raw msgid — a translation never contains the `^` prefix.

  1. named placeholders ($var, {brace}) — the set of names the SOURCE offers.
       - invented/misspelled name in a translation (name ∉ source)  → ERROR (the classic bug)
       - for NON-plural entries, a source name missing from the msgstr → ERROR (dropped var)
       - for PLURAL entries we do NOT require every form to carry every name: a singular
         form legitimately omits the count variable. We only forbid inventing names.
  2. printf specifiers (%d %s …) — a translation may not introduce a specifier the source
     lacks (count-sensitive) → ERROR. (Rare in Wesnoth, but fatal when wrong.)
  3. markup — each msgstr is run through validate_markup.check_string (auto-detects Pango /
     DocBook / po4a). A translator breaking a tag is a translation-side hard issue.
  4. plural arity — a plural entry must provide exactly the locale's nplurals forms (read
     from the .po header Plural-Forms), none empty → else WARN (under/over-translated).

Design: reuses po_parse (records), po_tokens (the one true patterns), validate_markup (the
one true balance check). No new token definitions live here — single source of truth holds.
=============================================================================================

Usage:  python validate_placeholders.py <source.pot> <translation.po> [--json] [--limit N]
Exit:   non-zero if any hard ERROR is found (WARNs alone keep exit 0).
"""
import sys, os, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings
import po_tokens
import validate_markup

_WML = po_tokens.PATTERNS["wml_var"]
_BRACE = po_tokens.PATTERNS["brace_var"]
_PRINTF = po_tokens.PATTERNS["printf"]


def _key(r):
    """Natural gettext identity, domain-independent (msgid is shared source↔translation)."""
    return (r["msgctxt"] or "", r["msgid"], r["msgid_plural"] or "")


def named(text):
    """Set of named placeholders ($var, {brace}) in a string. Trailing | terminator on a
    WML var is normalised away so `$x` and `$x|` compare as the same variable."""
    out = set()
    for t in _WML.findall(text):
        out.add(t.rstrip("|"))
    for t in _BRACE.findall(text):
        out.add(t)
    return out


def printf_counts(text):
    return collections.Counter(_PRINTF.findall(text))


def nplurals_of(records):
    """Read nplurals=N from the .po header's Plural-Forms. None if absent."""
    for r in records:
        if r.get("is_header"):
            hdr = r["msgstr"][0] if r["msgstr"] else ""
            m = re.search(r"nplurals\s*=\s*(\d+)", hdr)
            return int(m.group(1)) if m else None
    return None


def check_pair(src_path, tr_path):
    src_recs = parse_file(src_path)
    tr_recs = parse_file(tr_path)
    src_by = {_key(r): r for r in strings(src_recs)}
    nplurals = nplurals_of(tr_recs)

    findings = []                       # (severity, key_id, msg)
    stats = collections.Counter()

    def add(sev, r, msg):
        findings.append((sev, r["internal_id"], r["lineno"], msg))
        stats[sev] += 1

    for tr in strings(tr_recs):
        forms = [s for s in tr["msgstr"]]
        if not any(forms):
            stats["untranslated"] += 1
            continue
        stats["translated"] += 1
        src = src_by.get(_key(tr))
        if src is None:
            add("ERROR", tr, "orphan: no matching source entry (stale msgid?)")
            continue

        is_plural = src["msgid_plural"] is not None
        # SOURCE reference: display (post-caret) of msgid, plus plural form if any.
        src_names = named(src["display"])
        src_pf = printf_counts(src["display"])
        if is_plural:
            src_names |= named(src["msgid_plural"])
            src_pf = src_pf | printf_counts(src["msgid_plural"])   # Counter union = max per key

        # plural arity (translation must supply exactly nplurals non-empty forms)
        if is_plural and nplurals is not None:
            nonempty = sum(1 for s in tr["msgstr"] if s != "")
            if len(tr["msgstr"]) < nplurals or nonempty < nplurals:
                add("WARN", tr, f"plural arity: expected {nplurals} forms, "
                                f"got {len(tr['msgstr'])} ({nonempty} non-empty)")

        for i, s in enumerate(tr["msgstr"]):
            if s == "":
                continue
            tag = f"[{i}] " if is_plural else ""
            tnames = named(s)
            invented = tnames - src_names
            if invented:
                add("ERROR", tr, f"{tag}invented/misspelled placeholder(s): {sorted(invented)} "
                                 f"(source offers {sorted(src_names) or '—'})")
            if not is_plural:
                missing = src_names - tnames
                if missing:
                    add("ERROR", tr, f"dropped placeholder(s): {sorted(missing)}")
            # printf: translation may not introduce a specifier the source lacks
            extra_pf = printf_counts(s) - src_pf
            if extra_pf:
                add("ERROR", tr, f"{tag}printf specifier(s) not in source: {sorted(extra_pf.elements())}")
            # markup integrity of the translation itself (severity flows from the checker:
            # a broken tag is ERROR, an unescaped '&' is WARN — see validate_markup.check_string)
            for sev, msg in validate_markup.check_string(s):
                add(sev, tr, f"{tag}markup: {msg}")

    return findings, stats, nplurals


def main(argv):
    as_json = "--json" in argv
    if as_json:
        argv.remove("--json")
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit"); limit = int(argv[i + 1]); del argv[i:i + 2]
    if len(argv) < 2:
        print(__doc__); return 0
    src_path, tr_path = argv[0], argv[1]
    findings, stats, nplurals = check_pair(src_path, tr_path)
    errors = [f for f in findings if f[0] == "ERROR"]

    if as_json:
        print(json.dumps({
            "source": src_path, "translation": tr_path, "nplurals": nplurals,
            "stats": dict(stats),
            "findings": [{"severity": s, "id": i, "line": ln, "msg": m}
                         for (s, i, ln, m) in findings],
        }, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    locale = os.path.basename(tr_path)
    print(f"# {os.path.basename(os.path.dirname(tr_path)) or src_path} ← {locale}  "
          f"(nplurals={nplurals})")
    print(f"# translated={stats['translated']} untranslated={stats['untranslated']} "
          f"ERROR={stats['ERROR']} WARN={stats['WARN']}")
    shown = findings if limit is None else findings[:limit]
    for sev, iid, ln, msg in shown:
        print(f"  {sev:5} {iid}@L{ln}: {msg}")
    if limit is not None and len(findings) > limit:
        print(f"  … {len(findings) - limit} more")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
