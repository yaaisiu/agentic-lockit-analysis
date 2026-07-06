#!/usr/bin/env python3
# scripts/wesnoth/validate_markup.py
# source: profile wesnoth (GATE 1) — Marcin's C5.1/C5.3 ask: check markup & escapes are sound.
"""
WHY: broken Pango markup (unbalanced <b>…</b>), stray backslashes, or unescaped < > & will
render wrong or crash the game's text engine. This checks the ENGLISH SOURCE for those
defects (so we catch authoring issues) and — crucially for later — the same checks run on a
translation to catch a translator breaking the markup. It also separates real markup from
non-markup angle tokens (command-help metasyntax / literals), which resolves the Q2 noise.

Checks per string:
  1. KNOWN_TAGS balance — every <tag> has a matching </tag> (self-closing /> ignored).
  2. stray backslash — a '\\' not part of a known escape (\\n \\t \\r \\" \\\\).
  3. unescaped '&' — an '&' not starting a valid entity (&quot; &lt; … &#NN;).
Reports issues with internal_id:line. Non-markup angle tokens are summarised, not errored
(tracked as T2 — no cited translate/preserve rule yet).

Usage:  python validate_markup.py <file...> [--show-unknown]
Exit:   non-zero if any hard issue (balance/backslash/entity) is found.
"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings
import po_tokens

BACKSLASH = re.compile(r'\\(.)')
AMP = re.compile(r'&')
VALID_ENTITY = po_tokens.PATTERNS["entity"]   # single source of truth (incl. hex &#x/&#0x forms)


def check_string(text):
    """Validate one string's markup integrity, auto-selecting the family (see po_tokens).
    Returns a list of (severity, message) with severity in {"ERROR","WARN"}:
      * ERROR — structural: unbalanced/unclosed tags, unbalanced po4a, bare '<', stray '\\'.
      * WARN  — unescaped '&' inside a markup string. Wesnoth's engine tolerates a literal
                '&' used as shorthand for "and" (e.g. "swamp, & snow"), so this is flagged
                for a human, not treated as a hard failure (decided session 001, B1).
    Pango and DocBook share the open/close tag check; po4a (man pages) has its own."""
    if po_tokens.markup_family(text) == "po4a":
        return _check_po4a(text)
    return _check_tag(text)


def _check_tag(text):
    """Balanced-tag families: Pango (game UI) and DocBook (manual). Same grammar."""
    issues = []
    # 1. known-tag balance
    stack = []
    has_markup = bool(VALID_ENTITY.search(text))
    for raw, name, kind in po_tokens.angle_tokens(text):
        if name not in po_tokens.KNOWN_TAGS:
            continue
        has_markup = True
        if name in po_tokens.DOCBOOK_EMPTY:      # e.g. <imagedata …> is empty — never paired
            continue
        if kind == "open":
            stack.append(name)
        elif kind == "close":
            if not stack or stack[-1] != name:
                issues.append(("ERROR", f"unbalanced markup: {raw} (stack={stack})"))
            else:
                stack.pop()
    if stack:
        issues.append(("ERROR", f"unclosed markup: {stack}"))
    # 2. stray backslash (always valid — escapes are lexical)
    for m in BACKSLASH.finditer(text):
        if m.group(1) not in 'ntr"\\':
            issues.append(("ERROR", f"stray backslash: {text[max(0,m.start()-8):m.start()+4]!r}"))
    # 3. unescaped ampersand — ONLY meaningful inside markup strings. In a plain-text label
    #    '&' is literal (e.g. "Save & Quit"), so gating on has_markup avoids false positives.
    #    WARN not ERROR: the engine tolerates it and the source itself contains one.
    if has_markup:
        for m in AMP.finditer(text):
            if not VALID_ENTITY.match(text, m.start()):
                issues.append(("WARN", f"unescaped '&' in markup string: {text[m.start():m.start()+8]!r}"))
    return issues


def _check_po4a(text):
    """po4a / POD man markup: every span opener ([A-Z]<) closes at a '>'. A literal < > must
    be written E<lt> / E<gt>, so a bare '<' not preceded by an uppercase letter is a defect.
    Backslash/ampersand rules are roff's, not ours, so we don't police them here."""
    issues = []
    n_open = len(po_tokens.POD_OPEN.findall(text))
    n_close = text.count(">")
    if n_open != n_close:
        issues.append(("ERROR", f"unbalanced po4a markup: {n_open} opener(s) [A-Z]< vs {n_close} '>'"))
    for m in re.finditer(r'<', text):
        if m.start() == 0 or not text[m.start() - 1].isupper():
            issues.append(("ERROR", f"bare '<' in po4a (use E<lt>): {text[max(0,m.start()-6):m.start()+4]!r}"))
    return issues


def main(argv):
    show_unknown = "--show-unknown" in argv
    if show_unknown:
        argv.remove("--show-unknown")
    paths = argv
    if not paths:
        print(__doc__); return 0
    n_error = n_warn = 0
    fam_counts = collections.Counter()
    unknown = collections.Counter()          # residual bare <slot> metasyntax (tag strings only)
    for p in paths:
        for r in strings(parse_file(p)):
            fam = po_tokens.markup_family(r["msgid"])
            fam_counts[fam] += 1
            if fam == "tag":                 # po4a content isn't "unknown" — it's handled by _check_po4a
                for raw, name, kind in po_tokens.angle_tokens(r["msgid"]):
                    if name not in po_tokens.KNOWN_TAGS:
                        unknown[name] += 1
            for sev, msg in check_string(r["msgid"]):
                if sev == "ERROR": n_error += 1
                else: n_warn += 1
                print(f"{sev:5} {r['internal_id']}@L{r['lineno']}: {msg}")
    print(f"\n# {n_error} hard error(s), {n_warn} warning(s) across {len(paths)} file(s)",
          file=sys.stderr)
    print(f"# markup families seen: "
          f"{', '.join(f'{k}={v}' for k, v in fam_counts.most_common())}", file=sys.stderr)
    if unknown:
        print(f"# {sum(unknown.values())} bare <slot> command/CLI metasyntax "
              f"({len(unknown)} distinct) — argument placeholders, preserve verbatim (T2)",
              file=sys.stderr)
        if show_unknown:
            for name, c in unknown.most_common():
                print(f"    <{name}> x{c}", file=sys.stderr)
    return 1 if n_error else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
