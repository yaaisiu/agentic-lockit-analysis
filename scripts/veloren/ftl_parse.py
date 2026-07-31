#!/usr/bin/env python3
"""ftl_parse.py — dependency-free reader for Veloren's Fluent (.ftl) lockit.

=========================== WHY THIS EXISTS (read me) ===========================
This is the FOUNDATION script. Every other tool imports it. It exists because
`python-fluent` is not installed and our discipline is dependency-free, portable, and
reproducible (a weaker model / an API runner must be able to re-run it anywhere).

It codifies the anatomy CONFIRMED at GATE 1 (see vault/lockits/veloren/profile.md):
  * A Fluent file is a keyed tree, NOT rows×columns.
  * unit  = a MESSAGE  `id = value`           (id is globally unique across the bundle)
  * unit  = a TERM     `-id = value`           (shared snippet, referenced via { -id })
  * sub-unit = ATTRIBUTES `.name = value` (indented) — three roles we detect:
        metadata (.desc/.stat) · variant-array (.aN) · gender (.fem/.masc/.neut)
  * values/attributes may be MULTILINE and may contain PLACEABLES `{ ... }`:
        variables { $x } · selectors { $x -> [k]… *[other]… } · term/msg refs { -t }/{ m }
        · functions { TAIL($x) } · string literals { "" } (intentional blank)

=========================== HOW IT PARSES (the model) ===========================
Fluent's own grammar is context-free; a full parser is overkill for our needs
(inventory / extraction / validation — NOT re-serialisation). We use a robust
line+brace model that a less-capable agent can follow and reproduce:

  1. An ENTRY starts at column 0 with `id =` (message) or `-id =` (term).
  2. It CONTINUES through the following lines while they are indented AND we are either
     still inside an open placeable `{ … }` (brace depth > 0) — because selectors span
     lines — or the line is a normal indented continuation. A BLANK line at brace depth 0
     ENDS the entry (Fluent patterns don't contain blank lines).
  3. Inside an entry, an `.name =` line at brace depth 0 starts an ATTRIBUTE; everything
     else is continuation of the current value/attribute.
  4. Brace depth is counted IGNORING text inside "double-quoted" string literals, so
     `{"{"}` and `{""}` don't corrupt the count.

ASSUMPTIONS / LIMITS (documented on purpose):
  * We NORMALISE whitespace (strip + join multiline with '\n'); this is a reader for
    analysis, not a byte-exact rewriter. Do not use it to write .ftl back out.
  * A blank line ends a pattern (true for Veloren's files; matches Fluent norms).
  * Encoding is UTF-8, BOM tolerated on read (Fluent mandates no-BOM; validate.py flags it).

Run standalone to self-check against the GATE-1 census:
    python3 ftl_parse.py <dir-or-file>            # prints a census
    python3 ftl_parse.py <dir-or-file> --json     # dumps entries as JSON
"""
import re, os, sys, json, glob

IDENT = r'[A-Za-z][A-Za-z0-9_-]*'
RE_MSG_DEF  = re.compile(rf'^({IDENT})[ \t]*=(.*)$')
RE_TERM_DEF = re.compile(rf'^(-{IDENT})[ \t]*=(.*)$')
RE_ATTR_DEF = re.compile(rf'^[ \t]+\.({IDENT})[ \t]*=(.*)$')
RE_COMMENT  = re.compile(r'^(#{1,3})(?: ?(.*))?$')
EMPTY_VALUES = ('', '{""}', '{ "" }')

# Labeling is centralised in labels.py (the documented registry — single source of truth,
# with fluent-vs-project ORIGIN and an 'unknown' bucket for drift). ftl_parse just delegates.
import labels
GENDER_ATTRS = {'fem', 'masc', 'neut'}
def attr_role(name):
    """role only (metadata|gender|variant|other). See attr_label for the origin too."""
    return labels.label_attr(name)[0]
def attr_label(name):
    """-> (role, origin, note). origin ∈ {fluent, project, unknown}."""
    return labels.label_attr(name)

