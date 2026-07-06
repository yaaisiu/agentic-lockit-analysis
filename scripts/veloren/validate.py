#!/usr/bin/env python3
"""validate.py — structural validation of the Veloren Fluent SOURCE (single locale).

WHY: before trusting extraction or shipping a lockit, check the source is well-formed.
This is the Fluent analogue of Wesnoth's validate_markup, and it borrows that library
heuristic's SEVERITY philosophy ([[markup-families]]): structural breakage = ERROR;
suspicious-but-tolerated = WARN. There is NO angle-bracket markup in Fluent (GATE 1), so
instead we validate the things that actually break a Fluent bundle:

  ERROR  unbalanced placeable braces { }              (bundle fails to parse)
  ERROR  selector with != 1 default variant *[…]      (Fluent requires exactly one)
  ERROR  UTF-8 BOM present                            (Fluent mandates no-BOM)
  WARN   selector variant key not a CLDR category nor an integer
  WARN   placeable we cannot classify (kind 'other')  (unknown token — inspect)

Deterministic, dependency-free, built on ftl_parse. Exit code = number of ERRORs (0 = clean),
so it doubles as a CI gate. Cross-LOCALE checks (source vs translation) are a separate tool.

Usage:
  python3 validate.py <dir-or-file> [--warn]     # --warn also lists warnings
"""
import sys, os, glob
import ftl_parse as F

CLDR = {'zero', 'one', 'two', 'few', 'many', 'other'}


def brace_balanced(text):
    depth = 0; in_str = False; esc = False
    for ch in text:
        if in_str:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': in_str = False
        elif ch == '"': in_str = True
        elif ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0: return False
    return depth == 0


def check_placeables(text, findings, ctx):
    """Recurse through placeables; validate selectors + flag unknowns."""
    for p in F.placeables(text):
        kind, _ = F.classify_placeable(p)
        if kind == 'selector':
            keys = F.selector_variant_keys(p)
            defaults = sum(1 for _, d in keys if d)
            if defaults != 1:
                findings.append(('ERROR', ctx, f"selector has {defaults} default variants (need exactly 1)"))
            for key, _ in keys:
                if key not in CLDR and not key.lstrip('-').isdigit():
                    findings.append(('WARN', ctx, f"selector variant key '[{key}]' is not a CLDR category or integer"))
            # recurse into variant bodies (nested selectors/placeables)
            inner = p[p.index('->') + 2:]
            check_placeables(inner, findings, ctx)
        elif kind == 'other':
            findings.append(('WARN', ctx, f"unclassified placeable {{ {p[:40]} }}"))


def validate(target):
    findings = []
    # BOM check at the byte level (ftl_parse reads with utf-8-sig, so check raw here)
    for path in F.iter_files(target):
        if open(path, 'rb').read(3) == b'\xef\xbb\xbf':
            rel = os.path.relpath(path, target if os.path.isdir(target) else os.path.dirname(target))
            findings.append(('ERROR', f"{rel}", "file has a UTF-8 BOM (Fluent mandates no-BOM)"))

    entries, _ = F.parse_tree(target)
    for u in F.iter_units(entries, include_empty=True):
        ctx = f"{u['file']}:{u['line']} {u['id']}" + (f".{u['attr']}" if u['attr'] else "")
        if not brace_balanced(u['text']):
            findings.append(('ERROR', ctx, "unbalanced placeable braces { }"))
            continue
        check_placeables(u['text'], findings, ctx)
    return findings


def main(target, show_warn):
    findings = validate(target)
    errors = [f for f in findings if f[0] == 'ERROR']
    warns = [f for f in findings if f[0] == 'WARN']
    for sev, ctx, msg in errors:
        print(f"ERROR  {ctx}\n         {msg}")
    if show_warn:
        for sev, ctx, msg in warns:
            print(f"WARN   {ctx}\n         {msg}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)"
          + ("" if show_warn else "  (use --warn to list warnings)"))
    return len(errors)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: validate.py <dir-or-file> [--warn]")
    sys.exit(main(sys.argv[1], '--warn' in sys.argv))
