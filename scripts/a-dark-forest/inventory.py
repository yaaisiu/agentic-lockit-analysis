#!/usr/bin/env python3
"""inventory.py — placeholder / construct inventory for A Dark Forest, with origin labels.

WHY: before you can validate or translate safely you must know EVERY moving part in the text
and where its meaning comes from (format vs project). This lists each construct class, a count,
and example locations, all via the shared labels registry — so the inventory and the validator
can never disagree about what a token is.

    python3 inventory.py [csv]
"""
import sys, collections
import csv_parse as P
import labels as L


def main(path):
    lk = P.parse_file(path)
    print(f"# Construct inventory — {path}\n")

    # placeholders / control tokens in locale text
    print("## Placeholder / control tokens (locale text)")
    counts = collections.Counter()
    ex = {}
    for r in lk.records:
        for loc in lk.locales:
            for cls, tok in L.scan_tokens(r.values[loc]):
                counts[(cls, tok)] += 1
                ex.setdefault((cls, tok), f"row {r.row} {r.key}/{loc}")
    for (cls, tok), c in counts.most_common():
        origin = next((o for name, pat, o, note in L.PLACEHOLDER_CLASSES if name == cls), '?')
        print(f"  {cls:<12} {tok!r:8} ×{c:<4} origin={origin:<7} e.g. {ex[(cls, tok)]}")

    # value shapes
    print("\n## Value shapes")
    shp = collections.Counter()
    for r in lk.records:
        for loc in lk.locales:
            shp[r.shape(loc)] += 1
    for s, c in shp.most_common():
        print(f"  {s:<8} ×{c:<5} origin={L.VALUE_SHAPES[s][0]}")

    # description tags
    print("\n## Description tags (context column)")
    tags = collections.Counter()
    for r in lk.records:
        for t in r.tags:
            tags[t] += 1
    for t, c in tags.most_common():
        kind, origin, note = L.label_desc_tag(t)
        flag = '  <<< UNKNOWN — classify' if origin == L.UNKNOWN else ''
        print(f"  [{t}] ×{c}  kind={kind} origin={origin}{flag}")

    # key-embedded constructs
    print("\n## Key-embedded constructs")
    kc = collections.Counter()
    kex = {}
    for r in lk.records:
        for kind, origin, note in L.label_key(r.key):
            kc[kind] += 1
            kex.setdefault(kind, r.key)
    for kind, c in kc.most_common():
        print(f"  {kind:<15} ×{c:<4} e.g. {kex[kind]}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '../../data/a-dark-forest/localization.csv')
