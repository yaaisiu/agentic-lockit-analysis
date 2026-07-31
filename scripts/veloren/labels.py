#!/usr/bin/env python3
"""labels.py — the documented LABELING REGISTRY for the Veloren Fluent lockit.

======================== WHY THIS EXISTS (Marcin's rule) ========================
Every construct our tools recognise must be LABELED with two things:
  1. WHAT it is           (role/kind: metadata, gender, variant, var, selector, function…)
  2. Its ORIGIN           — where its MEANING is defined:
        'fluent'   defined by the Fluent format spec        → portable to ANY .ftl lockit
        'project'  a Veloren convention layered on Fluent   → specific to THIS lockit
        'unknown'  NOT in this registry                     → FLAG for a human to classify

The point of the 'unknown' bucket is DRIFT DETECTION: when the lockit changes — a new
attribute role, a new custom function, a new placeable shape — our tools must not silently
mis-handle it. Instead it surfaces as 'unknown' and the audit reports it, so we notice and
extend the registry deliberately. This file is the SINGLE SOURCE OF TRUTH; every other
script imports it. Keeping labels here (not scattered) means one edit updates the whole
toolkit — and this docstring IS the human documentation of the scheme.

Separating 'fluent' vs 'project' matters because: fluent-origin knowledge is reusable on the
NEXT .ftl lockit (promote to library); project-origin knowledge is Veloren-specific (stays in
this toolkit). Telling them apart keeps the library clean.

Run the drift audit any time:
    python3 labels.py --audit <dir>      # lists every 'unknown' construct + where it is
    python3 labels.py                    # prints the registry (the documentation)
"""
import re, sys, collections

FLUENT, PROJECT, UNKNOWN = 'fluent', 'project', 'unknown'

# --- ATTRIBUTES ------------------------------------------------------------------
# Attributes are a Fluent MECHANISM, but the MEANING of a given attribute name is a
# Veloren convention → origin 'project'. Unrecognised names → 'unknown' (drift).
ATTRIBUTE_ROLES = {          # exact name -> (role, origin, note)
    'desc': ('metadata', PROJECT, 'UI description text'),
    'stat': ('metadata', PROJECT, 'formatted stat line (often a selector)'),
    'fem':  ('gender',   PROJECT, 'feminine grammatical form'),
    'masc': ('gender',   PROJECT, 'masculine grammatical form'),
    'neut': ('gender',   PROJECT, 'neuter grammatical form'),
}
ATTRIBUTE_PATTERNS = [       # (regex, (role, origin, note)) — checked after exact names
    (re.compile(r'^a\d+$'), ('variant', PROJECT, 'random-pick variant array (.a0,.a1,…)')),
]
# 'enum' role: a message is a lookup TABLE whose attributes are keyed by a domain enum
# (the engine picks one by a runtime key). Distinct from .aN (random-pick by index).
# Catalogued by FAMILY so the registry documents the vocabulary; a NEW key not listed here
# re-surfaces as 'unknown' → we notice the vocabulary changed (Marcin's drift rule).
ENUM_ATTR_FAMILIES = {       # discovered by the drift audit at GATE 2 (session 002)
    'buff-kind':   ['burning', 'bleeding', 'curse', 'crippled', 'frozen', 'mysterious'],
    'weapon-kind': ['sword', 'axe', 'hammer', 'bow', 'staff', 'sceptre'],
    'hire-period': ['day', 'week', 'unknown'],
    'time-unit':   ['days', 'hours', 'minutes', 'seconds'],
}
ENUM_ATTRS = {k: fam for fam, keys in ENUM_ATTR_FAMILIES.items() for k in keys}

def label_attr(name):
    """-> (role, origin, note). Unknown attribute names are surfaced, not guessed."""
    if name in ATTRIBUTE_ROLES:
        return ATTRIBUTE_ROLES[name]
    for pat, lab in ATTRIBUTE_PATTERNS:
        if pat.match(name):
            return lab
    if name in ENUM_ATTRS:
        return ('enum', PROJECT, f'named enum key (family: {ENUM_ATTRS[name]})')
    return ('other', UNKNOWN, f'unrecognised attribute name .{name} — classify me')

