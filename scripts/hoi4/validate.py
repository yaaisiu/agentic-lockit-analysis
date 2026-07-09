#!/usr/bin/env python3
"""validate.py — structural validation + cross-locale length reference for the HoI4 lockit.

WHY: profiling must "report, don't fix". This surfaces structural facts a human should see:
  * parse warnings (malformed / apparently multi-line lines) — engine truncates from the first
    bad line, so these matter; we log-and-skip and list them.
  * duplicate keys (within/across files) — override candidates (replace-folder / load order).
  * colour spans that don't balance in one string (§X without §!, or vice-versa) — the NOTED
    tail; often a legit cross-string span (colour closed after a $VAR$), sometimes a typo.
  * escaped-quote occurrences (\") — the rare tail; located so a human can eyeball them.

--length-ref (Marcin's E1 idea): HoI4 has NO char-limit column, so there is no hard limit to
check. Instead, as a SOFT REFERENCE, compare a translation's TRANSLATABLE-text length to the
English source's, per key, and flag large ratios (default > 1.6× or < 0.5×). It's informational
(long/short translations often overflow fixed UI), NOT a pass/fail. This is a PREPARED tool: it
needs a second locale file/dir; we only hold English here, so it runs when you point it at one.

    python3 validate.py ../../data/hoi4/en                      # structural checks
    python3 validate.py ../../sources/hoi4 --dups               # dup keys across all 206
    python3 validate.py --length-ref <en_dir> <other_dir> [--ratio 1.6]
"""
import sys, re, collections
import clausewitz_parse as P
import labels as L
from extract import clean_text


def structural(arg, show_dups=False):
    lk = P.load(arg)
    print(f"VALIDATE {arg}   ({len(lk.entries)} entries, {len(lk.files)} files)\n")

    print(f"parse warnings (malformed/multiline): {len(lk.warnings)}")
    for f, ln, kind, txt in lk.warnings[:10]:
        print(f"  {f}:{ln} [{kind}] {txt!r}")

    dups = lk.duplicate_keys()
    print(f"\nduplicate keys: {len(dups)}")
    if show_dups:
        for k, es in list(dups.items())[:40]:
            print(f"  {k}  in {[f'{e.source_file.split('/')[-1]}:{e.line}' for e in es]}")

    unbalanced = [(e) for e in lk.entries if L.color_unbalanced(e.value)]
    print(f"\ncolour spans unbalanced within one string (NOTED): {len(unbalanced)}")
    for e in unbalanced[:8]:
        o = len(re.findall(r'§[A-Za-z]', e.value)); c = e.value.count('§!')
        print(f"  {e.source_file.split('/')[-1]}:{e.line} {e.key}  opens={o} closes={c}")

    escq = [e for e in lk.entries if L.NOTED_PROBES['escaped-quote'].search(e.value)]
    print(f"\nescaped-quote \\\" occurrences (NOTED tail): {len(escq)}")
    for e in escq[:8]:
        print(f"  {e.source_file.split('/')[-1]}:{e.line} {e.key}")

    return len(lk.warnings)


def length_ref(en_arg, other_arg, ratio=1.6):
    """Compare translatable-text length of each key: other vs English source. Soft reference."""
    en = {e.key: e for e in P.load(en_arg).entries}
    other = {e.key: e for e in P.load(other_arg).entries}
    lo = 1.0 / ratio
    both = [k for k in other if k in en]
    flagged = []
    for k in both:
        s = len(clean_text(en[k].value)); t = len(clean_text(other[k].value))
        if s == 0:
            continue
        r = t / s
        if r >= ratio or r <= lo:
            flagged.append((r, k, s, t))
    flagged.sort(reverse=True)
    print(f"LENGTH REFERENCE  {other_arg} vs {en_arg}")
    print(f"keys in both: {len(both)}   flagged (ratio ≥{ratio} or ≤{lo:.2f}): {len(flagged)}")
    print("(soft reference only — HoI4 has no char limit; long/short may overflow fixed UI)\n")
    for r, k, s, t in flagged[:30]:
        print(f"  {r:5.2f}×  {k}  (src {s} → {t} chars)")
    return len(flagged)


if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--length-ref' in argv:
        rest = [a for a in argv if a != '--length-ref' and not a.startswith('--ratio')]
        ratio = float(argv[argv.index('--ratio') + 1]) if '--ratio' in argv else 1.6
        pos = [a for a in rest if not a.startswith('--')]
        length_ref(pos[0], pos[1], ratio)
    else:
        pos = [a for a in argv if not a.startswith('--')]
        structural(pos[0] if pos else '../../data/hoi4/en', show_dups='--dups' in argv)
