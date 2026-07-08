#!/usr/bin/env python3
"""labels.py — the documented LABELING REGISTRY for the A Dark Forest CSV lockit.

======================== WHY THIS EXISTS (Marcin's rule) ========================
Every construct our tools recognise is LABELED with two things:
  1. WHAT it is   (kind: column role, placeholder class, value shape, description tag, key part)
  2. Its ORIGIN — where its MEANING is defined:
        'format'   defined by the file format (CSV/JSON/Godot spec) → portable to ANY such file
        'project'  a convention THIS lockit layers on top            → specific to A Dark Forest
        'unknown'  NOT in this registry                              → FLAG for a human

The 'unknown' bucket is DRIFT DETECTION: when the lockit changes between deliveries (a new
description tag, a new placeholder style, a new column), it must SURFACE — not be silently
mis-handled. `--audit` lists everything unknown. This is the SINGLE SOURCE OF TRUTH: every
other script imports these labels, so one edit updates the whole toolkit, and this docstring
IS the documentation of the scheme.

Separating 'format' from 'project' keeps the library clean: format-origin knowledge (CSV
quoting, JSON arrays, {N} slots) is reusable on the NEXT tabular lockit and is a promote
candidate; project-origin knowledge (what [noun] means, the key namespaces) stays here.

    python3 labels.py                 # print the registry (the documentation)
    python3 labels.py --audit <csv>   # list every construct unknown to the registry
"""
import re, sys, collections

FORMAT, PROJECT, UNKNOWN = 'format', 'project', 'unknown'

# --- COLUMNS ---------------------------------------------------------------------
# The header layout. 'description' is context (project), the locales are data (format:
# a CSV column per locale is just tabular structure). A NEW column name → unknown (drift).
COLUMN_ROLES = {                       # exact header name -> (role, origin, note)
    'key':         ('identity',    PROJECT, 'record id, namespace:name (not unique — see dup check)'),
    'description': ('context',     PROJECT, 'translator/dev notes + tag DSL; NOT player-facing'),
    'en':          ('source',      FORMAT,  'source locale (English)'),
    'zh': ('translation', FORMAT, 'Chinese (Simplified)'),
    'fr': ('translation', FORMAT, 'French'),
    'pt': ('translation', FORMAT, 'Portuguese (BR)'),
    'pl': ('translation', FORMAT, 'Polish'),
    'ua': ('translation', FORMAT, 'Ukrainian (partially translated)'),
    'th': ('translation', FORMAT, 'Thai'),
    'es': ('translation', FORMAT, 'Spanish'),
}
def label_column(name):
    return COLUMN_ROLES.get(name, ('other', UNKNOWN, f'unrecognised column {name!r} — classify me'))

# --- DESCRIPTION TAGS ------------------------------------------------------------
# A closed 4-tag annotation DSL in the `description` column. Anything else in brackets there
# is drift. All project-origin (their MEANING is an A-Dark-Forest convention).
DESC_TAGS = {                          # tag -> (kind, origin, note)
    'EMPTY':      ('status', PROJECT, 'string intentionally blank in all locales'),
    'DEPRECATED': ('status', PROJECT, 'dead string; excluded from extraction by default'),
    'noun':       ('pos',    PROJECT, 'part-of-speech hint for translators'),
    'verb':       ('pos',    PROJECT, 'part-of-speech hint for translators'),
}
def label_desc_tag(tag):
    return DESC_TAGS.get(tag, ('other', UNKNOWN, f'unrecognised description tag [{tag}] — classify me'))

# --- VALUE SHAPES ----------------------------------------------------------------
VALUE_SHAPES = {                       # shape -> (origin, note)
    'scalar': (FORMAT, 'plain string cell'),
    'array':  (FORMAT, 'JSON-array literal (multi-value cell); elements individually translatable'),
    'empty':  (FORMAT, 'blank cell (intentional iff description [EMPTY], else untranslated)'),
}

# --- PLACEHOLDERS / CONTROL CODES (inside locale text) ---------------------------
# Each entry: name -> (regex, origin, note). label_token() classifies a matched token.
PLACEHOLDER_CLASSES = [
    ('format-slot', re.compile(r'\{\d+\}'),  FORMAT, 'Godot String.format positional slot {0}..{3}'),
    ('newline',     re.compile(r'\\n'),      FORMAT, 'literal escaped newline (backslash-n)'),
]
# tokens that LOOK structural but must NOT be flagged as unknown constructs:
#   a literal & ("Writing & Narrative") is plain text, not an entity — see the drift note.
BENIGN_AMP = re.compile(r'&(?![#a-zA-Z0-9]+;)')     # bare & not forming an entity

def scan_tokens(text):
    """Yield (class_or_None, token) for every recognised placeholder token in `text`."""
    for name, pat, origin, note in PLACEHOLDER_CLASSES:
        for m in pat.finditer(text):
            yield name, m.group(0)

