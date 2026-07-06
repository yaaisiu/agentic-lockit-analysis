#!/usr/bin/env python3
"""test_toolkit.py — dual-mode tests for the Veloren Fluent toolkit.

WHY: a tool isn't real until it's run and pinned. Mode 1 = SYNTHETIC fixtures that lock the
parser's semantics (the tricky Fluent shapes: multiline w/ internal blank, col-0 selector,
attribute roles, terms, {""} empties, nested placeables). Mode 2 = REAL-CORPUS smoke that
asserts the GATE-1 census numbers so a future change that silently breaks parsing is caught.
No deps; run: python3 tests/test_toolkit.py   (from scripts/veloren/)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import ftl_parse as F
import inventory, validate, gender_pairs, labels

REAL = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'veloren', 'en')
REAL = os.path.normpath(REAL)

n = {'pass': 0, 'fail': 0}
def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    n['pass' if cond else 'fail'] += 1

FIX = '''\
# a standalone comment
buff-heal = Heal
    .desc = Gain health over time.
    .stat = { $duration ->
        [1] Restores { $str_total } point over { $duration } second.
        *[other] Restores { $str_total } points over { $duration } seconds.
    }

-server = Server

hud-free_look =
{ $toggle ->
[0] off { $key }
*[other] on
}

char-para = Line one.

    Line two after a blank.

npc-name = Guard
    .masc = Guard
    .fem = Guardess

speech =
    .a0 = Hello!
    .a1 = Hi!

frag = Bow Limbs
    .desc = {""}
'''


def test_parser():
    print("[parser — synthetic fixtures]")
    ents = F.parse_text(FIX, 'fix.ftl')
    by = {e.id: e for e in ents if e.kind != 'junk'}
    check("no junk lines", all(e.kind != 'junk' for e in ents))
    check("message + 2 attributes (desc, stat)", len(by['buff-heal'].attributes) == 2)
    check("standalone comment attached", by['buff-heal'].comment == 'a standalone comment')
    check("term parsed as kind=term", by['-server'].kind == 'term')
    check("col-0 selector captured as value", by['hud-free_look'].value.startswith('{ $toggle ->'))
    check("selector value contains default variant", '*[other]' in by['hud-free_look'].value)
    check("multiline w/ internal blank keeps both lines",
          'Line one.' in by['char-para'].value and 'Line two' in by['char-para'].value)
    check("gender attrs detected", {a for a, _ in by['npc-name'].attributes} == {'masc', 'fem'})
    check("attr_role gender", F.attr_role('fem') == 'gender' and F.attr_role('masc') == 'gender')
    check("attr_role variant", F.attr_role('a0') == 'variant' and F.attr_role('a12') == 'variant')
    check("attr_role metadata", F.attr_role('desc') == 'metadata')
    check("{\"\"} empty attribute recognised", by['frag'].attributes[0][1].strip() in F.EMPTY_VALUES)


def test_placeables():
    print("[placeables + classification]")
    check("var classified", F.classify_placeable('$name') == ('var', 'name'))
    check("selector classified", F.classify_placeable('$n -> [one] a *[other] b')[0] == 'selector')
    check("term-ref classified", F.classify_placeable('-server') == ('term-ref', '-server'))
    check("function classified", F.classify_placeable('TAIL($x)') == ('function', 'TAIL'))
    check("empty literal classified", F.classify_placeable('""') == ('literal', ''))
    check("hyphen/upper var names", F.all_variables('a { $SP } b { $gameinput-x }') == ['SP', 'gameinput-x'])
    keys = F.selector_variant_keys('{ $n -> [1] a *[other] b }')
    check("variant keys w/ default flag", keys == [('1', False), ('other', True)])


def test_translatable_units():
    print("[translatable units]")
    ents = F.parse_text(FIX, 'fix.ftl')
    tr = list(F.iter_units(ents, include_empty=False))
    allu = list(F.iter_units(ents, include_empty=True))
    check("empty {\"\"} excluded from translatable", len(allu) > len(tr))
    check("no translatable unit is empty", all(not u['empty'] for u in tr))
    roles = {u['role'] for u in tr}
    check("roles include value+gender+variant+metadata",
          {'value', 'gender', 'variant', 'metadata'} <= roles)


def test_validate():
    print("[validate — catches structural breakage]")
    bad = 'm1 = hello { $x\nm2 = { $n -> [1] a [other] b }\n'   # unbalanced + no default
    f = validate.validate_text if hasattr(validate, 'validate_text') else None
    # validate works on files/dirs; test via parse+checks directly
    ents = F.parse_text(bad, 'bad.ftl')
    u = list(F.iter_units(ents, include_empty=True))
    check("unbalanced braces detected", any(not validate.brace_balanced(x['text']) for x in u))
    findings = []
    for x in u:
        if validate.brace_balanced(x['text']):
            validate.check_placeables(x['text'], findings, x['id'])
    check("selector missing default flagged as ERROR",
          any(s == 'ERROR' and 'default' in m for s, c, m in findings))
    good = list(F.iter_units(F.parse_text(FIX, 'fix.ftl'), include_empty=True))
    gf = []
    for x in good:
        if validate.brace_balanced(x['text']):
            validate.check_placeables(x['text'], gf, x['id'])
    check("clean fixture has 0 ERRORs", not [x for x in gf if x[0] == 'ERROR'])


def test_labels():
    print("[labels — origin + unknown/drift]")
    check("desc origin=project", labels.label_attr('desc') == ('metadata', 'project', labels.label_attr('desc')[2]))
    check("fem role=gender origin=project", labels.label_attr('fem')[:2] == ('gender', 'project'))
    check("a5 role=variant origin=project", labels.label_attr('a5')[:2] == ('variant', 'project'))
    check("unknown attribute flagged", labels.label_attr('wibble')[1] == 'unknown')
    check("TAIL origin=project", labels.label_function('TAIL')[0] == 'project')
    check("NUMBER origin=fluent", labels.label_function('NUMBER')[0] == 'fluent')
    check("unknown function flagged", labels.label_function('ZORP')[0] == 'unknown')
    check("var placeable origin=fluent",
          labels.label_placeable('$x', F.classify_placeable)[1] == 'fluent')
    check("CLDR key origin=fluent", labels.label_variant_key('other')[0] == 'fluent')
    check("integer key origin=fluent", labels.label_variant_key('1')[0] == 'fluent')
    check("bad variant key flagged", labels.label_variant_key('plural')[0] == 'unknown')
    # drift: a fixture with an unknown attr + unknown function must be caught
    drift = 'm = { ZORP($x) }\n    .wibble = hi\n'
    ents = F.parse_text(drift, 'd.ftl')
    ua = [n for e in ents if e.kind != 'junk' for n, _ in e.attributes
          if labels.label_attr(n)[1] == 'unknown']
    check("audit-style catches unknown attr .wibble", 'wibble' in ua)


def test_real_corpus_drift():
    if not os.path.isdir(REAL):
        return
    print("[real corpus — drift audit clean]")
    check("no unknown constructs in en source", labels.audit(REAL) == 0)


def test_cross_locale():
    print("[cross-locale — real defects caught, false positives suppressed]")
    import tempfile, validate_placeholders as VP
    def wr(d, content):
        p = os.path.join(d, 'a.ftl')
        open(p, 'w', encoding='utf-8').write(content)
    en = tempfile.mkdtemp(); tr = tempfile.mkdtemp()
    wr(en, 'm1 = You were banned: { $reason }\n'
           'm2 = hi { $name }\n'
           'tip =\n    .a0 = Press { $key } to roll\n')
    wr(tr, 'm1 = Zostałeś zbanowany.\n'                                   # drops $reason (real)
           'm2 =\n    { $user_gender ->\n        [m] cześć { $name }\n        *[o] cześć { $name }\n    }\n'  # adds engine var (ok)
           'tip =\n    .a0 = Naciśnij coś\n')                              # variant .aN drops $key (skip)
    findings, _ = VP.check_pair(en, tr)
    msgs = ' '.join(m for s, i, a, m in findings if s == 'ERROR')
    check("real dropped $reason flagged as ERROR", 'reason' in msgs)
    check("engine var $user_gender NOT flagged invented", 'user_gender' not in msgs)
    check("variant .aN dropped $key NOT flagged (unsound index match)", 'key' not in msgs)


def test_real_corpus():
    if not os.path.isdir(REAL):
        print(f"[real corpus] SKIP — {REAL} not present"); return
    print("[real corpus — GATE-1 census pins]")
    ents, _ = F.parse_tree(REAL)
    msgs = [e for e in ents if e.kind == 'message']
    ids = [e.id for e in msgs]
    check("4241 messages", len(msgs) == 4241)
    check("0 id collisions", len(ids) == len(set(ids)))
    check("2 terms", sum(1 for e in ents if e.kind == 'term') == 2)
    check("3312 attributes", sum(len(e.attributes) for e in ents if e.kind != 'junk') == 3312)
    check("0 junk", not [e for e in ents if e.kind == 'junk'])
    roles = {}
    for e in ents:
        for a, _ in getattr(e, 'attributes', []):
            roles[F.attr_role(a)] = roles.get(F.attr_role(a), 0) + 1
    check("gender attrs == 616", roles.get('gender') == 616)
    check("variant attrs == 485", roles.get('variant') == 485)
    check("validate: 0 structural ERRORs on source", len(validate.validate(REAL)) >= 0
          and not [f for f in validate.validate(REAL) if f[0] == 'ERROR'])
    g = gender_pairs.collect(REAL)
    check("gender_pairs finds gendered messages", len(g) > 100)


if __name__ == '__main__':
    test_parser(); test_placeables(); test_translatable_units(); test_validate()
    test_labels(); test_cross_locale(); test_real_corpus()
    print("\n--- drift audit (labels) ---"); test_real_corpus_drift()
    print(f"\n{n['pass']} passed, {n['fail']} failed")
    sys.exit(1 if n['fail'] else 0)
