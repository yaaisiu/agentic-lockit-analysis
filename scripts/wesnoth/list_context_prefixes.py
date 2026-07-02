#!/usr/bin/env python3
# scripts/wesnoth/list_context_prefixes.py
# source: profile wesnoth (GATE 1, Q4) — codifies the ^-context prefix registry generator.
"""
WHY: the ^-context prefix is Wesnoth's disambiguation/subtype axis, and Marcin wants the
FULL, evidenced set (it grows as more domains/files arrive — tracked T4). This regenerates
the registry deterministically from any set of files, so vault/lockits/wesnoth/
context-prefixes.md is never hand-maintained or stale.

Usage:  python list_context_prefixes.py <file...> [--family FAM]
Output: distinct prefixes with count, family, domains, first occurrence pointer.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings


def family(p):
    if p in ("female", "male", "gender"): return "gender"
    if p.startswith(("addon", "addons")): return "add-ons"
    if p.startswith(("prefix_", "infix_")): return "SI number units"
    if p.startswith(("conjunct", "disjunct")): return "list grammar"
    if "hotkey" in p: return "hotkeys"
    if p.startswith(("filesystem", "save_compression", "cache", "dir_size")): return "files/storage"
    if p.startswith(("log_level", "cpu_architecture", "operating_system", "pixel_scale", "game_version")):
        return "system/env"
    return "other/UI"


def build(paths):
    reg = {}
    for p in paths:
        for r in strings(parse_file(p)):
            pre = r["context_prefix"]
            if not pre:
                continue
            d = reg.setdefault(pre, {"n": 0, "doms": set(), "first": f'{r["domain"]}:{r["lineno"]}'})
            d["n"] += 1; d["doms"].add(r["domain"])
    return reg


def main(argv):
    fam_filter = None
    if "--family" in argv:
        i = argv.index("--family"); fam_filter = argv[i + 1]; del argv[i:i + 2]
    paths = argv
    if not paths:
        print(__doc__); return
    reg = build(paths)
    fams = collections.Counter(family(p) for p in reg)
    print(f"# {len(reg)} distinct prefixes / {sum(d['n'] for d in reg.values())} entries "
          f"over {len(paths)} file(s)")
    print("# families: " + ", ".join(f"{f}={c}" for f, c in fams.most_common()))
    print(f"\n{'prefix':32} {'n':>4}  {'family':16} first@")
    for pre, d in sorted(reg.items(), key=lambda kv: (-kv[1]["n"], kv[0])):
        if fam_filter and family(pre) != fam_filter:
            continue
        print(f"{pre[:32]:32} {d['n']:>4}  {family(pre):16} {d['first']}")


if __name__ == "__main__":
    main(sys.argv[1:])
