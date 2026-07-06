#!/usr/bin/env python3
"""extract.py — pull translatable units from the Veloren Fluent lockit by selector.

WHY: spec §7 `extract_by_type`. Downstream work (translation, a Polish audit) needs to
slice the lockit: "give me every gender form", "every string in hud/", "everything under
the buff- namespace", "every message with a plural selector". Because Fluent isn't tabular,
"type" means: source file, key namespace/prefix, or ATTRIBUTE ROLE (metadata / variant /
gender / value) — the roles confirmed at GATE 1 (T-V1). Emitting the role column is the
concrete demonstration of T-V5 (does tagging sub-kinds help?) — you can now filter on it.

Units come from ftl_parse.iter_units so extraction can never disagree with the parser.
{""} intentional-empties are excluded unless --include-empty. No deps, local files only.

Usage:
  python3 extract.py <dir> [filters] [--format tsv|json] [--include-empty]
Filters (combine freely; all must match):
  --file SUBSTR        only units whose file path contains SUBSTR   (e.g. --file item/)
  --prefix STR         only ids starting with STR                   (e.g. --prefix hud-)
  --role ROLE          value | metadata | variant | gender | other  (repeatable)
  --attr NAME          only a specific attribute name               (e.g. --attr desc)
  --has-selector       only units whose text contains a { -> } selector
  --has-var            only units containing at least one { $var }
Output columns (tsv): file  line  id  attr  role  text(one-line)
"""
import sys, json
import ftl_parse as F


def parse_args(argv):
    a = {'file': None, 'prefix': None, 'roles': [], 'attr': None,
         'has_selector': False, 'has_var': False, 'format': 'tsv', 'include_empty': False}
    i = 0
    while i < len(argv):
        t = argv[i]
        if t == '--file': a['file'] = argv[i + 1]; i += 2
        elif t == '--prefix': a['prefix'] = argv[i + 1]; i += 2
        elif t == '--role': a['roles'].append(argv[i + 1]); i += 2
        elif t == '--attr': a['attr'] = argv[i + 1]; i += 2
        elif t == '--has-selector': a['has_selector'] = True; i += 1
        elif t == '--has-var': a['has_var'] = True; i += 1
        elif t == '--include-empty': a['include_empty'] = True; i += 1
        elif t == '--format': a['format'] = argv[i + 1]; i += 2
        else: i += 1
    return a


def select(target, a):
    entries, _ = F.parse_tree(target)
    for u in F.iter_units(entries, include_empty=a['include_empty']):
        if a['file'] and a['file'] not in u['file']: continue
        if a['prefix'] and not u['id'].startswith(a['prefix']): continue
        if a['roles'] and u['role'] not in a['roles']: continue
        if a['attr'] and u['attr'] != a['attr']: continue
        if a['has_selector'] and '->' not in u['text']: continue
        if a['has_var'] and not F.all_variables(u['text']): continue
        yield u


def main(target, argv):
    a = parse_args(argv)
    rows = list(select(target, a))
    if a['format'] == 'json':
        print(json.dumps(rows, ensure_ascii=False, indent=1)); return
    for u in rows:
        text = u['text'].replace('\t', '\\t').replace('\n', '\\n')
        print(f"{u['file']}\t{u['line']}\t{u['id']}\t{u['attr'] or ''}\t{u['role']}\t{text}")
    print(f"# {len(rows)} units", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
