#!/usr/bin/env python3
# scripts/wesnoth/extract_by_type.py
# source: profile wesnoth (GATE 1) — pull entries by textdomain, ^-context prefix, or substring.
"""
WHY: "string type" in Wesnoth = the textdomain (file) + the ^-context prefix (see profile.md).
This turns those axes into a filter so you can extract exactly one slice (e.g. all gender
forms, all UI of a given context, all dialogue) without hand-grepping the raw PO. Emits our
internal_id so results are traceable back to the profile.

Usage:
  python extract_by_type.py <file...> [--prefix P] [--contains S] [--has TOKENCLASS] [--jsonl]
    --prefix P        only entries whose ^-context prefix == P (e.g. female)
    --contains S      only entries whose display text contains S (case-insensitive)
    --has CLASS       only entries containing a token class from po_tokens (e.g. wml_var)
    --jsonl           full records as JSON lines (default: id, prefix, display)
NOTE: prints real source text — for local/data use only; never commit its output.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings
import po_tokens


def main(argv):
    opts = {"--prefix": None, "--contains": None, "--has": None}
    jsonl = "--jsonl" in argv
    if jsonl:
        argv.remove("--jsonl")
    for k in list(opts):
        if k in argv:
            i = argv.index(k); opts[k] = argv[i + 1]; del argv[i:i + 2]
    paths = argv
    if not paths:
        print(__doc__); return
    n = 0
    for p in paths:
        for r in strings(parse_file(p)):
            if opts["--prefix"] is not None and r["context_prefix"] != opts["--prefix"]:
                continue
            if opts["--contains"] and opts["--contains"].lower() not in r["display"].lower():
                continue
            if opts["--has"] and not po_tokens.find(r["msgid"]).get(opts["--has"]):
                continue
            n += 1
            if jsonl:
                print(json.dumps(r, ensure_ascii=False))
            else:
                pre = f'[{r["context_prefix"]}] ' if r["context_prefix"] else ""
                print(f'{r["internal_id"]}  {pre}{r["display"][:100]}')
    if not jsonl:
        print(f"\n# {n} matching entries", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
