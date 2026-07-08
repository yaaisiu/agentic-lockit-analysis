#!/usr/bin/env python3
"""validate_placeholders.py — CROSS-LOCALE invariants: source (en) vs each translation.

WHY (convention [[cross-locale-invariants]]): most structure in the English source must
survive translation, and the game-breaking defects (a dropped {0}, a mismatched array length)
are invisible to a human reviewer at 676×8 scale. This checks, per translated cell:
  1. FORMAT SLOTS {0}..{N}: the translation must use exactly the same SET of indices as en —
     not invent {3} the source lacks (renders literal / index error), not drop one en needs.
  2. ARRAY LENGTH: an array cell must keep en's element count (see arrays.py for the why the
     order is NOT checked — per-key order rule).
It is deliberately CONSERVATIVE to avoid false positives (the discipline from Wesnoth/Veloren):
  * a blank translation = untranslated, skipped (not "dropped").
  * literal \\n is NOT enforced (line-break placement is a translator's choice).
  * whole-word add/drop is NOT flagged (only placeholders/arrays, which are almost always real).
This is a prepared tool: our focus is English analysis, but it is built + tested now and run in
earnest at the translation phase.

    python3 validate_placeholders.py [csv] [--locale pl] [--warn]
"""
import sys, re, collections
import csv_parse as P

SLOT = re.compile(r'\{(\d+)\}')


def slot_set(s):
    return frozenset(SLOT.findall(s))


def main(argv):
    path = '../../data/a-dark-forest/localization.csv'
    only = None
    for i, t in enumerate(argv):
        if t == '--locale': only = argv[i + 1]
        elif not t.startswith('--') and (i == 0 or argv[i - 1] != '--locale'): path = t
    lk = P.parse_file(path)
    targets = [only] if only else [l for l in lk.locales if l != P.SOURCE]

    defects = collections.defaultdict(list)   # locale -> [msg]
    for r in lk.records:
        if r.is_deprecated:
            continue
        src = r.values[P.SOURCE]
        for loc in targets:
            tv = r.values[loc]
            if tv.strip() == '':
                continue   # untranslated — not a defect
            # 1) format-slot parity
            ss, ts = slot_set(src), slot_set(tv)
            if ss != ts:
                invented = sorted(ts - ss); dropped = sorted(ss - ts)
                parts = []
                if invented: parts.append(f"invented {{{','.join(invented)}}}")
                if dropped:  parts.append(f"dropped {{{','.join(dropped)}}}")
                defects[loc].append(f"row {r.row} {r.key}: slot mismatch — {'; '.join(parts)}")
            # 2) array length parity
            if r.shape(P.SOURCE) == P.ARRAY:
                se, te = r.elements(P.SOURCE), r.elements(loc)
                if te is None:
                    defects[loc].append(f"row {r.row} {r.key}: source is array but {loc} is not")
                elif len(se) != len(te):
                    defects[loc].append(f"row {r.row} {r.key}: array len {len(te)}≠{len(se)}")

    total = sum(len(v) for v in defects.values())
    print(f"# cross-locale placeholder/array check — {path}")
    print(f"source={P.SOURCE}  targets={targets}")
    print(f"defects: {total}\n")
    for loc in targets:
        print(f"  {loc:<4} {len(defects[loc])}")
    if '--warn' in argv or total:
        for loc in targets:
            for m in defects[loc]:
                print(f"  [{loc}] {m}")
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
