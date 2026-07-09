#!/usr/bin/env python3
"""keys.py — catalogue the KEY vocabularies (Marcin's GATE-1 request, T-H3).

WHY: HoI4 has TWO key styles (GATE 1), and the meaning lives in the key structure, so a translator
/ tool needs the vocabulary spelled out:
  * underscore keys  <TAG>_<...>_<SUFFIX>  — a leading 3-letter country tag + trailing grammatical/
    role suffixes (_DEF definite article, _desc, _OPTION_*). We catalogue the tag set and the
    suffix set so the closed-ish vocabulary is visible.
  * dotted event keys  <namespace>.<id>.<part>  — a namespace, a numeric event id, and a `part`.
    The part vocabulary is SEMI-OPEN (title/body/tooltip/options + open-ended NAMED conditional
    variants) — we classify each via labels.label_part and show the distribution by KIND.

This is a REPORT, not a validator; it makes the project-origin key conventions inspectable so they
can be documented and, where stable, promoted. Deterministic; no LLM.

    python3 keys.py ../../data/hoi4/en
    python3 keys.py ../../sources/hoi4        # full 206-file vocabulary
"""
import sys, re, collections
import clausewitz_parse as P
import labels as L


def catalogue(arg):
    lk = P.load(arg)
    tags = collections.Counter()
    suffixes = collections.Counter()
    namespaces = collections.Counter()
    part_kinds = collections.Counter()
    part_examples = collections.defaultdict(set)
    dotted = underscore = 0

    for e in lk.entries:
        if e.is_dotted:
            dotted += 1
            namespaces[e.namespace] += 1
            kind, _note = L.label_part(e.part)
            part_kinds[kind] += 1
            if len(part_examples[kind]) < 6:
                part_examples[kind].add(e.part)
        else:
            underscore += 1
            if e.tag:
                tags[e.tag] += 1
            # trailing UPPER or _lower suffix token (grammatical/role marker)
            m = re.search(r'_([A-Za-z][A-Za-z0-9]*)$', e.key)
            if m:
                suffixes[m.group(1)] += 1

    print(f"KEY CATALOGUE of {arg}   ({len(lk.entries)} entries)\n")
    print(f"key styles: underscore={underscore}  dotted-event={dotted}\n")
    print(f"country tags (leading [A-Z]{{3}}_): {len(tags)} distinct; top 15:")
    print(f"  {dict(tags.most_common(15))}\n")
    print(f"underscore trailing suffixes: {len(suffixes)} distinct; top 20:")
    for suf, c in suffixes.most_common(20):
        print(f"  _{suf:<16} ×{c}")
    print(f"\nevent namespaces: {len(namespaces)} distinct; top 15:")
    print(f"  {dict(namespaces.most_common(15))}\n")
    print(f"event part KINDS (via labels.label_part — semi-open vocab):")
    for kind, c in part_kinds.most_common():
        print(f"  {kind:<14} ×{c:<6} e.g. {sorted(part_examples[kind])[:5]}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    catalogue(args[0] if args else '../../data/hoi4/en')