def _brace_delta(line):
    """Net { … } depth change on a line, ignoring "quoted literals"."""
    depth = 0; in_str = False; esc = False
    for ch in line:
        if in_str:
            if esc:            esc = False
            elif ch == '\\':   esc = True
            elif ch == '"':    in_str = False
        elif ch == '"':        in_str = True
        elif ch == '{':        depth += 1
        elif ch == '}':        depth -= 1
    return depth


class Entry:
    __slots__ = ('kind', 'id', 'value', 'attributes', 'comment', 'file', 'line', 'section')
    def __init__(self, kind, id, value, attributes, comment, file, line, section=None):
        self.kind = kind                # 'message' | 'term'
        self.id = id
        self.value = value              # str (may be '' / '{""}')
        self.attributes = attributes    # list[ (name, value) ] in file order
        self.comment = comment          # attached standalone comment or None
        self.file = file                # relative path (provenance — kept searchable)
        self.line = line                # 1-based line of the def
        self.section = section          # enclosing '##'/'###' group marker or None
    def value_is_empty(self):
        return self.value.strip() in EMPTY_VALUES


def parse_text(text, file='<mem>'):
    """Tokenise into entries.

    Boundary rule (fixed after real-file testing): an entry begins ONLY at a column-0
    DEFINITION (`id =` / `-id =`) or a COMMENT (`#`). Every other line — blank, indented,
    OR a column-0 line that is neither a def nor a comment — is CONTINUATION of the current
    entry's value. This faithfully captures Veloren's two multiline shapes that a naive
    "indented-only" rule drops: (a) internal blank lines inside a block value, and
    (b) block values whose continuation sits at column 0 (e.g. a selector `{ $x -> … }`
    written flush-left). A column-0 non-def line with no open entry is real junk."""
    lines = text.split('\n')
    entries = []
    comment_buf = []                    # standalone (#) comments awaiting the NEXT entry
    block_lines = None                  # raw lines of the entry under construction
    block_start = 0
    block_comment = None
    block_section = None
    section = None                      # current '##'/'###' group marker (see below)
    section_buf = []                    # consecutive marker lines being accumulated
    last_marker = -2                    # line index of the previous marker line

    def flush():
        nonlocal block_lines
        if block_lines is not None:
            entries.append(_build_entry(block_lines, file, block_start + 1,
                                        block_comment, block_section))
        block_lines = None

    for i, line in enumerate(lines):
        cm = RE_COMMENT.match(line)
        if cm:
            flush()
            if len(cm.group(1)) == 1:   # '#' may attach to the next entry
                comment_buf.append(cm.group(2) or '')
            else:
                # '##' (group) / '###' (resource) markers do NOT attach to one entry — they
                # OPEN A SECTION that runs until the next marker. We keep the most recent one
                # as structural context: it is the finest-grained grouping Fluent offers, and
                # far finer than the file (48 files over ~7k units). Fluent distinguishes the
                # two levels; we deliberately collapse them, because both answer the same
                # question — "what part of the game is this?" — and a '###' only ever appears
                # where no '##' has yet applied.
                #
                # CONSECUTIVE marker lines are ONE section: Veloren writes two-line blocks
                # ("### This file contains non-player-facing items." / "### Feel free to
                # ignore them."), and keeping only the last line turns a real signal into a
                # dangling fragment. Joined like the '#' comment buffer above.
                section_buf = (section_buf if i == last_marker + 1 else []) + \
                              [(cm.group(2) or '').strip()]
                last_marker = i
                section = '\n'.join(x for x in section_buf if x) or None
                comment_buf = []
            continue
        is_def = (line[:1] not in (' ', '\t')) and \
                 bool(RE_TERM_DEF.match(line) or RE_MSG_DEF.match(line))
        if is_def:
            flush()
            block_lines = [line]
            block_start = i
            block_comment = '\n'.join(comment_buf) if comment_buf else None
            block_section = section
            comment_buf = []
            continue
        # continuation of the open entry, else blank/junk between entries
        if block_lines is not None:
            block_lines.append(line)
        elif line.strip() == '':
            comment_buf = []            # blank breaks comment attachment
        else:
            entries.append(Entry('junk', None, line, [], None, file, i + 1))
    flush()
    return entries


