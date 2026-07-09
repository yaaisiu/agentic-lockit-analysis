#!/usr/bin/env python3
"""labels.py — the documented LABELING REGISTRY for the HoI4 Clausewitz lockit.

======================== WHY THIS EXISTS (Marcin's rule) ========================
Every construct our tools recognise is LABELED with two things:
  1. WHAT it is   (kind: colour code, icon, flag, variable, scope function, escape, key part)
  2. Its ORIGIN — where its MEANING is defined:
        'format'   the Clausewitz old-style dialect (portable to EU4/Stellaris/other HoI4 files)
        'project'  a convention THIS dataset layers on top (what an event `part` letter means)
        'unknown'  NOT in this registry → FLAG for a human

The 'unknown' bucket is DRIFT DETECTION. The GATE-0 slice does NOT exercise the whole construct
space — e.g. it only shows colour letters Y R G H, but the full 206 files also use L T W O g b B.
So `--audit` is how we catalogue the tail and CATCH anything new (a colour letter outside the
known set, an escape other than \\n, a stray CK3/Vic3-style `#fmt` or `@icon!` that would mean the
dialect shifted). Never silently fold the unrecognised into "other".

Separating 'format' from 'project' keeps the library clean: the dialect (`§`/`£`/`@`/`$VAR|fmt$`/
`[scope.fn]`) is reusable on the next Paradox file (promote candidate); the event `part` meanings
stay here. This module is the SINGLE SOURCE OF TRUTH — one edit updates the whole toolkit.

    python3 labels.py                      # print the registry (the documentation)
    python3 labels.py --audit <file|dir>   # list every construct unknown to the registry
"""
import re, sys, collections

FORMAT, PROJECT, UNKNOWN = 'format', 'project', 'unknown'

# --- COLOUR LETTERS --------------------------------------------------------------
# §X opens a colour; §! closes. KNOWN = the set verified across all 206 files (GATE 1 drift
# preview). A §-letter outside this set is DRIFT → audit flags it.
KNOWN_COLOR_LETTERS = set('YGRHLTWOgbB')      # slice: Y R G H; +full-206: L T W O g b B

# --- INLINE CONSTRUCTS (inside a value) ------------------------------------------
# name -> (regex, origin, note). These are the recognised tokens; scan_tokens() yields them.
INLINE = [
    ('colour-open', re.compile(r'§([A-Za-z])'), FORMAT, 'colour open §+letter (letter in KNOWN set)'),
    ('colour-close', re.compile(r'§!'),          FORMAT, 'colour close §!'),
    ('icon',        re.compile(r'£(\w+)'),       FORMAT, 'text icon £name (whitespace-terminated, NO closing £)'),
    ('flag',        re.compile(r'@([A-Z]{3})'),  FORMAT, 'flag icon @TAG (3-letter country tag)'),
    ('variable',    re.compile(r'\$([^$]*)\$'),  FORMAT, 'variable $NAME$ or $NAME|fmt$ (fmt = colour and/or number format)'),
    ('scope-fn',    re.compile(r'\[([^\]]*)\]'), FORMAT, 'engine data function [scope.fn] (dotted/bare/?optional/|fmt)'),
    ('newline',     re.compile(r'\\n'),          FORMAT, 'literal escaped newline'),
]

def scan_tokens(text):
    """Yield (name, token) for every recognised inline construct in `text`."""
    for name, pat, _o, _n in INLINE:
        for m in pat.finditer(text):
            yield name, m.group(0)

def split_var(tok):
    """'$VALUE|+=%1$' -> ('VALUE', '+=%1'); '$EFF$' -> ('EFF', None). fmt = colour and/or number."""
    inner = tok.strip('$')
    if '|' in inner:
        name, fmt = inner.split('|', 1)
        return (name, fmt)
    return (inner, None)

def classify_scope(inner):
    """Classify a [..] body: optional? scoped-vs-bare? has |fmt? -> dict of flags."""
    optional = inner.startswith('?')
    body = inner[1:] if optional else inner
    fmt = None
    if '|' in body:
        body, fmt = body.split('|', 1)
    return {'optional': optional, 'scoped': '.' in body, 'bare': '.' not in body, 'fmt': fmt}

