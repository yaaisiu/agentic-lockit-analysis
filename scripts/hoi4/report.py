#!/usr/bin/env python3
"""report.py — the one-screen "what we know" summary for the HoI4 lockit.

WHY: a single command that profiles a file-or-dir into the headline facts from profile.md —
scale (files/entries), the two key styles, the version-integer distribution, the construct
census, and the drift status (tier-1 unknown must be 0). It composes the other modules so the
numbers always agree with them. Deterministic; safe to run on the slice or all 206.

    python3 report.py ../../data/hoi4/en
    python3 report.py ../../sources/hoi4      # full corpus
"""
import sys, collections
import clausewitz_parse as P
import labels as L


def report(arg):
    lk = P.load(arg)
    n = len(lk.entries)
    dotted = sum(1 for e in lk.entries if e.is_dotted)
    ver = collections.Counter(e.version for e in lk.entries if e.version is not None)
    con = collections.Counter()
    for e in lk.entries:
        for name, _tok in L.scan_tokens(e.value):
            con[name] += 1
    dups = lk.duplicate_keys()

    print(f"╔═ HoI4 lockit report ═ {arg}")
    print(f"║ format     Clausewitz pseudo-YAML (line-regex; NOT PyYAML), UTF-8-BOM")
    print(f"║ files      {len(lk.files)}   langs {lk.langs}")
    print(f"║ entries    {n}   unique keys {len(lk.by_key())}   duplicate keys {len(dups)}")
    print(f"║ key styles underscore {n - dotted}  ·  dotted-event {dotted}")
    print(f"║ version :N {dict(sorted(ver.items()))}  (optional revision counter — not identity)")
    print(f"║ empty      {sum(1 for e in lk.entries if e.is_empty)} genuinely empty values")
    print(f"║ parse      {len(lk.warnings)} malformed/multiline warnings")
    print(f"║ constructs " + "  ".join(f"{k}={con[k]}" for k, *_ in L.INLINE))
    print(f"╚═ drift     run `labels.py --audit {arg}` (tier-1 unknown must be 0)")
    if dups:
        print(f"\n⚠ {len(dups)} duplicate keys (override candidates) — see validate.py --dups")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    report(args[0] if args else '../../data/hoi4/en')
