#!/usr/bin/env python3
# scripts/wesnoth/po_parse.py
# source: profile wesnoth (GATE 1 confirmed 2026-07-02) — regenerate via lockit-wesnoth-toolkit skill
"""
THE foundation reader for the Wesnoth lockit. Every other script imports this.

=========================  WHY THIS EXISTS / HOW IT WORKS  =========================
(Written so a *less-capable* agent — or a future you — can rely on it without re-deriving.)

The Wesnoth lockit is a set of **GNU gettext PO templates** (`.pot`). It is NOT a
spreadsheet: there are no columns, no key field, no char-limit field. So this parser turns
each `.pot` file into a list of uniform *records* that DO have named fields — giving every
downstream script one stable shape to work with.

Design decisions and the reasons for them:

1. **Dependency-free.** No `polib`/`pandas`. The system must run under cheap models and
   later inside an API runner with a minimal environment, so we parse PO by hand. PO's
   grammar is simple enough (see below) that this is safe and testable.

2. **Keep the RAW string (escapes intact).** In the file, a line break is the two
   characters backslash+`n` ("\\n"), a tab is "\\t", etc. All our detection regexes
   (placeholders, markup, escapes — see vault/lockits/wesnoth/variables.md) are written
   against that RAW form, so we store it verbatim and DO NOT unescape. `unescape()` is
   provided for when you need the displayed text (e.g. measuring length). Storing raw is
   the lossless choice; unescaping is a lossy view you opt into.

3. **Preserve every field separately — never merge or drop (GATE 1 rule).** msgid, plural,
   msgctxt, the `^`-context, and ALL comments (`#.` extracted, `#:` refs, `#,` flags,
   `#|` previous, `# ` translator) are kept as distinct fields. `^`-prefix and `#.` ids are
   each incomplete/non-unique, so we never collapse identity onto them.

4. **Identity = the standard gettext key, generalised.** A record's natural key is
   `(domain, msgctxt, msgid[, msgid_plural])`. Wesnoth never uses `msgctxt`, so
   `(domain, msgid)` is unique in practice — but we keep `msgctxt` in the key so this same
   parser works on any other `.po` file that DOES use it. We also mint a compact, reorder-
   proof `internal_id = "<domain>:" + sha1(domain ⋮ msgctxt ⋮ msgid ⋮ plural)[:10]`
   (⋮ = the 0x1f separator, which cannot occur in the text). Line numbers are a *locator*,
   never the id — entries move when strings are added.

5. **The `^` caret context (Wesnoth-specific).** The engine hides everything up to and
   including the first `^` before display. We split it into `context_prefix` + `display`
   for convenience, but we ALSO keep the whole `msgid`, because the raw msgid is the key.

PO grammar we handle: entries separated by blank line(s); each entry = optional comment
lines then optional `msgctxt`, then `msgid`, optional `msgid_plural`, then `msgstr` or
`msgstr[N]`; any of those quoted values may continue over multiple `"..."` lines. The
first entry has an empty `msgid ""` and is the header (metadata in its msgstr).
====================================================================================

CLI:
  python po_parse.py <file.pot> [--summary | --jsonl | --check]
  # --summary : human counts (default)   --jsonl : one record per line   --check : self-test
Import:
  from po_parse import parse_file, unescape
"""
import sys, os, re, json, hashlib

SEP = "\x1f"  # unit separator: cannot appear in PO text, so safe as a key delimiter
CARET_RE = re.compile(r'^([^\^]{1,40}?)\^')      # short context token before first ^
_ESCAPES = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\', 'a': '\a', 'b': '\b', 'f': '\f', 'v': '\v'}