# --- ESCAPES ---------------------------------------------------------------------
# Known backslash escapes (verified across all 206): \n (newline) and \t (tab) only, plus the
# structural \\ and \". Anything else is DRIFT.
KNOWN_ESCAPES = set('nt\\"')

# --- DRIFT PROBES (tier 1: any hit = an UNKNOWN construct → audit FAILS) -----------
# These signal a genuinely NEW/foreign syntax. They must be 0 on HoI4 old-style.
DRIFT_PROBES = {
    'other-escape':   re.compile(r'\\(?![nt\\"])[A-Za-z]'),  # escape other than \n \t \\ \"
    'newstyle-fmt':   re.compile(r'#\w+\b[^#]*#!'),          # genuine CK3/Vic3 #key…#! span → wrong dialect
    'newstyle-icon':  re.compile(r'@\w+!'),                  # CK3/Vic3 @icon! → drift
    'curly-brace':    re.compile(r'\{[^}]*\}'),              # {..} not used by HoI4 loc → drift
}
# NOTE: a bare `#word` with no closing `#!` (e.g. "#TODO_NORDIC") is a dev marker in the text,
# NOT CK3 formatting — deliberately NOT flagged (the probe requires the closing `#!`).

# --- NOTED PROBES (tier 2: expected tail — REPORTED but NOT counted as unknown) ----
# Real HoI4 patterns worth surfacing that are not drift: the escaped-quote tail (~21/206), and
# colour spans that don't balance inside one string (colour opened in a key and closed after a
# $VAR$ interpolation — a known HoI4 concatenation pattern, not necessarily a defect).
NOTED_PROBES = {
    'escaped-quote':  re.compile(r'\\"'),                    # literal \" — rare; validate.py locates each
}

def color_letter_issues(text):
    """Yield ('unknown-color', '§X') for letters outside KNOWN. Drift-tier."""
    for m in re.finditer(r'§([A-Za-z])', text):
        if m.group(1) not in KNOWN_COLOR_LETTERS:
            yield 'unknown-color', '§' + m.group(1)

def color_unbalanced(text):
    """True if §X openers != §! closers in this string (a NOTED cross-string colour span)."""
    return len(re.findall(r'§[A-Za-z]', text)) != text.count('§!')

# --- KEY PARTS (project) ---------------------------------------------------------
# Event dotted keys are namespace.id.part. The `part` vocabulary is a SEMI-OPEN set: a small
# closed core (title/body/tooltip), single-letter options a..z (Mexico.19 goes to r!), numbered
# variants, and compound forms (option.tt, desc.<opt>) — PLUS open-ended NAMED conditional
# variants writers invent (`desc.baltics`, `keep_leader`, `tripartite_rejection`). Named variants
# are EXPECTED (origin project), not drift — so label_part classifies into a KIND and never
# returns 'unknown'. keys.py catalogues the full distribution (Marcin's T-H3).
_CORE = {'t': 'title', 'title': 'title', 'd': 'body', 'desc': 'body', 'tt': 'tooltip',
         'do': 'option', 'opt': 'option', 'warning': 'body'}
def label_part(part):
    """(kind, note) for an event part. Never 'unknown' — parts are a semi-open project vocab."""
    if not part:
        return ('none', 'no part')
    head = part.split('.', 1)[0]                  # compound: 'desc.a' -> 'desc'; 'a.tt' -> 'a'
    base = re.sub(r'\d+$', '', head)              # numbered variant: 'desc2'->'desc', 't.4'->'t'
    if '.tt' in part or part.endswith('.tt') or base == 'tt':
        return ('tooltip', 'option/entry tooltip')
    if base in _CORE:
        return (_CORE[base], f'core event part .{base}')
    if re.fullmatch(r'[a-z]', base):
        return ('option', f'event option .{base}')
    if re.fullmatch(r'[a-z]\d*', head) or re.fullmatch(r'\d+', head):
        return ('option', 'numbered option/variant')
    return ('named-variant', 'named conditional/semantic variant text (open project vocab)')


