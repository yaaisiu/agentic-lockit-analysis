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
VALID_ENTITY = re.compile(r'&(?:quot|lt|gt|amp|apos|#\d+);')


def check_string(text):
    issues = []
    # 1. known-tag balance
    stack = []
    has_markup = bool(VALID_ENTITY.search(text))
    for raw, name, kind in po_tokens.angle_tokens(text):
        if name not in po_tokens.KNOWN_TAGS:
            continue
        has_markup = True
        if kind == "open":
            stack.append(name)
        elif kind == "close":
            if not stack or stack[-1] != name:
                issues.append(f"unbalanced markup: {raw} (stack={stack})")
            else:
                stack.pop()
    if stack:
        issues.append(f"unclosed markup: {stack}")
    # 2. stray backslash (always valid — escapes are lexical)
    for m in BACKSLASH.finditer(text):
        if m.group(1) not in 'ntr"\\':
            issues.append(f"stray backslash: {text[max(0,m.start()-8):m.start()+4]!r}")
    # 3. unescaped ampersand — ONLY meaningful inside markup strings. In a plain-text label
    #    '&' is literal (e.g. "Save & Quit"), so gating on has_markup avoids false positives.
    if has_markup:
        for m in AMP.finditer(text):
            if not VALID_ENTITY.match(text, m.start()):
                issues.append(f"unescaped '&' in markup string: {text[m.start():m.start()+8]!r}")
    return issues


def main(argv):
    show_unknown = "--show-unknown" in argv
    if show_unknown:
        argv.remove("--show-unknown")
    paths = argv
    if not paths:
        print(__doc__); return 0
    total_issues = 0
    unknown = collections.Counter()
    for p in paths:
        for r in strings(parse_file(p)):
            for raw, name, kind in po_tokens.angle_tokens(r["msgid"]):
                if name not in po_tokens.KNOWN_TAGS:
                    unknown[name] += 1
            issues = check_string(r["msgid"])
            for it in issues:
                total_issues += 1
                print(f"{r['internal_id']}@L{r['lineno']}: {it}")
    print(f"\n# {total_issues} hard issue(s) across {len(paths)} file(s)", file=sys.stderr)
    if unknown:
        print(f"# {sum(unknown.values())} non-markup angle tokens ({len(unknown)} distinct) "
              f"— metasyntax/literal, tracked T2", file=sys.stderr)
        if show_unknown:
            for name, c in unknown.most_common():
                print(f"    <{name}> x{c}", file=sys.stderr)
    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