# --- PLACEABLES ------------------------------------------------------------------
# Placeable KINDS are pure Fluent syntax → origin 'fluent'. (Functions are special-cased
# below: the syntax is Fluent, but a specific function may be a project extension.)
PLACEABLE_ORIGIN = {
    'var':      (FLUENT, 'runtime variable { $x }'),
    'selector': (FLUENT, 'inline plural/conditional { $x -> … }'),
    'term-ref': (FLUENT, 'reference to a term { -t }'),
    'msg-ref':  (FLUENT, 'reference to a message { m[.attr] }'),
    'literal':  (FLUENT, 'string literal { "…" } ({""}=intentional blank)'),
}

# --- FUNCTIONS -------------------------------------------------------------------
FUNCTIONS = {                # name -> (origin, note)
    'NUMBER':   (FLUENT,  'Fluent built-in number formatter'),
    'DATETIME': (FLUENT,  'Fluent built-in date/time formatter'),
    'TAIL':     (PROJECT, 'Veloren custom: strip a noun\'s leading article'),
}
def label_function(name):
    return FUNCTIONS.get(name, (UNKNOWN, f'unrecognised function {name}() — classify me'))

# --- ENGINE-SUPPLIED VARIABLES ---------------------------------------------------
# Variables the Veloren engine provides for GRAMMATICAL AGREEMENT that a translation may
# legitimately use even when the English source does not (English rarely inflects). Marked
# project-origin. The cross-locale checker must NOT flag these as "invented" — doing so is
# the classic over-constraint the convention warns about (a locale needs an extra particle).
# Discovered at the GATE-2 all-locale sweep (session 002): $victim_gender / $attacker_gender /
# $user_gender / $player_gender / $gender, and the general `*_gender` pattern.
ENGINE_VARS = {'victim_gender', 'attacker_gender', 'user_gender', 'player_gender', 'gender'}
def is_engine_var(name):
    return name in ENGINE_VARS or name.endswith('_gender')

# --- SELECTOR VARIANT KEYS -------------------------------------------------------
CLDR = {'zero', 'one', 'two', 'few', 'many', 'other'}
def label_variant_key(key):
    if key in CLDR:
        return (FLUENT, 'CLDR plural category')
    if key.lstrip('-').isdigit():
        return (FLUENT, 'explicit number match')
    return (UNKNOWN, f'unrecognised selector variant key [{key}] — classify me')

def label_placeable(p, classify):
    """classify = ftl_parse.classify_placeable. -> (kind, origin, detail, note)."""
    kind, detail = classify(p)
    if kind == 'function':
        o, note = label_function(detail); return (kind, o, detail, note)
    o, note = PLACEABLE_ORIGIN.get(kind, (UNKNOWN, f'unrecognised placeable: {p[:40]}'))
    return (kind, o, detail, note)


# --- SELECTOR SYNTAX PIECES ------------------------------------------------------
# A selector is not one token: it is syntax wrapped around translatable prose. When a span is
# used as a MASK it must cover only the syntax (see ftl_parse.placeable_tokens), so the head,
# each variant key and the closer are labeled here as constructs in their own right. All three
# are pure Fluent grammar → origin 'fluent'; the VARIANT KEY defers to label_variant_key, so an
# unrecognised key still surfaces as drift instead of being waved through as "selector syntax".
SELECTOR_PIECES = {
    'selector-head':  'selector head { $x -> — the variable being switched on',
    'selector-key':   'selector variant key [k] / *[k] (starred = default)',
    'selector-close': 'selector closer }',
}
def label_selector_piece(syntax, payload):
    """-> (kind, origin, detail, note). kind is always 'selector'."""
    if syntax == 'selector-key':
        o, note = label_variant_key(payload)
        return ('selector', o, payload, note)
    if syntax not in SELECTOR_PIECES:
        return ('selector', UNKNOWN, '', f'unrecognised selector piece {syntax!r} — classify me')
    return ('selector', FLUENT, payload or '', SELECTOR_PIECES[syntax])


