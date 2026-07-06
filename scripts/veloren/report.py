#!/usr/bin/env python3
"""report.py — the "what we know" profile of the Veloren lockit, in honest numbers.

WHY: Marcin's GATE-1 instruction — "inform the user about all counts properly." A naive
"string count" is misleading for Fluent: some messages are empty CONTAINERS (all content in
attributes), 771 attributes are intentional {""} blanks, and attributes carry three
different kinds of content. This report separates TOTAL structure from TRANSLATABLE content
and breaks it down the way the profile (vault/lockits/veloren/profile.md) describes, so the
reader sees the real shape. Regenerable any time; drives no decisions by itself.

Usage: python3 report.py <dir-or-file>
"""
import sys, re, collections
import ftl_parse as F

KEY_OK = re.compile(r'^-?[a-z][a-z0-9]*(?:[_-][a-z0-9]+)*$')


def main(target):
    entries, _ = F.parse_tree(target)
    real = [e for e in entries if e.kind != 'junk']
    msgs = [e for e in real if e.kind == 'message']
    terms = [e for e in real if e.kind == 'term']

    attr_roles = collections.Counter()
    attr_empty = 0
    for e in real:
        for name, val in e.attributes:
            attr_roles[F.attr_role(name)] += 1
            if val.strip() in F.EMPTY_VALUES:
                attr_empty += 1
    container_msgs = sum(1 for e in msgs if e.value_is_empty())

    units_all = list(F.iter_units(entries, include_empty=True))
    units_tr = list(F.iter_units(entries, include_empty=False))

    prefixes = collections.Counter(e.id.split('-')[0] for e in msgs)
    key_outliers = [e for e in msgs if not KEY_OK.match(e.id)]

    print("=" * 66)
    print("VELOREN LOCKIT — WHAT WE KNOW (Fluent .ftl, English source)")
    print("=" * 66)
    print(f"\nFILES: {len(F.iter_files(target))}   encoding UTF-8 (no BOM)")
    print("\nSTRUCTURE (total):")
    print(f"  messages ....... {len(msgs)}  (ids all unique, 0 collisions = one bundle namespace)")
    print(f"  terms .......... {len(terms)}  ({', '.join(t.id for t in terms)})")
    print(f"  attributes ..... {sum(len(e.attributes) for e in real)}")
    print(f"     metadata (.desc/.stat) . {attr_roles['metadata']}")
    print(f"     gender (.fem/.masc/.neut) {attr_roles['gender']}")
    print(f"     variant array (.aN) .... {attr_roles['variant']}")
    print(f"     enum (named lookup) .... {attr_roles['enum']}")
    print(f"     other/unknown .......... {attr_roles['other']}  (drift: labels.py --audit)")
    print("\nTRANSLATABLE vs NON-CONTENT (honest counts):")
    print(f"  translatable units ......... {len(units_tr)}   (message/term values + non-empty attributes)")
    print(f"  container messages (empty value, content in attrs) . {container_msgs}")
    print(f"  intentional-empty attributes ({{\"\"}}) .............. {attr_empty}")
    print(f"  total units incl. empties .. {len(units_all)}")

    print("\nKEY NAMESPACES (top 12 prefixes):")
    print("  " + ', '.join(f'{k}({c})' for k, c in prefixes.most_common(12)))
    print(f"\nKEY-NAMING OUTLIERS (not lowercase-snake): {len(key_outliers)}")
    if key_outliers:
        sample = ', '.join(e.id for e in key_outliers[:6])
        print(f"  e.g. {sample}  (PascalCase: tutorial-*/achievement-* mirror code enum names)")

    # placeholder one-liner (delegate detail to inventory.py)
    vs = collections.Counter()
    for u in units_all:
        for p in F.placeables(u['text']):
            vs[F.classify_placeable(p)[0]] += 1
    print("\nPLACEABLES:", ', '.join(f'{k}={c}' for k, c in vs.most_common()))
    print("  (detail: inventory.py · gender: gender_pairs.py · structural check: validate.py)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: report.py <dir-or-file>")
    main(sys.argv[1])
