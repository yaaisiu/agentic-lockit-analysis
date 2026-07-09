#!/usr/bin/env python3
"""test_toolkit.py — dual-mode tests for the HoI4 Clausewitz toolkit.

WHY: a tool isn't real until it's run and pinned. Mode 1 = SYNTHETIC fixtures that lock the
reader's semantics on the tricky shapes (BOM, optional version, greedy first→last quote with
UNESCAPED inner quotes, empty value, malformed log-and-skip, both key styles) and the labeling
registry (known constructs, tier-1 drift, tier-2 noted tail), plus the prepared cross-locale
tools. Mode 2 = REAL-CORPUS smoke that asserts the GATE-1 census numbers on the slice and that the
drift audit is 0 on all 206 files — so a future change that silently breaks parsing/labeling is
caught. No third-party deps.

    python3 tests/test_toolkit.py            # from scripts/hoi4/
"""
import os, sys, tempfile, shutil, io, contextlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import clausewitz_parse as P
import labels as L
import extract, validate, validate_placeholders

HERE = os.path.dirname(__file__)
SLICE = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'data', 'hoi4', 'en'))
ALL206 = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'sources', 'hoi4'))

n = {'pass': 0, 'fail': 0}
def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    n['pass' if cond else 'fail'] += 1

def write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('﻿' + text)     # prepend BOM so we exercise utf-8-sig

# ── Mode 1: synthetic fixtures ────────────────────────────────────────────────
FIX = """l_english:
 PLAIN_KEY:0 "Just text"
 NO_VERSION_KEY: "No version here"
 GER_fascism: "German Reich"
 GER_fascism_DEF: "the German Reich"
 germany.4.t: "Anschluss"
 germany.4.desc: "Body text"
 germany.4.a: "Option A"
 news.214.d_not_baltic: ""There is no outcome," said the man."
 stability.37.t: ""A Somber and Sacred Duty""
 election.1.d: ""
 COLOURED:0 "§GClick§! then £pol_power $VAL|H0$ for [Root.GetName]\\nEnd"
 FLAGGED: "@GER Germany and @ITA Italy"
 this line is malformed with no quotes
 UNTERMINATED: "open quote but no close
"""

