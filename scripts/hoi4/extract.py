#!/usr/bin/env python3
"""extract.py — pull a subset of strings, optionally as clean translatable text.

WHY: downstream work (translation, review, length checks) needs to SELECT strings and, often, to
see the TRANSLATABLE TEXT with the non-translatable dialect stripped. GATE 1 fixed the
non-translatable set: §X/§!, £icon, @TAG, $VAR$/$VAR|fmt$, [scope.fn], \\n. `--clean` removes
exactly those (leaving surrounding words + spacing) so you see what a human actually translates.
The raw value is always available too (nothing is mutated in the source).

Selectors (combine freely): --file SUBSTR · --namespace NS · --tag TAG · --style dotted|underscore
Output: --clean (stripped text) | default raw. --limit N.

    python3 extract.py ../../data/hoi4/en --namespace germany --clean
    python3 extract.py ../../data/hoi4/en --style underscore --tag GER --limit 20
"""
import sys, re
import clausewitz_parse as P

# order matters: strip scope/var/icon (which may contain letters) before colour/flag/newline
_STRIP = [
    re.compile(r'\[[^\]]*\]'),      # [scope.fn]
    re.compile(r'\$[^$]*\$'),       # $VAR$ / $VAR|fmt$
    re.compile(r'£\w+'),            # £icon
    re.compile(r'@[A-Z]{3}'),       # @TAG flag
    re.compile(r'§[A-Za-z]'),       # colour open
    re.compile(r'§!'),              # colour close
    re.compile(r'\\n'),             # newline
    re.compile(r'\\t'),             # tab
]

def clean_text(v):
    """Return only the translatable text: strip every non-translatable construct, tidy spaces."""
    for pat in _STRIP:
        v = pat.sub(' ', v)
    return re.sub(r'\s+', ' ', v).strip()


def select(lk, file=None, namespace=None, tag=None, style=None):
    for e in lk.entries:
        if file and file not in e.source_file:
            continue
        if namespace and e.namespace != namespace:
            continue
        if tag and e.tag != tag:
            continue
        if style == 'dotted' and not e.is_dotted:
            continue
        if style == 'underscore' and e.is_dotted:
            continue
        yield e


def main(argv):
    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    args = [a for a in argv if not a.startswith('--')]
    path = args[0] if args else '../../data/hoi4/en'
    lk = P.load(path)
    clean = '--clean' in argv
    limit = int(opt('--limit', '0')) or None
    rows = list(select(lk, opt('--file'), opt('--namespace'), opt('--tag'), opt('--style')))
    shown = rows[:limit] if limit else rows
    for e in shown:
        text = clean_text(e.value) if clean else e.value
        print(f"{e.key}\t{text}")
    print(f"\n# {len(shown)}/{len(rows)} selected (of {len(lk.entries)} entries)", file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
