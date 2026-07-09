#!/usr/bin/env python3
"""validate_placeholders.py — cross-locale construct preservation (PREPARED tool).

WHY: a translation must preserve the machine-readable tokens or the game breaks or mis-renders.
The invariant across locales (GATE 1 non-translatable set): the MULTISET of variables `$NAME$`,
scope functions `[scope.fn]`, icons `£name`, and flags `@TAG` should match the English source
per key; `\\n` and colour codes are advisory (colour/formatting can legitimately shift). We report
tokens the translation DROPPED or ADDED — real upstream defects (as the Wesnoth/A-Dark-Forest
cross-locale validators found real bugs). We only hold English here, so this is PREPARED: point it
at a source and a target locale (file or dir) and it runs.

    python3 validate_placeholders.py <en_dir> <other_dir>
    python3 validate_placeholders.py <en_dir> <other_dir> --advisory   # also report \n/colour drift
"""
import sys, re, collections
import clausewitz_parse as P

VAR   = re.compile(r'\$[^$]*\$')
SCOPE = re.compile(r'\[[^\]]*\]')
ICON  = re.compile(r'£\w+')
FLAG  = re.compile(r'@[A-Z]{3}')
NL    = re.compile(r'\\n')
COL   = re.compile(r'§[A-Za-z!]')


def signature(v, advisory=False):
    """Multiset of invariant tokens for one value. $VAR$ is normalised on NAME only (drop |fmt),
    so a colour-modifier change isn't a false positive; the referenced variable must still match."""
    sig = collections.Counter()
    for m in VAR.finditer(v):
        name = m.group(0).strip('$').split('|', 1)[0]
        sig['$' + name + '$'] += 1
    for pat, tag in ((SCOPE, ''), (ICON, ''), (FLAG, '')):
        for m in pat.finditer(v):
            sig[m.group(0)] += 1
    if advisory:
        sig['\\n×'] = len(NL.findall(v))
        sig['§×'] = len(COL.findall(v))
    return sig


def check(en_arg, other_arg, advisory=False):
    en = {e.key: e.value for e in P.load(en_arg).entries}
    other = {e.key: e.value for e in P.load(other_arg).entries}
    both = [k for k in other if k in en]
    defects = []
    for k in both:
        se, so = signature(en[k], advisory), signature(other[k], advisory)
        if se != so:
            dropped = se - so
            added = so - se
            defects.append((k, dropped, added))
    print(f"PLACEHOLDER CHECK  {other_arg} vs {en_arg}")
    print(f"keys in both: {len(both)}   defects (token multiset differs): {len(defects)}\n")
    for k, dropped, added in defects[:40]:
        parts = []
        if dropped:
            parts.append("DROPPED " + ' '.join(f'{t}×{c}' for t, c in dropped.items()))
        if added:
            parts.append("ADDED " + ' '.join(f'{t}×{c}' for t, c in added.items()))
        print(f"  {k}: {' | '.join(parts)}")
    return len(defects)


if __name__ == '__main__':
    pos = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(pos) < 2:
        print(__doc__); sys.exit(2)
    check(pos[0], pos[1], advisory='--advisory' in sys.argv)
