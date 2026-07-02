#!/usr/bin/env python3
# vault/library/script-templates/po_parse_template.py
# TEMPLATE — reusable across any gettext lockit. first_seen: wesnoth (session 000).
"""
PURPOSE: a dependency-free GNU gettext PO/POT reader that turns any .po/.pot into uniform
records with a stable identity — the foundation every gettext toolkit should start from.

WHY (rationale a less-capable agent can follow and reproduce):
- **No dependencies** (no polib/pandas): runs in a minimal env / under cheaper models / in an
  API runner. PO's grammar is small enough to parse safely by hand.
- **Keep strings RAW** (escapes like \\n intact): token-detection regexes are written against
  the raw form; `unescape()` is opt-in for when you need displayed text (e.g. length).
- **Preserve every field; nothing merged/dropped.** msgid, plural, msgctxt, all comment
  classes, flags. Identity = standard gettext key `(domain, msgctxt, msgid[, plural])` +
  a reorder-proof `sha1` internal id (line numbers are locators, not ids).

HOW TO PARAMETERISE for a new lockit:
- Set `domain` (defaults to filename stem = textdomain).
- If the project uses an INLINE CONTEXT PREFIX instead of msgctxt (see library convention
  [[inline-context-prefix]]), plug a splitter into `context_split` (Wesnoth used caret `^`).
- Build project-specific token detection in a separate module (keep this parser generic).

CLI: python po_parse_template.py <file.po|.pot> [--summary|--jsonl|--check]
"""
import sys, os, re, json, hashlib

SEP = "\x1f"
_ESCAPES = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\', 'a': '\a', 'b': '\b', 'f': '\f', 'v': '\v'}


def unescape(raw: str) -> str:
    out, i, n = [], 0, len(raw)
    while i < n:
        if raw[i] == '\\' and i + 1 < n:
            out.append(_ESCAPES.get(raw[i + 1], raw[i + 1])); i += 2
        else:
            out.append(raw[i]); i += 1
    return ''.join(out)


def _dequote(s: str) -> str:
    s = s.strip()
    return s[1:-1] if len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s


def _internal_id(domain, msgctxt, msgid, plural) -> str:
    h = hashlib.sha1(SEP.join([domain, msgctxt or "", msgid, plural or ""]).encode("utf-8"))
    return f"{domain}:{h.hexdigest()[:10]}"


def context_split(msgid):
    """Override for projects with an inline context prefix. Default: no split."""
    return None, msgid


def parse_file(path, domain=None):
    if domain is None:
        domain = os.path.splitext(os.path.basename(path))[0]
    lines = open(path, encoding="utf-8", errors="replace").readlines()
    records, cur, field, pidx = [], None, None, None

    def blank(ln):
        return {"domain": domain, "lineno": ln, "msgctxt": None, "msgid": "",
                "msgid_plural": None, "msgstr": [],
                "comments": {"translator": [], "extracted": [], "refs": [], "previous": []},
                "flags": [], "_c": False}

    def flush():
        nonlocal cur
        if cur and (cur["msgid"] != "" or cur["msgctxt"] is not None or cur["_c"] or any(cur["msgstr"])):
            cur["is_header"] = (cur["msgid"] == "" and cur["msgctxt"] is None)
            cur["context_prefix"], cur["display"] = context_split(cur["msgid"])
            cur["internal_id"] = None if cur["is_header"] else _internal_id(
                domain, cur["msgctxt"], cur["msgid"], cur["msgid_plural"])
            cur.pop("_c", None); records.append(cur)
        cur = None

    for idx, raw in enumerate(lines):
        line = raw.rstrip("\n"); ln = idx + 1
        if line.strip() == "":
            flush(); field = None; continue
        if cur is None:
            cur = blank(ln)
        if line.startswith("#"):
            cur["_c"] = True
            if line.startswith("#."): cur["comments"]["extracted"].append(line[2:].strip())
            elif line.startswith("#:"): cur["comments"]["refs"].append(line[2:].strip())
            elif line.startswith("#,"): cur["flags"] += [f.strip() for f in line[2:].split(",") if f.strip()]
            elif line.startswith("#|"): cur["comments"]["previous"].append(line[2:].strip())
            else: cur["comments"]["translator"].append(line[1:].strip())
        elif line.startswith("msgctxt "): field = "msgctxt"; cur["msgctxt"] = _dequote(line[8:])
        elif line.startswith("msgid_plural "): field = "msgid_plural"; cur["msgid_plural"] = _dequote(line[13:])
        elif line.startswith("msgid "): field = "msgid"; cur["msgid"] += _dequote(line[6:])
        elif line.startswith("msgstr["):
            m = re.match(r'msgstr\[(\d+)\]\s*(.*)', line); pidx = int(m.group(1)); field = "msgstr"
            while len(cur["msgstr"]) <= pidx: cur["msgstr"].append("")
            cur["msgstr"][pidx] += _dequote(m.group(2))
        elif line.startswith("msgstr "): field = "msgstr"; pidx = 0
        elif line.startswith('"'):
            v = _dequote(line)
            if field == "msgctxt": cur["msgctxt"] = (cur["msgctxt"] or "") + v
            elif field == "msgid_plural": cur["msgid_plural"] = (cur["msgid_plural"] or "") + v
            elif field == "msgid": cur["msgid"] += v
            elif field == "msgstr":
                if not cur["msgstr"]: cur["msgstr"].append("")
                cur["msgstr"][pidx or 0] += v
        if line.startswith("msgstr ") and field == "msgstr":
            if not cur["msgstr"]: cur["msgstr"].append("")
            cur["msgstr"][0] += _dequote(line[7:])
    flush()
    return records


def strings(records):
    return [r for r in records if not r.get("is_header")]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    path, mode = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "--summary")
    recs = parse_file(path); S = strings(recs)
    if mode == "--jsonl":
        for r in recs: print(json.dumps(r, ensure_ascii=False))
    elif mode == "--check":
        assert len({r["internal_id"] for r in S}) == len(S), "ids not unique"
        print(f"OK: {len(S)} strings, ids unique")
    else:
        print(f"{path}: {len(recs)} records, {len(S)} strings, "
              f"{len({r['internal_id'] for r in S})} unique ids")