def mode1():
    print("MODE 1 — synthetic fixtures")
    d = tempfile.mkdtemp(prefix='hoi4t_')
    try:
        fp = os.path.join(d, 'fix_l_english.yml')
        write(fp, FIX)
        entries, warnings = P.parse_file(fp)
        byk = {e.key: e for e in entries}

        # --- reader semantics ---
        check("BOM stripped + header parsed (lang=english)", entries and entries[0].lang == 'english')
        check("optional version: PLAIN_KEY=0, NO_VERSION_KEY=None",
              byk['PLAIN_KEY'].version == 0 and byk['NO_VERSION_KEY'].version is None)
        check("greedy first→last quote keeps UNESCAPED inner quotes",
              byk['news.214.d_not_baltic'].value == '"There is no outcome," said the man.')
        check("double-outer-quote value keeps inner quotes",
              byk['stability.37.t'].value == '"A Somber and Sacred Duty"')
        check("genuinely empty value", byk['election.1.d'].value == '' and byk['election.1.d'].is_empty)
        check("malformed line log-and-skipped (not raised)",
              any(k == 'malformed' for _f, _l, k, _t in warnings))
        check("unterminated quote flagged multiline?",
              any(k == 'multiline?' for _f, _l, k, _t in warnings))

        # --- key styles ---
        check("underscore tag detected (GER_fascism → tag GER)", byk['GER_fascism'].tag == 'GER')
        check("dotted event key: namespace/id/part",
              byk['germany.4.t'].namespace == 'germany' and byk['germany.4.t'].event_id == '4'
              and byk['germany.4.t'].part == 't')
        check("underscore key is NOT dotted", not byk['GER_fascism'].is_dotted)

        # --- labels: known constructs ---
        toks = dict((name, tok) for name, tok in L.scan_tokens(byk['COLOURED'].value))
        check("scan_tokens finds colour/icon/variable/scope/newline",
              {'colour-open', 'colour-close', 'icon', 'variable', 'scope-fn', 'newline'} <= set(toks))
        check("split_var drops |fmt: $VAL|H0$ → ('VAL','H0')", L.split_var('$VAL|H0$') == ('VAL', 'H0'))
        check("classify_scope: [?X.Y] optional+scoped",
              L.classify_scope('?X.GetName') == {'optional': True, 'scoped': True, 'bare': False, 'fmt': None})
        check("label_part: named variant (keep_leader) → named-variant, never 'other'",
              L.label_part('keep_leader')[0] == 'named-variant')
        check("label_part: desc.<cond> is a body branch", L.label_part('desc.baltics')[0] == 'body')
        check("label_part: .tt → tooltip", L.label_part('a.tt')[0] == 'tooltip')

        # --- labels: tier-1 drift on clean fixture = 0 ---
        with contextlib.redirect_stdout(io.StringIO()):
            drift0 = L.audit(fp)
        check("clean fixture: tier-1 drift == 0", drift0 == 0)

        # --- labels: each drift probe fires on a synthetic bad value ---
        check("unknown colour letter flagged", list(L.color_letter_issues("§Zbad")) != [])
        check("other-escape (\\q) is drift", L.DRIFT_PROBES['other-escape'].search(r'a\qb') is not None)
        check("\\t is NOT drift (known escape)", L.DRIFT_PROBES['other-escape'].search(r'a\tb') is None)
        check("genuine CK3 #..#! span is drift", L.DRIFT_PROBES['newstyle-fmt'].search('#bold hi#!') is not None)
        check("bare #TODO (no #!) is NOT drift", L.DRIFT_PROBES['newstyle-fmt'].search('#TODO_X here') is None)
        check("curly {x} is drift", L.DRIFT_PROBES['curly-brace'].search('a {x} b') is not None)
        check("escaped-quote is NOTED not drift", L.NOTED_PROBES['escaped-quote'].search(r'say \"hi\"') is not None)
        check("unbalanced colour detected", L.color_unbalanced('§Yopen with no close'))

        # --- extract.clean_text strips the non-translatable set ---
        clean = extract.clean_text(byk['COLOURED'].value)
        check("clean_text strips constructs, keeps words",
              'Click' in clean and 'End' in clean and '§' not in clean and '£' not in clean
              and '$' not in clean and '[' not in clean and '\\n' not in clean)

        # --- prepared cross-locale tools ---
        en = os.path.join(d, 'en'); tr = os.path.join(d, 'tr')
        os.makedirs(en); os.makedirs(tr)
        write(os.path.join(en, 'a_l_english.yml'),
              'l_english:\n K1: "Cost $GOLD$ for [Root.GetName]"\n K2: "Short"\n')
        write(os.path.join(tr, 'a_l_polish.yml'),
              'l_polish:\n K1: "Koszt for [Root.GetName]"\n K2: "A much much much longer translation here"\n')
        with contextlib.redirect_stdout(io.StringIO()):
            defects = validate_placeholders.check(en, tr)
            flagged = validate.length_ref(en, tr, ratio=1.6)
        check("placeholder check catches DROPPED $GOLD$ (1 defect)", defects == 1)
        check("length-ref flags the long K2 translation", flagged >= 1)

        # --- reference integrity: resolved / engine / dangling classification ---
        rd = tempfile.mkdtemp(prefix='hoi4r_')
        try:
            write(os.path.join(rd, 'r_l_english.yml'),
                  'l_english:\n'
                  ' dam: "Dam"\n'
                  ' dam_alias: "$dam$"\n'                      # resolved: $dam$ → key `dam`
                  ' engine_use: "$VALUE$ men and $COUNTRY$"\n'  # engine values (ALL-CAPS)
                  ' broken: "see $totally_missing_thing$"\n')   # dangling: lowercase, no such key
            rlk = P.load(rd)
            resolved, engine, dangling = validate.classify_references(rlk)
            check("reference: $dam$ resolves to key `dam`", resolved == 1)
            check("reference: ALL-CAPS $VALUE$/$COUNTRY$ = engine values", engine == 2)
            check("reference: lowercase $totally_missing_thing$ = dangling",
                  len(dangling) == 1 and dangling[0][1] == 'totally_missing_thing')
            # event structure: an event with a title but no body
            write(os.path.join(rd, 'e_l_english.yml'),
                  'l_english:\n foo.1.t: "Title only"\n foo.2.t: "T"\n foo.2.desc: "Body"\n')
            ev = validate.event_structure(P.load(rd))
            check("event_structure: foo.1 has title, no body",
                  ev[('foo', '1')] == {'title'} and 'body' in ev[('foo', '2')])
        finally:
            shutil.rmtree(rd, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)

# ── Mode 2: real-corpus smoke ─────────────────────────────────────────────────
def mode2():
    print("\nMODE 2 — real-corpus smoke")
    if not os.path.isdir(SLICE):
        print("  -- SKIP: data/hoi4/en not present"); return
    lk = P.load(SLICE)
    check("slice: 12867 entries", len(lk.entries) == 12867)
    check("slice: 0 duplicate keys", len(lk.duplicate_keys()) == 0)
    check("slice: 0 parse warnings", len(lk.warnings) == 0)
    check("slice: key styles 9515 underscore / 3352 dotted",
          sum(1 for e in lk.entries if e.is_dotted) == 3352)
    ver = {e.version for e in lk.entries if e.version is not None}
    check("slice: version integers ⊆ {0,1,2,3,4}", ver <= {0, 1, 2, 3, 4})
    with contextlib.redirect_stdout(io.StringIO()):
        drift = L.audit(SLICE)
    check("slice: tier-1 drift == 0", drift == 0)

    if os.path.isdir(ALL206):
        with contextlib.redirect_stdout(io.StringIO()):
            drift_all = L.audit(ALL206)
        check("all 206: tier-1 drift == 0 (registry recognises whole corpus)", drift_all == 0)
        # reference integrity is only meaningful on the FULL corpus (cross-file refs)
        all_lk = P.load(ALL206)
        _res, _eng, dangling = validate.classify_references(all_lk)
        check("all 206: 40 dangling reference candidates (defect list)", len(dangling) == 40)
        ev = validate.event_structure(all_lk)
        check("all 206: 245 events missing a title",
              sum(1 for parts in ev.values() if 'title' not in parts) == 245)
    else:
        print("  -- note: sources/hoi4 not present, skipping 206-file audit")


if __name__ == '__main__':
    mode1()
    mode2()
    print(f"\n{n['pass']} passed, {n['fail']} failed")
    sys.exit(1 if n['fail'] else 0)
