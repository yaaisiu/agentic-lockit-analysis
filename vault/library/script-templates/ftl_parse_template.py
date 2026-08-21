#!/usr/bin/env python3
# vault/library/script-templates/ftl_parse_template.py
# TEMPLATE — dependency-free reader for ANY Project Fluent (.ftl) lockit. first_seen: veloren (session 002).
"""
PURPOSE: parse a Fluent file/tree into messages, terms, attributes, and classified placeables,
for inventory / extraction / validation (NOT byte-exact re-serialisation). The counterpart of
[[po_parse_template]] for gettext. Embodies convention [[fluent-ftl]].

WHY (rationale a less-capable agent can follow and reproduce):
- python-fluent may be absent and our discipline is dependency-free + portable. Fluent's real
  grammar is context-free, but our needs don't require a spec-perfect parser — they require a
  FACTUAL, reproducible structural read. A line+brace model delivers that and is easy to reason
  about. (Prove correctness by reproducing a recon census: message/attr counts + 0 junk.)
- The one non-obvious rule, learned the hard way: an entry's boundary is NOT "indented lines".
  Block values can contain internal blank lines AND can continue flush at column 0 (e.g. a
  selector written left-aligned). So: an entry BEGINS at a column-0 definition (`id =` / `-id =`)
  or a comment, and CONTINUES by absorbing every other line until the next such boundary. Track
  brace depth (ignoring "quoted" literals) so an indented `.name =` inside an open `{ … }` is
  not mistaken for an attribute.
- Labeling the MEANING of attribute names / custom functions is PROJECT-specific — this template
  returns raw structure; layer [[construct-origin-labeling]] on top per lockit.

HOW TO PARAMETERISE for a new Fluent lockit:
- Usually nothing: the reader is format-general. Add project labeling in a separate module
  (e.g. label_attr(name)->role/origin, known custom functions) and call it on `Entry.attributes`.
- iter_units(entries) yields translatable units (message/term values + non-empty attributes);
  pass include_empty=True to also see {""} blanks.

CLI: python3 ftl_parse_template.py <dir-or-file> [--json]
"""
import re, os, sys, json, glob

IDENT = r'[A-Za-z][A-Za-z0-9_-]*'
RE_MSG_DEF  = re.compile(rf'^({IDENT})[ \t]*=(.*)$')
RE_TERM_DEF = re.compile(rf'^(-{IDENT})[ \t]*=(.*)$')
RE_ATTR_DEF = re.compile(rf'^[ \t]+\.({IDENT})[ \t]*=(.*)$')
RE_COMMENT  = re.compile(r'^(#{1,3})(?: ?(.*))?$')
EMPTY_VALUES = ('', '{""}', '{ "" }')


def _brace_delta(line):
    """Net { … } depth change on a line, ignoring "quoted literals" (so {"{"} / {""} are safe)."""
    depth = 0; in_str = False; esc = False
    for ch in line:
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        elif ch == '"': in_str = True
        elif ch == '{': depth += 1
        elif ch == '}': depth -= 1
    return depth


class Entry:
    __slots__ = ('kind', 'id', 'value', 'attributes', 'comment', 'file', 'line')
    def __init__(self, kind, id, value, attributes, comment, file, line):
        self.kind = kind                # 'message' | 'term' | 'junk'
        self.id = id
        self.value = value
        self.attributes = attributes    # list[(name, value)] in file order
        self.comment = comment
        self.file = file
        self.line = line
    def value_is_empty(self):
        return self.value.strip() in EMPTY_VALUES


def parse_text(text, file='<mem>'):
    """Entry boundary = column-0 definition or comment; everything else is continuation."""
    lines = text.split('\n')
    entries = []
    comment_buf = []
    block_lines = None; block_start = 0; block_comment = None

    def flush():
        nonlocal block_lines
        if block_lines is not None:
            entries.append(_build_entry(block_lines, file, block_start + 1, block_comment))
        block_lines = None

    for i, line in enumerate(lines):
        cm = RE_COMMENT.match(line)
        if cm:
            flush()
            comment_buf = comment_buf + [cm.group(2) or ''] if len(cm.group(1)) == 1 else []
            continue
        is_def = (line[:1] not in (' ', '\t')) and bool(RE_TERM_DEF.match(line) or RE_MSG_DEF.match(line))
        if is_def:
            flush()
            block_lines = [line]; block_start = i
            block_comment = '\n'.join(comment_buf) if comment_buf else None
            comment_buf = []
            continue
        if block_lines is not None:
            block_lines.append(line)
        elif line.strip() == '':
            comment_buf = []
        else:
            entries.append(Entry('junk', None, line, [], None, file, i + 1))
    flush()
    return entries


def _build_entry(block, file, lineno, comment):
    m = RE_TERM_DEF.match(block[0]) or RE_MSG_DEF.match(block[0])
    ident = m.group(1)
    kind = 'term' if ident.startswith('-') else 'message'
    value_lines = [m.group(2).strip()] if m.group(2).strip() else []
    attrs = []
    cur_lines = value_lines
    depth = _brace_delta(block[0])
    for nl in block[1:]:
        adef = RE_ATTR_DEF.match(nl) if depth <= 0 else None
        if adef:
            cur_lines = [adef.group(2).strip()] if adef.group(2).strip() else []
            attrs.append([adef.group(1), cur_lines])
        else:
            cur_lines.append(nl.strip())
        depth += _brace_delta(nl)
    value = '\n'.join(value_lines).strip()
    attributes = [(name, '\n'.join(ls).strip()) for name, ls in attrs]
    return Entry(kind, ident, value, attributes, comment, file, lineno)


