#!/usr/bin/env python3
"""inventory.py — placeholder / placeable inventory for the Veloren Fluent lockit.

WHY: GATE 1 (variables.md) confirmed 5 placeable classes; translators & QA need to know
exactly which tokens appear, how often, and in which keys, so nothing is accidentally
translated or dropped. This is the `list_placeholders.py` role from spec §7, specialised
to Fluent. All counts come from the shared reader (ftl_parse) so they can never drift from
the parser's model. No network, no deps.

Classes reported (see classify_placeable in ftl_parse):
  var        { $x }            runtime arg — preserve verbatim
  selector   { $x -> … }       inline plural/conditional — keep intact
  function   { TAIL($x) }      Veloren-custom / Fluent built-in — preserve
  term-ref   { -term }         reference to a shared snippet
  msg-ref    { message[.attr] }reference to another message
  literal    { "…" }           literal ({""} = intentional blank)

Usage:
  python3 inventory.py <dir-or-file>            # human summary
  python3 inventory.py <dir-or-file> --json     # machine-readable
"""
import sys, json, re, collections
import ftl_parse as F


def build(target):
    entries, _ = F.parse_tree(target)
    inv = {
        'var': collections.Counter(), 'selector': collections.Counter(),
        'function': collections.Counter(), 'term-ref': collections.Counter(),
        'msg-ref': collections.Counter(), 'literal': collections.Counter(),
        'other': collections.Counter(),
    }
    var_keys = collections.defaultdict(set)      # var name -> set of keys using it
    var_in_value = var_in_attr = 0
    selector_keys = collections.Counter()        # variant key -> count
    charset = collections.Counter()
    empties = 0

    for u in F.iter_units(entries, include_empty=True):
        text = u['text']
        for _s, _e, p in F.placeables(text):
            kind, detail = F.classify_placeable(p)
            inv[kind][detail] += 1
            if kind == 'var':
                var_keys[detail].add(u['id'])
                (var_in_attr and None)
                if u['attr'] is None: var_in_value += 1
                else: var_in_attr += 1
            if kind == 'selector':
                for key, is_def in F.selector_variant_keys(p):
                    selector_keys[('*' if is_def else '') + key] += 1
            if kind == 'literal' and detail == '':
                empties += 1
        # variable charset census (all $vars, incl. nested inside selectors)
        for v in F.all_variables(text):
            if v.isupper():            charset['UPPER'] += 1
            elif '-' in v:             charset['has-hyphen'] += 1
            elif any(c.isdigit() for c in v): charset['has-digit'] += 1
            else:                       charset['lower_snake'] += 1
    return {
        'inv': inv, 'var_keys': var_keys, 'var_in_value': var_in_value,
        'var_in_attr': var_in_attr, 'selector_keys': selector_keys,
        'charset': charset, 'empties': empties,
    }


def main(target, as_json):
    d = build(target)
    inv = d['inv']
    if as_json:
        out = {k: dict(v) for k, v in inv.items()}
        out['selector_variant_keys'] = dict(d['selector_keys'])
        out['var_charset'] = dict(d['charset'])
        out['var_in_value'] = d['var_in_value']; out['var_in_attr'] = d['var_in_attr']
        print(json.dumps(out, ensure_ascii=False, indent=1)); return

    def total(c): return sum(c.values())
    print(f"VARIABLES  {{ $x }}   refs={total(inv['var'])}  unique={len(inv['var'])}"
          f"  (on values={d['var_in_value']}, on attributes={d['var_in_attr']})")
    for name, cnt in inv['var'].most_common(15):
        print(f"    ${name:<24} {cnt:4d}  in {len(d['var_keys'][name])} keys")
    print("    charset:", dict(d['charset']))
    print(f"\nSELECTORS  {{ $x -> … }}   count={total(inv['selector'])}")
    import labels
    keys_annot = ', '.join(f'{k}({c})[{labels.label_variant_key(k.lstrip("*"))[0]}]'
                           for k, c in d['selector_keys'].most_common())
    print("    variant keys:", keys_annot)
    fns = ', '.join(f'{n}({c}) origin={labels.label_function(n)[0]}'
                    for n, c in inv['function'].items())
    print(f"\nFUNCTIONS  {{ FUNC() }}   {fns}")
    print(f"TERM-REFS  {{ -t }}       {dict(inv['term-ref'])}")
    print(f"MSG-REFS   {{ m[.a] }}    count={total(inv['msg-ref'])}  unique={len(inv['msg-ref'])}")
    print(f"LITERALS   {{ \"…\" }}      count={total(inv['literal'])}  of which empty {{\"\"}}={d['empties']}")
    if total(inv['other']):
        print(f"OTHER (unclassified):    {dict(inv['other'])}   <-- inspect these")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("usage: inventory.py <dir-or-file> [--json]")
    main(sys.argv[1], '--json' in sys.argv)
