#!/usr/bin/env python3
"""gender_pairs.py — collect grammatical-gender attribute sets (.fem/.masc/.neut).

WHY: GATE 1 found a THIRD attribute role — grammatical gender (616 attrs: fem 303, masc
303, neut 10). This is the SAME CONCEPT as Wesnoth's gender/agreement family (different
mechanism: there an inline `female^` prefix, here Fluent attributes) — a cross-format reuse
worth a dedicated tool. A downstream Polish audit lives or dies on gender agreement, so we
surface each message's gender forms side-by-side AND flag INCOMPLETE sets (e.g. a fem form
with no masc) — those are the interesting QA cases. Deterministic; built on ftl_parse.

Usage:
  python3 gender_pairs.py <dir-or-file>            # table + incomplete-set report
  python3 gender_pairs.py <dir-or-file> --json
"""
import sys, json
import ftl_parse as F

GENDER = ('masc', 'fem', 'neut')


def collect(target):
    entries, _ = F.parse_tree(target)
    rows = []
    for e in entries:
        if e.kind == 'junk':
            continue
        g = {name: val for name, val in e.attributes if name in GENDER}
        if g:
            rows.append({'file': e.file, 'line': e.line, 'id': e.id,
                         'value': e.value,
                         **{k: g.get(k, '') for k in GENDER},
                         'complete': all(k in g for k in ('masc', 'fem'))})
    return rows


def main(target, as_json):
    rows = collect(target)
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1)); return
    print(f"messages carrying gender forms: {len(rows)}")
    incomplete = [r for r in rows if not r['complete']]
    print(f"  with both masc+fem: {len(rows) - len(incomplete)}   incomplete: {len(incomplete)}\n")
    for r in rows[:20]:
        print(f"  {r['id']}  ({r['file']}:{r['line']})")
        print(f"      masc={r['masc']!r}  fem={r['fem']!r}" + (f"  neut={r['neut']!r}" if r['neut'] else ""))
    if len(rows) > 20:
        print(f"  … {len(rows) - 20} more (use --json for all)")
    if incomplete:
        print(f"\nINCOMPLETE gender sets (missing masc or fem) — {len(incomplete)}:")
        for r in incomplete[:15]:
            have = [k for k in GENDER if r[k]]
            print(f"  {r['id']}  has only: {', '.join(have)}   ({r['file']}:{r['line']})")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: gender_pairs.py <dir-or-file> [--json]")
    main(sys.argv[1], '--json' in sys.argv)
