#!/usr/bin/env python3
"""arrays.py — expose JSON-array cells element-by-element + check length parity.

WHY (Marcin, GATE 1 Q3): 30 keys store a MULTI-VALUE cell as a JSON array (settlement tiers,
button pairs, random flavour). The translatable unit is each ELEMENT, and the one hard
invariant is that every locale keeps the SAME NUMBER of elements as the source (a translator
who drops an option breaks the game's indexing). This tool:
  * lists every array key with its per-locale element counts, and
  * flags length mismatches vs the source (en).
It does NOT compare elements by index across locales, because the order rule is PER KEY:
ordered tiers must align but interchangeable pairs / random-pick sets may be reordered
(like Veloren .aN random-pick arrays — see cross-locale-invariants). So we check LENGTH, an
always-valid invariant, and leave per-element order to human review.

    python3 arrays.py [csv]                 # summary + any length mismatches
    python3 arrays.py [csv] --key tab_data_titles:world   # show one array key's elements
"""
import sys
import csv_parse as P


def array_keys(lk):
    return [r for r in lk.records if r.shape(P.SOURCE) == P.ARRAY]


def main(argv):
    path = '../../data/a-dark-forest/localization.csv'
    want_key = None
    i = 0
    while i < len(argv):
        if argv[i] == '--key': want_key = argv[i + 1]; i += 2
        else: path = argv[i]; i += 1
    lk = P.parse_file(path)
    recs = array_keys(lk)

    if want_key:
        r = next((x for x in recs if x.key == want_key), None)
        if not r:
            raise SystemExit(f"{want_key} is not an array-valued key")
        print(f"# {r.key}   ({r.description})")
        for loc in lk.locales:
            els = r.elements(loc)
            if els is None:
                print(f"  {loc:<4} (not an array / empty)")
            else:
                print(f"  {loc:<4} [{len(els)}] {els}")
        return 0

    print(f"# Array-valued keys: {len(recs)}  (source={P.SOURCE})\n")
    mism = 0
    for r in recs:
        src = r.elements(P.SOURCE)
        src_n = len(src) if src is not None else None
        bad = []
        for loc in lk.locales:
            if loc == P.SOURCE: continue
            v = r.values[loc]
            if v.strip() == '':      # untranslated → not a defect
                continue
            els = r.elements(loc)
            if els is None:
                bad.append(f"{loc}:not-array")
            elif src_n is not None and len(els) != src_n:
                bad.append(f"{loc}:{len(els)}≠{src_n}")
        flag = '  <<< LENGTH MISMATCH' if bad else ''
        if bad:
            mism += 1
        print(f"  {r.key:<32} en=[{src_n}] {' '.join(bad) if bad else 'all locales OK'}{flag}")
    print(f"\nkeys with a length mismatch: {mism}")
    return 1 if mism else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