# --- registry dump ---------------------------------------------------------------
def print_registry():
    print("LABELING REGISTRY — HoI4 Clausewitz (old-style dialect)")
    print("origin: format = Clausewitz dialect (portable) · project = this dataset · unknown = FLAG\n")
    print(f"COLOUR LETTERS (known set): {''.join(sorted(KNOWN_COLOR_LETTERS))}")
    print("  §<letter> opens, §! closes; a letter outside the set → unknown → FLAG\n")
    print("INLINE CONSTRUCTS (origin format):")
    for name, pat, o, note in INLINE:
        print(f"  {name:<13} /{pat.pattern}/  {note}")
    print("\n$VAR|fmt$: fmt is a FORMAT SPEC — colour letter AND/OR number format (%, .0, +=, precision)")
    print("[scope.fn]: sub-forms — dotted [Root.GetName] · nested [From.From.Get] · bare [GetDate]"
          " · optional [?scope.Fn] · |fmt [scope.fn|+=%]")
    print("\nEVENT KEY PARTS (origin project — semi-open vocab; catalogued by keys.py):")
    print("  core: .t/.title/.d/.desc/.tt(tooltip) · options .a…​.z · numbered .t.2/.desc2 ·"
          " compound .a.tt/.desc.a · NAMED variants (.desc.baltics, keep_leader) = expected")
    print("\nDRIFT PROBES — tier 1 (any hit = UNKNOWN → audit fails):")
    for name, pat in DRIFT_PROBES.items():
        print(f"  {name:<14} /{pat.pattern}/")
    print(f"  unknown-color   §<letter> outside {{{''.join(sorted(KNOWN_COLOR_LETTERS))}}}")
    print("\nNOTED PROBES — tier 2 (expected tail, reported not failed):")
    for name, pat in NOTED_PROBES.items():
        print(f"  {name:<14} /{pat.pattern}/")
    print("  unclosed-color  §X openers != §! closers in one string (cross-string colour span)")


# --- drift audit -----------------------------------------------------------------
def audit(arg):
    """Scan a file/dir. TIER 1 (drift) = unknown constructs → nonzero exit. TIER 2 (noted) =
    expected tail, reported for visibility. ALSO censuses the full colour-letter set so a run
    across all 206 shows the whole construct space, not just the slice's."""
    import clausewitz_parse as P
    lk = P.load(arg)
    drift = collections.Counter(); noted = collections.Counter(); loc = {}
    colour_letters = collections.Counter()

    for e in lk.entries:
        v = e.value
        for m in re.finditer(r'§([A-Za-z])', v):
            colour_letters[m.group(1)] += 1
        for cat, detail in color_letter_issues(v):            # unknown colour letter (drift)
            drift[(cat, detail)] += 1
            loc.setdefault((cat, detail), f'{e.source_file}:{e.line} {e.key}')
        for name, pat in DRIFT_PROBES.items():
            if pat.search(v):
                drift[('drift', name)] += 1
                loc.setdefault(('drift', name), f'{e.source_file}:{e.line} {e.key}: {v[:40]!r}')
        for name, pat in NOTED_PROBES.items():
            if pat.search(v):
                noted[('noted', name)] += 1
                loc.setdefault(('noted', name), f'{e.source_file}:{e.line} {e.key}: {v[:40]!r}')
        if color_unbalanced(v):
            noted[('noted', 'unclosed-color')] += 1
            loc.setdefault(('noted', 'unclosed-color'), f'{e.source_file}:{e.line} {e.key}')

    total = sum(drift.values())
    print(f"DRIFT AUDIT of {arg}   ({len(lk.entries)} entries, {len(lk.files)} files)")
    print(f"colour letters seen: {dict(colour_letters.most_common())}")
    print(f"colour letters OUTSIDE known set: {sorted(set(colour_letters) - KNOWN_COLOR_LETTERS) or 'none'}")
    print(f"\nUNKNOWN constructs (tier-1 drift): {total}")
    if total:
        for (cat, name), c in drift.most_common():
            print(f"  {cat:<13} {name!r}  ×{c}   first at {loc.get((cat, name), '?')}")
    else:
        print("  ✓ every construct is labeled & known to the registry")
    print(f"\nNOTED tail (tier-2, expected — reported, not a failure):")
    if noted:
        for (cat, name), c in noted.most_common():
            print(f"  {name:<15} ×{c}   first at {loc.get((cat, name), '?')}")
    else:
        print("  (none)")
    return total


if __name__ == '__main__':
    if '--audit' in sys.argv:
        i = sys.argv.index('--audit')
        target = sys.argv[i + 1] if len(sys.argv) > i + 1 else '../../data/hoi4/en'
        sys.exit(1 if audit(target) else 0)
    print_registry()
