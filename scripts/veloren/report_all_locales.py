#!/usr/bin/env python3
"""report_all_locales.py — corpus-wide TECHNICAL-defect sweep across every translation.

WHY: the cross-locale checker (validate_placeholders.py) proves out on one locale; this runs
it over ALL of them and aggregates into one report of the *pure technical* mistakes — the
mechanical, game-breaking, human-invisible ones our toolkit is built to catch (dropped /
invented { $vars }, unbalanced braces, dropped selectors, missing gender forms). It does NOT
judge translation quality — only structure that must survive translation
([[cross-locale-invariants]]). We SURFACE; on GPL upstream data we never fix.

Deterministic, dependency-free. Reads translations read-only from wherever you point it.

Usage:
  python3 report_all_locales.py <source-dir> <locales-root> <out.md>
  e.g. python3 report_all_locales.py ../../data/veloren/en \\
                 ../../sources/veloren/assets/voxygen/i18n ../../data/veloren/technical-defects.md
"""
import sys, os, glob, collections
import validate_placeholders as V

CATS = [  # (label, severity, substring test)
    ('dropped-variable',   'ERROR', lambda m: 'dropped variable' in m),
    ('invented-variable',  'ERROR', lambda m: 'invented variable' in m),
    ('unbalanced-braces',  'ERROR', lambda m: 'unbalanced' in m),
    ('dropped-selector',   'WARN',  lambda m: 'selector' in m and 'dropped it' in m),
    ('invented-term',      'WARN',  lambda m: 'invented term' in m),
    ('missing-gender',     'WARN',  lambda m: 'gender forms' in m),
    ('orphan-id',          'WARN',  lambda m: 'orphan' in m),
]

def categorise(msg):
    for label, sev, test in CATS:
        if test(msg):
            return label, sev
    return 'other', 'WARN'


def main(src, root, out):
    locales = sorted(d for d in os.listdir(root)
                     if os.path.isdir(os.path.join(root, d)) and d != 'en')
    per_locale = {}
    all_errors = []                              # (locale, id, attr, cat, msg)
    cat_totals = collections.Counter()
    for loc in locales:
        findings, stats = V.check_pair(src, os.path.join(root, loc))
        c = collections.Counter()
        for sev, i, a, m in findings:
            cat, _ = categorise(m)
            c[cat] += 1; cat_totals[cat] += 1
            if sev == 'ERROR':
                all_errors.append((loc, i, a, cat, m))
        per_locale[loc] = {'translated': stats['translated'],
                           'errors': sum(1 for f in findings if f[0] == 'ERROR'),
                           'warns': sum(1 for f in findings if f[0] == 'WARN'),
                           'cats': c}

    lines = []
    def w(s=''): lines.append(s)
    w("# Veloren — cross-locale TECHNICAL-defect report")
    w()
    w("Source: English `.ftl` · Tool: `validate_placeholders.py` over all locales · session 002.")
    w("**Technical mistakes only** (structure that must survive translation) — not quality.")
    w("We surface; upstream GPL data is never edited here. See [[cross-locale-invariants]].")
    w()
    tot_err = sum(p['errors'] for p in per_locale.values())
    tot_warn = sum(p['warns'] for p in per_locale.values())
    w(f"## Summary — {len(locales)} locales · **{tot_err} ERRORs** · {tot_warn} WARNs")
    w()
    w("| defect type | severity | count |")
    w("|---|---|---|")
    for label, sev, _ in CATS:
        if cat_totals[label]:
            w(f"| {label} | {sev} | {cat_totals[label]} |")
    w()
    w("## ERRORs (hard technical defects — dropped/invented vars, broken braces)")
    if not all_errors:
        w("_none_")
    else:
        w("| locale | message id | detail |")
        w("|---|---|---|")
        for loc, i, a, cat, m in sorted(all_errors):
            key = f"`{i}" + (f".{a}" if a else "") + "`"
            w(f"| {loc} | {key} | {m} |")
    w()
    w("### About the WARNs (review-level, not hard breakage)")
    w("- **orphan-id** — a key in the translation with no match in the current source. Almost")
    w("  always **version skew** (the translation lags/leads the English source), not a defect.")
    w("- **dropped-selector** — the source had a plural `{ -> }` the translation didn't branch;")
    w("  often legitimate for languages that don't need that distinction. Review, don't assume.")
    w("- **missing-gender** — source message has `.fem/.masc/.neut` the translation lacks; may be")
    w("  intentional or an agreement gap (high-value to check for Polish).")
    w("Engine-supplied agreement vars (`*_gender`) and `.aN` variant-array index mismatches are")
    w("intentionally NOT flagged (legitimate divergence — see [[cross-locale-invariants]]).")
    w()
    w("## Per-locale (sorted by ERRORs, then WARNs)")
    w()
    w("| locale | translated units | ERRORs | WARNs | top defect types |")
    w("|---|---|---|---|---|")
    for loc in sorted(per_locale, key=lambda L: (-per_locale[L]['errors'], -per_locale[L]['warns'])):
        p = per_locale[loc]
        top = ', '.join(f"{k}×{v}" for k, v in p['cats'].most_common(3))
        w(f"| {loc} | {p['translated']} | {p['errors']} | {p['warns']} | {top} |")
    w()

    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    # terminal summary
    print(f"swept {len(locales)} locales -> {out}")
    print(f"TOTAL: {tot_err} ERRORs, {tot_warn} WARNs")
    print("by type:", dict(cat_totals))
    print("\nlocales with ERRORs:")
    for loc in sorted(per_locale, key=lambda L: -per_locale[L]['errors']):
        if per_locale[loc]['errors']:
            print(f"  {loc:8} {per_locale[loc]['errors']} error(s)")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
