#!/usr/bin/env python3
"""report.py — "what we know" about the A Dark Forest lockit, honestly.

WHY: the profile is prose; this is the same picture regenerated from the live file, so a
number that drifts from the doc is caught. It is deliberately HONEST about completeness —
it separates INTENTIONAL blanks ([EMPTY]) from UNTRANSLATED cells (Marcin, GATE 1 B3), so
`ua`'s half-empty column is not mistaken for a broken file.

    python3 report.py [csv]        # default: ../../data/a-dark-forest/localization.csv
"""
import sys, collections
import csv_parse as P


def main(path):
    lk = P.parse_file(path)
    recs = lk.records
    print(f"# A Dark Forest — report ({path})\n")
    print(f"records:      {len(recs)}")
    print(f"unique keys:  {len(set(r.key for r in recs))}")
    dups = lk.duplicate_keys()
    print(f"duplicate keys: {len(dups)}" + (f"  → {list(dups)} (upstream bug; report)" if dups else ""))
    print(f"locales:      {lk.locales}  (source={P.SOURCE})")
    deprecated = [r for r in recs if r.is_deprecated]
    marked_empty = [r for r in recs if r.is_marked_empty]
    print(f"deprecated:   {len(deprecated)} rows (excluded from extraction by default)")
    print(f"marked [EMPTY]: {len(marked_empty)} rows (intentionally blank in all locales)")

    print("\n## Namespaces (string-type axis)")
    for ns, rs in sorted(lk.by_namespace().items(), key=lambda kv: -len(kv[1])):
        print(f"  {ns:<28} {len(rs)}")

    print("\n## Value shapes (records × locales)")
    shapes = collections.Counter()
    for r in recs:
        for loc in lk.locales:
            shapes[r.shape(loc)] += 1
    for s, c in shapes.most_common():
        print(f"  {s:<8} {c}")
    arr_keys = sorted({r.key for r in recs if r.shape(P.SOURCE) == P.ARRAY})
    print(f"  array-valued keys: {len(arr_keys)}")

    print("\n## Completeness per locale (honest: intentional vs untranslated)")
    print(f"  {'locale':<8} {'filled':>6} {'blank':>6} {'intentional':>12} {'untrans':>8} {'untrans(active)':>16}")
    n = len(recs)
    for loc in lk.locales:
        blank = sum(1 for r in recs if r.values[loc].strip() == '')
        intentional = sum(1 for r in recs if r.values[loc].strip() == '' and r.is_marked_empty)
        untrans = sum(1 for r in recs if r.is_untranslated(loc))
        active = sum(1 for r in recs if r.is_untranslated(loc) and not r.is_deprecated)
        filled = n - blank
        print(f"  {loc:<8} {filled:>6} {blank:>6} {intentional:>12} {untrans:>8} {active:>16}")
    print("\n  (untranslated = blank, source present, not marked [EMPTY];")
    print("   'active' also excludes [DEPRECATED] rows — the count that matters for 'is this locale done'.)")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../../data/a-dark-forest/localization.csv')