def iter_files(target):
    if os.path.isdir(target):
        return sorted(glob.glob(os.path.join(target, '**', '*.ftl'), recursive=True))
    return [target]


def parse_file(path, root=None):
    text = open(path, encoding='utf-8-sig').read()
    return parse_text(text, os.path.relpath(path, root) if root else path)


def parse_tree(target):
    root = target if os.path.isdir(target) else os.path.dirname(target)
    out = []
    for p in iter_files(target):
        out.extend(parse_file(p, root))
    return out, root


# ---- placeables -----------------------------------------------------------------
def placeables(text):
    """Top-level { … } SPANS in order (brace-matched, quote-aware) -> [(start, end, inner)].

    WHY SPANS AND NOT JUST THE TEXT (changed s007; see [[construct-spans-not-tokens]]):
    a placeable must be RE-ANCHORABLE in the string it came from. Anything downstream that
    stores an annotation, a highlight, or a QA finding stores it as an OFFSET, and offsets
    cannot be recovered later. This function used to return only `text[i+1:j-1].strip()`,
    which threw the offsets away AND made the returned value differ from the real source
    slice on 495 of one corpus's 1267 placeables (every `{ $x }` with inner spacing).
    Nothing could be re-anchored from that, and the loss was invisible until someone needed it.

    `inner` is still STRIPPED, because the classifiers are written against the stripped form;
    the exact source slice is `text[start:end]`, so nothing is lost. Callers wanting only the
    inner text write:  `for _s, _e, p in placeables(t):`

    An UNTERMINATED placeable is NOT emitted (we stop scanning). The old code appended
    `text[i+1:n-1]` — inventing a token that ends nowhere and silently dropping the last
    character. As a SPAN that becomes a mask swallowing the rest of the string, which is far
    worse than absence. Unbalanced braces are a structural defect; the validator is the
    channel a human should hear about it on.

    TOP-LEVEL ONLY, by design. A selector comes back as ONE span covering its variant bodies —
    correct for counting and validation, WRONG for masking, because those bodies are
    translatable prose. If your consumer subtracts spans from the text, you need a flattening
    pass on top of this; see [[construct-spans-not-tokens]] § "a span used as a MASK".

    CHANGING THIS IN A LIVE TOOLKIT: change it IN PLACE, never via a sibling function (a
    duplicate brace scanner is exactly the drift this template exists to prevent), and PROVE
    the migration — capture every downstream tool's output before the edit and diff for
    byte-identity after. Watch for call sites where a missed unpack fails SILENTLY (one used
    the result as a Counter key: a tuple is hashable, so it would have printed `(12, 20, '$x')`
    instead of raising). Pin those with a test.
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
            if depth:
                break                      # unterminated: emit nothing, don't invent a span
            out.append((i, j, text[i + 1:j - 1].strip())); i = j
        else:
            i += 1
    return out


def classify_placeable(p):
    """-> (kind, detail). kinds: var, selector, term-ref, function, literal, msg-ref, other."""
    if p.startswith('$'):
        mm = re.match(rf'\$({IDENT})', p)
        return ('selector', mm.group(1) if mm else '') if '->' in p else ('var', mm.group(1) if mm else p)
    if '->' in p:
        mm = re.search(rf'\$({IDENT})', p); return ('selector', mm.group(1) if mm else '')
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
    return re.findall(rf'\$({IDENT})', text)


def selector_variant_keys(placeable_text):
    return [(key, bool(star)) for star, key in
            re.findall(r'(\*?)\[\s*([A-Za-z0-9_ .-]+?)\s*\]', placeable_text)]


def iter_units(entries, include_empty=False):
    for e in entries:
        if e.kind == 'junk':
            continue
        if include_empty or not e.value_is_empty():
            yield {'file': e.file, 'line': e.line, 'id': e.id, 'kind': e.kind,
                   'attr': None, 'text': e.value, 'empty': e.value_is_empty()}
        for name, val in e.attributes:
            empty = val.strip() in EMPTY_VALUES
            if include_empty or not empty:
                yield {'file': e.file, 'line': e.line, 'id': e.id, 'kind': e.kind,
                       'attr': name, 'text': val, 'empty': empty}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: ftl_parse_template.py <dir-or-file> [--json]")
    entries, _ = parse_tree(sys.argv[1])
    if '--json' in sys.argv:
        print(json.dumps([{'kind': e.kind, 'id': e.id, 'file': e.file, 'line': e.line,
                           'value': e.value, 'attributes': e.attributes}
                          for e in entries if e.kind != 'junk'], ensure_ascii=False, indent=1))
    else:
        msgs = [e for e in entries if e.kind == 'message']
        ids = [e.id for e in msgs]
        print(f"files: {len(iter_files(sys.argv[1]))}  messages: {len(msgs)} "
              f"(unique {len(set(ids))}, collisions {len(ids) - len(set(ids))})  "
              f"terms: {sum(1 for e in entries if e.kind == 'term')}  "
              f"attributes: {sum(len(e.attributes) for e in entries if e.kind != 'junk')}  "
              f"junk: {sum(1 for e in entries if e.kind == 'junk')}")
