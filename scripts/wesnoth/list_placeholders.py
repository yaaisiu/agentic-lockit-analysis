#!/usr/bin/env python3
# scripts/wesnoth/list_placeholders.py
# source: profile wesnoth (GATE 1) — inventory in-string tokens across one or more .pot/.po files.
"""
WHY: translators and QA must know every placeholder/markup/escape/entity style in play, how
often each occurs, and where — so nothing gets translated that should be preserved. This
codifies the recon that produced [[variables]] into a repeatable report (no LLM needed).
Imports po_parse (records) and po_tokens (the one true patterns).

Usage:  python list_placeholders.py <file...> [--examples N]
Output: per token-class → total count, distinct tokens, #entries, top tokens with a sample
        internal_id:line so you can navigate to the real string in gitignored data/.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings
import po_tokens


def inventory(paths, examples=1):
    per = {name: {"total": 0, "distinct": collections.Counter(), "entries": 0,
                  "example": {}} for name in po_tokens.PATTERNS}
    n_entries = 0
    for p in paths:
        for r in strings(parse_file(p)):
            n_entries += 1
            found = po_tokens.find(r["msgid"])
            for name, matches in found.items():
                if matches:
                    per[name]["entries"] += 1
                    per[name]["total"] += len(matches)
                    for tok in matches:
                        per[name]["distinct"][tok] += 1
                        per[name]["example"].setdefault(tok, f'{r["internal_id"]}@L{r["lineno"]}')
    return per, n_entries


def main(argv):
    examples = 1
    if "--examples" in argv:
        i = argv.index("--examples"); examples = int(argv[i + 1]); del argv[i:i + 2]
    paths = argv
    if not paths:
        print(__doc__); return
    per, n = inventory(paths)
    print(f"# placeholder inventory over {len(paths)} file(s), {n} strings\n")
    for name, d in per.items():
        if not d["total"]:
            continue
        print(f"## {name}: {d['total']} occurrences · {len(d['distinct'])} distinct · in {d['entries']} strings")
        for tok, cnt in d["distinct"].most_common(examples if examples > 1 else 5):
            print(f"    {cnt:5}  {tok[:32]:32}  e.g. {d['example'][tok]}")
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
