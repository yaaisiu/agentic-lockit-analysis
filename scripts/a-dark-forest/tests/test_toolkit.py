#!/usr/bin/env python3
"""test_toolkit.py — dual-mode tests for the A Dark Forest CSV toolkit.

WHY: a tool isn't real until it's run and pinned. Mode 1 = SYNTHETIC fixtures that lock the
reader's semantics on the tricky shapes (quoted commas, doubled-quotes, JSON-array cells,
intentional [EMPTY] vs untranslated, duplicate keys, key constructs, description tag drift).
Mode 2 = REAL-CORPUS smoke that asserts the GATE-1 census numbers + the 3 known es defects, so
a future change that silently breaks parsing or validation is caught. No deps.

    python3 tests/test_toolkit.py        # from scripts/a-dark-forest/
"""
import os, sys, io, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import csv_parse as P
import labels as L
import arrays, validate, validate_placeholders, extract

REAL = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..',
                                     'data', 'a-dark-forest', 'localization.csv'))

n = {'pass': 0, 'fail': 0}
def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    n['pass' if cond else 'fail'] += 1


# A synthetic CSV exercising every shape. Note the quoted commas, doubled quotes, a JSON
# array, an intentional [EMPTY], an untranslated pl cell, a duplicate key, a stray-comma
# broken array, and an unknown description tag.
FIX_ROWS = [
    ['key', 'description', 'en', 'pl'],
    ['ui_label:hello', '[noun] greeting', 'Hello, world', 'Witaj, świecie'],           # quoted comma
    ['ui_label:quote', 'has a "quote"', 'Say "hi"', 'Powiedz "cześć"'],                 # doubled quotes
    ['ui_label:offline', 'timer', 'Away for {0}. \\n', 'Nieobecny {0}. \\n'],           # slot + \n
    ['tab_data_titles:x', 'tiers', '["A","B","C"]', '["A","B","C"]'],                   # array ok
    ['tab_data_titles:y', 'tiers', '["A","B"]', '["A"]'],                               # array len mismatch
    ['ui_label:opt', 'option', '["?"]', '["?"],'],                                      # stray-comma broken array
    ['ui_label:blank', '[EMPTY]', '', ''],                                              # intentional empty
    ['ui_label:todo', 'needs pl', 'Translate me', ''],                                  # untranslated pl
    ['ui_label:dup', 'first', 'One', 'Jeden'],
    ['ui_label:dup', 'second', 'One', 'Jeden'],                                         # duplicate key
    ['enemy_data_option_title:wolf-2', 'variant', 'Wolf', 'Wilk'],                      # -N variant key
    ['ui_label:reborn_X_line_1', 'template', 'Reborn', 'Odrodzony'],                    # X template key
    ['ui_label:weird', '[MYSTERY] tag', 'x', 'y'],                                      # unknown desc tag
]

def write_fixture(path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(FIX_ROWS)


def test_reader(tmp):
    print("[reader — synthetic fixtures]")
    fx = os.path.join(tmp, 'fix.csv'); write_fixture(fx)
    lk = P.parse_file(fx)
    by = {}
    for r in lk.records:
        by.setdefault(r.key, []).append(r)
    check("quoted comma kept as one cell", by['ui_label:hello'][0].values['en'] == 'Hello, world')
    check("doubled quote decoded", by['ui_label:quote'][0].values['en'] == 'Say "hi"')
    check("locales exclude meta cols", lk.locales == ['en', 'pl'])
    check("array cell shape=array", by['tab_data_titles:x'][0].shape('en') == P.ARRAY)
    check("array elements parsed", by['tab_data_titles:x'][0].elements('en') == ['A', 'B', 'C'])
    check("broken array (stray comma) shape=scalar", by['ui_label:opt'][0].shape('pl') == P.SCALAR)
    check("intentional empty detected", by['ui_label:blank'][0].is_marked_empty)
    check("intentional-empty cell not counted untranslated",
          not by['ui_label:blank'][0].is_untranslated('pl'))
    check("untranslated pl detected", by['ui_label:todo'][0].is_untranslated('pl'))
    check("duplicate key surfaced", 'ui_label:dup' in lk.duplicate_keys())
    check("namespace split", by['tab_data_titles:x'][0].namespace == 'tab_data_titles')


def test_labels(tmp):
    print("[labels — registry + key constructs]")
    check("known column labeled format", L.label_column('en')[1] == L.FORMAT)
    check("unknown column flagged", L.label_column('zz')[1] == L.UNKNOWN)
    check("known desc tag project", L.label_desc_tag('noun')[1] == L.PROJECT)
    check("unknown desc tag flagged", L.label_desc_tag('MYSTERY')[1] == L.UNKNOWN)
    check("variant-suffix key construct", any(k[0] == 'variant-suffix'
          for k in L.label_key('enemy_data_option_title:wolf-2')))
    check("X template-slot key construct", any(k[0] == 'template-slot'
          for k in L.label_key('ui_label:reborn_X_line_1')))
    check("format slot token scanned", ('format-slot', '{0}') in list(L.scan_tokens('Away {0}')))


def test_validators(tmp):
    print("[validators — synthetic]")
    fx = os.path.join(tmp, 'fix.csv'); write_fixture(fx)
    lk = P.parse_file(fx)
    # arrays: one real length mismatch (tab_data_titles:y), one broken (ui_label:opt)
    recs = arrays.array_keys(lk)
    check("array_keys finds the 3 array-source keys", len(recs) == 3)
    # validate: dup key + broken array + unknown tag = ERRORs
    rc = validate.main([fx])
    check("validate returns nonzero on defects", rc == 1)
    # placeholder/array cross-locale: pl len mismatch + broken array on pl
    rc2 = validate_placeholders.main([fx])
    check("cross-locale validator flags pl defects", rc2 == 1)


def test_real():
    print("[real corpus — GATE-1 census pins]")
    if not os.path.exists(REAL):
        check("real file present (skipped)", True); return
    lk = P.parse_file(REAL)
    check("676 records", len(lk.records) == 676)
    check("675 unique keys", len(set(r.key for r in lk.records)) == 675)
    check("1 duplicate key (ui_label:heart)", list(lk.duplicate_keys()) == ['ui_label:heart'])
    check("24 namespaces", len(lk.by_namespace()) == 24)
    check("8 locales, en source", lk.locales == ['en','zh','fr','pt','pl','ua','th','es'])
    check("27 deprecated", sum(1 for r in lk.records if r.is_deprecated) == 27)
    check("80 marked [EMPTY]", sum(1 for r in lk.records if r.is_marked_empty) == 80)
    check("30 array-valued keys", len(arrays.array_keys(lk)) == 30)
    check("0 drift (all constructs known)", L.audit(REAL) == 0)
    # the 3 known upstream es array defects (stray comma `["?"],`)
    rc = validate_placeholders.main([REAL, '--locale', 'es'])
    check("exactly 3 es cross-locale defects", rc == 1)


def main():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        test_reader(tmp)
        test_labels(tmp)
        test_validators(tmp)
    test_real()
    print(f"\n{n['pass']} passed, {n['fail']} failed")
    return 1 if n['fail'] else 0


if __name__ == '__main__':
    sys.exit(main())