# constructs that would signal a NEW/unknown control syntax if they appeared in locale text
# (we affirmatively looked for these at GATE 1 and found none — the audit re-checks every run):
DRIFT_PROBES = {
    'angle-tag':      re.compile(r'<[^>]+>'),
    'html-entity':    re.compile(r'&[#a-zA-Z0-9]+;'),
    'bbcode':         re.compile(r'\[/?[a-zA-Z][a-zA-Z0-9 =._-]*\]'),   # only on non-array cells
    'curly-nonnum':   re.compile(r'\{[^}0-9][^}]*\}'),
    'dollar-var':     re.compile(r'\$\{?[a-zA-Z_]'),
    'percent-spec':   re.compile(r'%[0-9]*[a-zA-Z]'),
    'at-var':         re.compile(r'@[a-zA-Z_]'),
    'other-escape':   re.compile(r'\\(?!n)[a-zA-Z]'),
}

# --- KEY-EMBEDDED CONSTRUCTS -----------------------------------------------------
KEY_CONSTRUCTS = [                     # (regex on full key, kind, origin, note)
    (re.compile(r'-(-?\d+)$'), 'variant-suffix', PROJECT, 'variant index -1/-2 (e.g. enemy option, setting)'),
    (re.compile(r'(?:^|_)X(?:_|$)'), 'template-slot', PROJECT, 'runtime numeric slot X in key (reborn_X_line_*)'),
]
def label_key(key):
    """Return list of (kind, origin, note) for special constructs found in a key (may be empty)."""
    out = []
    for pat, kind, origin, note in KEY_CONSTRUCTS:
        if pat.search(key):
            out.append((kind, origin, note))
    return out


# --- registry dump (documentation) ----------------------------------------------
def print_registry():
    print("LABELING REGISTRY — A Dark Forest CSV")
    print("origin: format = CSV/JSON/Godot spec (portable) · project = this lockit · unknown = FLAG\n")
    print("COLUMNS:")
    for n, (role, o, note) in COLUMN_ROLES.items():
        print(f"  {n:<12} role={role:<11} origin={o:<7} {note}")
    print("  <any other>  origin=unknown → FLAG")
    print("\nDESCRIPTION TAGS (closed set):")
    for t, (k, o, note) in DESC_TAGS.items():
        print(f"  [{t:<10}] kind={k:<7} origin={o:<7} {note}")
    print("  [<any other>] origin=unknown → FLAG")
    print("\nVALUE SHAPES:")
    for s, (o, note) in VALUE_SHAPES.items():
        print(f"  {s:<7} origin={o:<7} {note}")
    print("\nPLACEHOLDER / CONTROL CLASSES (in locale text):")
    for name, pat, o, note in PLACEHOLDER_CLASSES:
        print(f"  {name:<12} /{pat.pattern}/  origin={o:<7} {note}")
    print("  any other structural token (see DRIFT_PROBES) → unknown → FLAG")
    print("\nKEY-EMBEDDED CONSTRUCTS:")
    for pat, kind, o, note in KEY_CONSTRUCTS:
        print(f"  /{pat.pattern}/  kind={kind:<14} origin={o:<7} {note}")


# --- drift audit -----------------------------------------------------------------
def audit(path):
    """Scan a lockit and report every construct 'unknown' to the registry (drift detector)."""
    import csv_parse as P
    lk = P.parse_file(path)
    unknown = collections.Counter()
    loc = {}

    # 1) columns
    for c in lk.header:
        if label_column(c)[1] == UNKNOWN:
            unknown[('column', c)] += 1; loc.setdefault(('column', c), 'header')

    # 2) description tags + 3) locale-text control tokens
    for r in lk.records:
        for tag in r.tags:
            if label_desc_tag(tag)[1] == UNKNOWN:
                unknown[('desc-tag', tag)] += 1
                loc.setdefault(('desc-tag', tag), f'row {r.row} {r.key}')
        for locale in lk.locales:
            v = r.values[locale]
            shape = P.value_shape(v)
            if shape == P.ARRAY:
                continue   # JSON arrays are a known shape; their [..] is not markup
            for name, pat in DRIFT_PROBES.items():
                # a bare '&' that is a literal word-joiner is benign, not an entity
                if name == 'html-entity' and not pat.search(v):
                    continue
                if pat.search(v):
                    unknown[('token', name)] += 1
                    loc.setdefault(('token', name), f'row {r.row} {r.key}/{locale}: {v[:40]!r}')

    total = sum(unknown.values())
    print(f"DRIFT AUDIT of {path}")
    print(f"unknown constructs: {total}\n")
    if total:
        for (cat, name), c in unknown.most_common():
            print(f"  {cat:<9} {name!r}  ×{c}   first at {loc.get((cat, name), '?')}")
    else:
        print("✓ every construct is labeled & known to the registry")
    return total


if __name__ == '__main__':
    if '--audit' in sys.argv:
        i = sys.argv.index('--audit')
        target = sys.argv[i + 1] if len(sys.argv) > i + 1 else '../../data/a-dark-forest/localization.csv'
        sys.exit(1 if audit(target) else 0)
    print_registry()
