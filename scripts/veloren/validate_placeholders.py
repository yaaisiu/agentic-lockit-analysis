#!/usr/bin/env python3
"""validate_placeholders.py — CROSS-LOCALE checker for the Veloren Fluent lockit.

WHY (this is one of our core capabilities): a translation must preserve the structure the
engine depends on, or strings break silently in the shipped game. A misspelled `{ $nam }`
renders literally; a dropped `{ $key }` loses information; an unbalanced `{` corrupts the
Fluent bundle. A human reviewer misses these at scale; a deterministic source-vs-translation
diff catches them cheaply. This is the Fluent instance of library convention
[[cross-locale-invariants]] + template [[validate_placeholders]] (which were gettext-shaped);
the invariants are the same, the reader (ftl_parse) and the placeholder syntax differ.

MATCH by identity: a translation keeps the source MESSAGE ID (globally unique) and attribute
name. We compare unit-for-unit `(id, attr|value)`.

INVARIANTS (per translated unit) — with the convention's "don't over-constrain" rule:
  ERROR  invented { $var } — a name in the translation absent from source (typo → literal)
  ERROR  dropped  { $var } — a source name missing from the translation ...
                             ...ONLY on NON-selector units (plural/selector variants may
                             legitimately omit a var — never flagged, per the convention)
  ERROR  unbalanced placeable braces { } in the translation (structural)
  WARN   source unit has a selector { -> } but the translation dropped it (may lose plural
         correctness — but some languages legitimately don't branch, so WARN not ERROR)
  WARN   invented { -term } reference not in source
  WARN   gender forms (.fem/.masc/.neut) present in source message but missing in translation
         (gender agreement — high-value for Polish; may be intentionally incomplete → WARN)
  (untranslated units and orphan target units are counted/《WARN》, not treated as defects)

We SURFACE defects; on third-party/upstream GPL data we never edit it. Exit code = #ERRORs.

Usage:
  python3 validate_placeholders.py <source-dir> <translation-dir> [--warn] [--json]
  e.g. python3 validate_placeholders.py ../../data/veloren/en ../../data/veloren/pl --warn
"""
import sys, os, json, collections
import ftl_parse as F
import labels

GENDER = {'fem', 'masc', 'neut'}


def build(target):
    """Return (units, gender_by_msg). units: {(id, attr|None): text}."""
    entries, _ = F.parse_tree(target)
    units = {}
    gender = collections.defaultdict(set)
    for e in entries:
        if e.kind == 'junk':
            continue
        units[(e.id, None)] = e.value
        for name, val in e.attributes:
            units[(e.id, name)] = val
            if name in GENDER:
                gender[e.id].add(name)
    return units, gender


def check_pair(src_dir, tr_dir):
    src, src_gender = build(src_dir)
    tr, _ = build(tr_dir)
    findings = []            # (severity, id, attr, msg)
    stats = collections.Counter()

    def add(sev, key, msg):
        findings.append((sev, key[0], key[1], msg)); stats[sev] += 1

    for key, tr_text in tr.items():
        if key not in src:
            add('WARN', key, "orphan: no matching source unit (stale id/attr?)")
            continue
        src_text = src[key]
        # skip units that are empty on either side (untranslated / intentional blank)
        if tr_text.strip() in F.EMPTY_VALUES or src_text.strip() in F.EMPTY_VALUES:
            stats['skipped_empty'] += 1
            continue
        stats['translated'] += 1
        # structural
        from validate import brace_balanced
        if not brace_balanced(tr_text):
            add('ERROR', key, "unbalanced placeable braces { } in translation")
            continue
        # A .aN variant array is a RANDOM-PICK set the engine reorders per locale, so matching
        # a translation's .a5 to the source's .a5 by index is unsound → skip var invent/drop
        # on variant-role units (still brace-checked above). Same "don't over-constrain" logic
        # the convention applies to plural forms. (WARN so it's visible we skipped.)
        is_variant = labels.label_attr(key[1])[0] == 'variant' if key[1] else False
        src_vars = set(F.all_variables(src_text))
        tr_vars = set(F.all_variables(tr_text))
        if not is_variant:
            # invented = a var in the translation absent from source AND not an engine-supplied
            # agreement var (gender context a locale may legitimately add).
            invented = {v for v in (tr_vars - src_vars) if not labels.is_engine_var(v)}
            if invented:
                add('ERROR', key, f"invented variable(s): {sorted('$' + v for v in invented)}")
            src_has_selector = '->' in src_text
            if not src_has_selector:
                dropped = src_vars - tr_vars
                if dropped:
                    add('ERROR', key, f"dropped variable(s): {sorted('$' + v for v in dropped)}")
            elif '->' not in tr_text:
                add('WARN', key, "source has a selector { -> } but translation dropped it")
        # term references
        src_terms = {d for p in F.placeables(src_text)
                     for k, d in [F.classify_placeable(p)] if k == 'term-ref'}
        tr_terms = {d for p in F.placeables(tr_text)
                    for k, d in [F.classify_placeable(p)] if k == 'term-ref'}
        if tr_terms - src_terms:
            add('WARN', key, f"invented term ref(s): {sorted(tr_terms - src_terms)}")

    # gender coverage: source message has gender forms, translation message lacks them
    tr_msgs = {k[0] for k in tr}
    tr_gender = collections.defaultdict(set)
    for (mid, attr) in tr:
        if attr in GENDER:
            tr_gender[mid].add(attr)
    for mid, forms in src_gender.items():
        if mid in tr_msgs and not (forms & tr_gender.get(mid, set())):
            add('WARN', (mid, None), f"gender forms {sorted(forms)} in source missing in translation")

    return findings, stats


def main(argv):
    as_json = '--json' in argv
    show_warn = '--warn' in argv
    pos = [a for a in argv if not a.startswith('--')]
    if len(pos) < 2:
        sys.exit(__doc__)
    findings, stats = check_pair(pos[0], pos[1])
    errors = [f for f in findings if f[0] == 'ERROR']
    warns = [f for f in findings if f[0] == 'WARN']
    if as_json:
        print(json.dumps({'stats': dict(stats),
                          'findings': [{'sev': s, 'id': i, 'attr': a, 'msg': m}
                                       for s, i, a, m in findings]}, ensure_ascii=False, indent=1))
        return len(errors)
    print(f"# {os.path.basename(pos[1])} vs {os.path.basename(pos[0])}: "
          f"translated={stats['translated']} skipped_empty={stats['skipped_empty']} "
          f"ERROR={len(errors)} WARN={len(warns)}")
    for sev, i, a, m in (errors + (warns if show_warn else [])):
        loc = f"{i}.{a}" if a else i
        print(f"  {sev:5} {loc}: {m}")
    if not show_warn and warns:
        print(f"  … {len(warns)} warnings (use --warn to list)")
    return len(errors)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