def _build_entry(block, file, lineno, comment, section=None):
    m = RE_TERM_DEF.match(block[0]) or RE_MSG_DEF.match(block[0])
    ident = m.group(1)
    kind = 'term' if ident.startswith('-') else 'message'
    inline = m.group(2)
    value_lines = [inline.strip()] if inline.strip() else []
    attrs = []                          # list of [name, [lines]]
    cur_lines = value_lines
    depth = _brace_delta(block[0])
    for nl in block[1:]:
        adef = RE_ATTR_DEF.match(nl) if depth <= 0 else None
        if adef:
            name = adef.group(1); rest = adef.group(2)
            cur_lines = [rest.strip()] if rest.strip() else []
            attrs.append([name, cur_lines])
        else:
            cur_lines.append(nl.strip())
        depth += _brace_delta(nl)
    value = '\n'.join(value_lines).strip()
    attributes = [(name, '\n'.join(ls).strip()) for name, ls in attrs]
    return Entry(kind, ident, value, attributes, comment, file, lineno, section)


def parse_file(path, root=None):
    text = open(path, encoding='utf-8-sig').read()
    rel = os.path.relpath(path, root) if root else path
    return parse_text(text, rel)


def iter_files(target):
    if os.path.isdir(target):
        return sorted(glob.glob(os.path.join(target, '**', '*.ftl'), recursive=True))
    return [target]


def parse_tree(target):
    """Parse a dir (or file). Returns (entries, root). root used for relative paths."""
    root = target if os.path.isdir(target) else os.path.dirname(target)
    entries = []
    for p in iter_files(target):
        entries.extend(parse_file(p, root))
    return entries, root


# ---- placeables -----------------------------------------------------------------
def placeables(text):
    """Top-level { … } SPANS in order (brace-matched, quote-aware) -> [(start, end, inner)].

    WHY SPANS (not just the inner text): a placeable has to be RE-ANCHORABLE in the string
    it came from. The bundle contract we export to (lockit-annotator contracts/
    line.schema.json) requires every placeholder to carry (start, end, token) with
    source_text[start:end] == token EXACTLY, delimiters included — and offsets are what an
    annotation is stored against. This function used to return only text[i+1:j-1].strip(),
    which threw the offsets away AND made the value differ from the real source slice on 495
    of this corpus's 1267 placeables (any `{ $x }` with inner spacing). Nothing could be
    re-anchored from that.

    `inner` is still STRIPPED, because classify_placeable / selector_variant_keys /
    labels.label_placeable are all written against the stripped form; the exact source slice
    is text[start:end], so nothing is lost. Callers wanting only the inner text write:
        for _s, _e, p in placeables(t):

    An UNTERMINATED placeable is NOT emitted (we stop scanning). The old code appended
    text[i+1:n-1] — inventing a token that ends nowhere and silently dropping the last
    character. As a SPAN that becomes a mask swallowing the rest of the string, which is far
    worse than absence. Unbalanced braces are a structural defect and validate.py already
    reports them as an ERROR; that stays the channel a human hears about it. (0 in the
    Veloren en corpus.)

    NOTE for nesting: this is TOP-LEVEL only, by design — the bundle contract's v0.2
    containment model lists top-level placeables only, and a selector is ONE span covering
    its variant text. validate.py recurses into selector bodies for its own checks; spans
    from that recursion are relative to the inner string, not to the unit.
    """
    out = []; i = 0; n = len(text)
    while i < n:
        if text[i] == '{':
            depth = 1; j = i + 1; in_str = False; esc = False
            while j < n and depth:
                c = text[j]
                if in_str:
                    if esc: esc = False
                    elif c == '\\': esc = True
                    elif c == '"': in_str = False
                elif c == '"': in_str = True
                elif c == '{': depth += 1
                elif c == '}': depth -= 1
                j += 1
            if depth:                       # unterminated → not a placeable
                break
            out.append((i, j, text[i + 1:j - 1].strip()))
            i = j
        else:
            i += 1
    return out


