#!/usr/bin/env python3
"""inventory.py — placeholder / construct inventory for the HoI4 lockit.

WHY: "what constructs are in here, how many, and where?" is the first question about any lockit.
This counts every recognised inline construct (from the labels.py registry — single source of
truth), plus the $VAR|fmt$ format-modifier breakdown and the [scope.fn] sub-form breakdown that
GATE 1 called out. Deterministic; import-and-count, no LLM. Works on a file or the whole dir.

    python3 inventory.py ../../data/hoi4/en                 # the slice
    python3 inventory.py ../../sources/hoi4 --samples 3     # all 206, 3 example keys each
"""
import sys, re, collections
import clausewitz_parse as P
import labels as L


def inventory(arg, samples=2):
    lk = P.load(arg)
    counts = collections.Counter()        # occurrences
    entries_with = collections.Counter()  # entries containing >=1
    ex = collections.defaultdict(list)
    var_fmts = collections.Counter()
    scope_forms = collections.Counter()

    for e in lk.entries:
        seen = set()
        for name, tok in L.scan_tokens(e.value):
            counts[name] += 1; seen.add(name)
            if len(ex[name]) < samples:
                ex[name].append(f'{e.key} :: {tok}')
        for name in seen:
            entries_with[name] += 1
        # $VAR|fmt$ modifier census
        for m in re.finditer(r'\$([^$]*)\$', e.value):
            _n, fmt = L.split_var(m.group(0))
            if fmt is not None:
                var_fmts[fmt] += 1
        # [scope.fn] sub-form census
        for m in re.finditer(r'\[([^\]]*)\]', e.value):
            c = L.classify_scope(m.group(1))
            form = ('optional-' if c['optional'] else '') + ('bare' if c['bare'] else 'scoped')
            scope_forms[form] += 1
            if c['fmt'] is not None:
                scope_forms['+|fmt'] += 1

    print(f"INVENTORY of {arg}   ({len(lk.entries)} entries, {len(lk.files)} files)\n")
    print(f"{'construct':<13} {'occurs':>8} {'entries':>8}   examples")
    for name, _pat, _o, _note in L.INLINE:
        exs = '   |   '.join(ex[name][:samples])
        print(f"{name:<13} {counts[name]:>8} {entries_with[name]:>8}   {exs}")
    print(f"\n$VAR|fmt$ modifiers (top 15): {dict(var_fmts.most_common(15))}")
    print(f"[scope.fn] sub-forms: {dict(scope_forms)}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    s = 2
    if '--samples' in sys.argv:
        s = int(sys.argv[sys.argv.index('--samples') + 1])
    inventory(args[0] if args else '../../data/hoi4/en', s)