# --- registry dump (documentation) ----------------------------------------------
def print_registry():
    print("LABELING REGISTRY (origin: fluent = format spec · project = Veloren · unknown = flag)\n")
    print("ATTRIBUTE ROLES:")
    for n, (role, orig, note) in ATTRIBUTE_ROLES.items():
        print(f"  .{n:<6} role={role:<9} origin={orig:<8} {note}")
    for pat, (role, orig, note) in ATTRIBUTE_PATTERNS:
        print(f"  /{pat.pattern}/  role={role:<9} origin={orig:<8} {note}")
    print("  enum role (origin=project) — named lookup keys, by family:")
    for fam, keys in ENUM_ATTR_FAMILIES.items():
        print(f"    {fam:<12} {', '.join('.' + k for k in keys)}")
    print("  <any other>  role=other   origin=unknown  → FLAG")
    print("\nPLACEABLE KINDS:")
    for k, (orig, note) in PLACEABLE_ORIGIN.items():
        print(f"  {k:<9} origin={orig:<8} {note}")
    print("\nSELECTOR SYNTAX PIECES (a selector masks as 3+ tokens, never as one construct):")
    for k, note in SELECTOR_PIECES.items():
        print(f"  {k:<15} origin=fluent   {note}")
    print("\nFUNCTIONS:")
    for n, (orig, note) in FUNCTIONS.items():
        print(f"  {n:<9} origin={orig:<8} {note}")
    print("  <any other>  origin=unknown  → FLAG")
    print("\nSELECTOR VARIANT KEYS: CLDR {zero,one,two,few,many,other} + integers = fluent; else unknown → FLAG")


# --- drift audit -----------------------------------------------------------------
def audit(target):
    """Scan a lockit and report every construct that is 'unknown' to the registry."""
    import ftl_parse as F              # lazy import to avoid a cycle (ftl_parse imports us)
    entries, _ = F.parse_tree(target)
    unknown_attrs = collections.Counter()
    unknown_funcs = collections.Counter()
    unknown_keys = collections.Counter()
    unknown_placeables = collections.Counter()
    loc = {}
    for e in entries:
        if e.kind == 'junk':
            continue
        for name, _ in e.attributes:
            role, orig, _ = label_attr(name)
            if orig == UNKNOWN:
                unknown_attrs[name] += 1; loc.setdefault(('attr', name), f"{e.file}:{e.line}")
    for u in F.iter_units(entries, include_empty=True):
        # NOTE: placeables() yields (start, end, inner) — unpack. If you leave `p` as the
        # tuple, `p[:40]` below still "works" (a tuple slice is hashable, so the Counter
        # accepts it) and this audit silently starts reporting (12, 20, '$x') instead of the
        # construct. Every other call site would raise; this one would not. Pinned by a test.
        for _s, _e, p in F.placeables(u['text']):
            kind, orig, detail, _ = label_placeable(p, F.classify_placeable)
            ctx = f"{u['file']}:{u['line']} {u['id']}"
            if kind == 'function' and orig == UNKNOWN:
                unknown_funcs[detail] += 1; loc.setdefault(('fn', detail), ctx)
            elif orig == UNKNOWN:
                unknown_placeables[p[:40]] += 1; loc.setdefault(('pl', p[:40]), ctx)
            if kind == 'selector':
                for key, _ in F.selector_variant_keys(p):
                    if label_variant_key(key)[0] == UNKNOWN:
                        unknown_keys[key] += 1; loc.setdefault(('key', key), ctx)
    total = sum(map(sum, [unknown_attrs.values(), unknown_funcs.values(),
                          unknown_keys.values(), unknown_placeables.values()]))
    print(f"DRIFT AUDIT of {target}")
    print(f"unknown constructs: {total}\n")
    for title, ctr, tag in [("attributes", unknown_attrs, 'attr'),
                            ("functions", unknown_funcs, 'fn'),
                            ("selector variant keys", unknown_keys, 'key'),
                            ("placeables", unknown_placeables, 'pl')]:
        if ctr:
            print(f"UNKNOWN {title}:")
            for name, c in ctr.most_common():
                print(f"  {name!r}  ×{c}   first at {loc.get((tag, name), '?')}")
    if total == 0:
        print("✓ every construct is labeled & known to the registry")
    return total


if __name__ == '__main__':
    if '--audit' in sys.argv:
        i = sys.argv.index('--audit')
        sys.exit(1 if audit(sys.argv[i + 1]) else 0)
    print_registry()