def classify_placeable(p):
    """-> (kind, detail). kinds: var, selector, term-ref, function, literal, msg-ref, other"""
    if p.startswith('$'):
        mm = re.match(rf'\$({IDENT})', p)
        return ('selector', mm.group(1)) if '->' in p else ('var', mm.group(1) if mm else p)
    if '->' in p:
        mm = re.search(rf'\$({IDENT})', p)
        return ('selector', mm.group(1) if mm else '')
    if p.startswith('-'):
        mm = re.match(rf'(-{IDENT})', p); return ('term-ref', mm.group(1) if mm else p)
    if p.startswith('"'):
        return ('literal', p[1:-1] if len(p) >= 2 else '')
    mf = re.match(rf'([A-Z][A-Z0-9_]+)\s*\(', p)
    if mf:
        return ('function', mf.group(1))
    mr = re.match(rf'({IDENT}(?:\.{IDENT})?)$', p)
    if mr:
        return ('msg-ref', mr.group(1))
    return ('other', p)


def all_variables(text):
    """Every $var in text (incl. inside selectors) — for the variable inventory."""
    return re.findall(rf'\$({IDENT})', text)


def selector_variant_keys(placeable_text):
    """Variant keys of a selector placeable, with which is default (leading *)."""
    keys = []
    for star, key in re.findall(r'(\*?)\[\s*([A-Za-z0-9_ .-]+?)\s*\]', placeable_text):
        keys.append((key, bool(star)))
    return keys


# ---- translatable units ---------------------------------------------------------
def iter_units(entries, include_empty=False):
    """Yield translatable units as dicts. A unit is a message/term VALUE or an ATTRIBUTE.
    Empty ({""}) units are skipped unless include_empty=True (GATE 1: track but exclude
    from translatable counts). role is 'value' for the message value, else the attr role."""
    for e in entries:
        if e.kind == 'junk':
            continue
        if include_empty or not e.value_is_empty():
            yield {'file': e.file, 'line': e.line, 'id': e.id, 'kind': e.kind,
                   'attr': None, 'role': 'value', 'text': e.value,
                   'empty': e.value_is_empty()}
        for name, val in e.attributes:
            empty = val.strip() in EMPTY_VALUES
            if include_empty or not empty:
                yield {'file': e.file, 'line': e.line, 'id': e.id, 'kind': e.kind,
                       'attr': name, 'role': attr_role(name), 'text': val, 'empty': empty}


# ---- standalone: self-check census ---------------------------------------------
def _census(target):
    entries, _ = parse_tree(target)
    msgs = [e for e in entries if e.kind == 'message']
    terms = [e for e in entries if e.kind == 'term']
    junk = [e for e in entries if e.kind == 'junk']
    attr_total = sum(len(e.attributes) for e in entries if e.kind != 'junk')
    ids = [e.id for e in msgs]
    dup = len(ids) - len(set(ids))
    empties = sum(1 for e in entries if e.kind != 'junk' and e.value_is_empty()) \
        + sum(1 for e in entries if e.kind != 'junk'
              for _, v in e.attributes if v.strip() in EMPTY_VALUES)
    roles = {}
    for e in entries:
        for name, _ in getattr(e, 'attributes', []):
            roles[attr_role(name)] = roles.get(attr_role(name), 0) + 1
    print(f"files parsed:        {len(iter_files(target))}")
    print(f"messages:            {len(msgs)}  (unique ids: {len(set(ids))}, collisions: {dup})")
    print(f"terms:               {len(terms)}")
    print(f"attributes:          {attr_total}   by role: {roles}")
    print(f"junk lines:          {len(junk)}")
    print(f"intentional empties: {empties}")
    print(f"translatable units:  {sum(1 for _ in iter_units(entries))}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: ftl_parse.py <dir-or-file> [--json]")
    target = sys.argv[1]
    if '--json' in sys.argv:
        entries, _ = parse_tree(target)
        out = [{'kind': e.kind, 'id': e.id, 'file': e.file, 'line': e.line,
                'value': e.value, 'attributes': e.attributes, 'comment': e.comment,
                'section': e.section}
               for e in entries if e.kind != 'junk']
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        _census(target)