def unescape(raw: str) -> str:
    """Turn RAW PO string content (escapes as written) into the displayed text.
    Opt-in and lossy — use only when you need real characters (e.g. length)."""
    out, i, n = [], 0, len(raw)
    while i < n:
        c = raw[i]
        if c == '\\' and i + 1 < n:
            out.append(_ESCAPES.get(raw[i + 1], raw[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def _dequote(s: str) -> str:
    """Strip the surrounding quotes of a PO value token, keeping inner escapes RAW."""
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def _internal_id(domain, msgctxt, msgid, plural) -> str:
    h = hashlib.sha1(SEP.join([domain, msgctxt or "", msgid, plural or ""]).encode("utf-8"))
    return f"{domain}:{h.hexdigest()[:10]}"


def parse_file(path: str, domain: str = None):
    """Parse one .po/.pot file into a list of record dicts. `domain` defaults to the
    filename stem (the gettext textdomain)."""
    if domain is None:
        domain = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    records = []
    cur = None
    field = None          # which multi-line value we're currently appending to
    plural_idx = None

    def flush():
        nonlocal cur
        if cur is not None and (cur["msgid"] != "" or cur["msgctxt"] is not None
                                or cur["_comments"] or any(cur["msgstr"])):
            _finalize(cur, domain)
            records.append(cur)
        cur = None

    def blank(lineno):
        return {"domain": domain, "lineno": lineno, "msgctxt": None,
                "msgid": "", "msgid_plural": None, "msgstr": [],
                "comments": {"translator": [], "extracted": [], "refs": [], "previous": []},
                "flags": [], "_comments": False}

    for idx, raw in enumerate(lines):
        line = raw.rstrip("\n")
        lineno = idx + 1
        if line.strip() == "":
            flush(); field = None; continue
        if cur is None:
            cur = blank(lineno)
        if line.startswith("#"):
            cur["_comments"] = True
            if line.startswith("#."):   cur["comments"]["extracted"].append(line[2:].strip())
            elif line.startswith("#:"): cur["comments"]["refs"].append(line[2:].strip())
            elif line.startswith("#,"): cur["flags"] += [f.strip() for f in line[2:].split(",") if f.strip()]
            elif line.startswith("#|"): cur["comments"]["previous"].append(line[2:].strip())
            else:                       cur["comments"]["translator"].append(line[1:].strip())
            continue
        if line.startswith("msgctxt "):
            field = "msgctxt"; cur["msgctxt"] = _dequote(line[len("msgctxt "):])
        elif line.startswith("msgid_plural "):
            field = "msgid_plural"; cur["msgid_plural"] = _dequote(line[len("msgid_plural "):])
        elif line.startswith("msgid "):
            field = "msgid"; cur["msgid"] += _dequote(line[len("msgid "):])
        elif line.startswith("msgstr["):
            m = re.match(r'msgstr\[(\d+)\]\s*(.*)', line)
            plural_idx = int(m.group(1)); field = "msgstr"
            while len(cur["msgstr"]) <= plural_idx: cur["msgstr"].append("")
            cur["msgstr"][plural_idx] += _dequote(m.group(2))
        elif line.startswith("msgstr "):
            field = "msgstr"; plural_idx = 0
            if not cur["msgstr"]: cur["msgstr"].append("")
            cur["msgstr"][0] += _dequote(line[len("msgstr "):])
        elif line.startswith('"'):
            val = _dequote(line)
            if field == "msgctxt": cur["msgctxt"] = (cur["msgctxt"] or "") + val
            elif field == "msgid_plural": cur["msgid_plural"] = (cur["msgid_plural"] or "") + val
            elif field == "msgid": cur["msgid"] += val
            elif field == "msgstr":
                if not cur["msgstr"]: cur["msgstr"].append("")
                cur["msgstr"][plural_idx or 0] += val
    flush()
    return records


def _finalize(rec, domain):
    """Derive is_header, ^-context split, and internal_id. Keeps msgid whole (it's the key)."""
    rec["is_header"] = (rec["msgid"] == "" and rec["msgctxt"] is None)
    m = CARET_RE.match(rec["msgid"])
    rec["context_prefix"] = m.group(1) if m else None
    rec["display"] = rec["msgid"][m.end():] if m else rec["msgid"]
    rec["internal_id"] = None if rec["is_header"] else _internal_id(
        domain, rec["msgctxt"], rec["msgid"], rec["msgid_plural"])
    rec.pop("_comments", None)
    return rec


def strings(records):
    """The translatable entries (drop the header)."""
    return [r for r in records if not r.get("is_header")]


def _summary(path):
    recs = parse_file(path)
    S = strings(recs)
    caret = sum(1 for r in S if r["context_prefix"])
    plural = sum(1 for r in S if r["msgid_plural"] is not None)
    withref = sum(1 for r in S if r["comments"]["refs"])
    withdot = sum(1 for r in S if r["comments"]["extracted"])
    ids = {r["internal_id"] for r in S}
    print(f"file: {path}")
    print(f"  total records: {len(recs)}  header: {len(recs)-len(S)}  strings: {len(S)}")
    print(f"  unique internal_id: {len(ids)}  (collisions: {len(S)-len(ids)})")
    print(f"  ^context: {caret}   msgid_plural: {plural}   with #: {withref}   with #.: {withdot}")
    ex = next((r for r in S if r["context_prefix"]), S[0])
    print(f"  sample record @L{ex['lineno']}: id={ex['internal_id']} prefix={ex['context_prefix']!r} "
          f"display[:40]={ex['display'][:40]!r}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(0)
    path = args[0]
    mode = args[1] if len(args) > 1 else "--summary"
    if mode == "--jsonl":
        for r in parse_file(path):
            print(json.dumps(r, ensure_ascii=False))
    elif mode == "--check":
        recs = parse_file(path); S = strings(recs)
        assert len({r["internal_id"] for r in S}) == len(S), "internal_id not unique!"
        assert all(r["msgid"] for r in S), "empty msgid among strings!"
        print(f"OK: {len(S)} strings, ids unique, msgids non-empty")
    else:
        _summary(path)
