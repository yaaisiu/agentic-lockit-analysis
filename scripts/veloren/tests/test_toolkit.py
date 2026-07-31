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
### Fixture resource comment.
### Second line of the same block.

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

## Dialogue

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
    check("### resource marker becomes the section",
          by['buff-heal'].section == 'Fixture resource comment.\nSecond line of the same block.')
    check("consecutive marker lines join into ONE section",
          '\n' in by['buff-heal'].section)
    check("a later ## marker replaces the section", by['npc-name'].section == 'Dialogue')
    check("section does not leak into the value or the comment",
          'Dialogue' not in by['npc-name'].value and by['npc-name'].comment is None)
    check("a '#' comment still attaches independently of the section",
          by['buff-heal'].comment == 'a standalone comment')


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


def test_placeable_spans():
    """The (start, end, inner) contract. WHY: the bundle exporter anchors every placeholder
    to source_text[start:end], so an offset that is off by one — or a scanner that invents a
    span for an unterminated brace — corrupts a stored annotation, silently."""
    print("[placeables — spans (bundle contract)]")
    check("span + inner returned", F.placeables('a { $x } b') == [(2, 8, '$x')])
    t = 'x { $x } y'
    s, e, inner = F.placeables(t)[0]
    check("slice is the VERBATIM token incl. braces", t[s:e] == '{ $x }')
    check("the strip trap: '{'+inner+'}' != the slice", '{' + inner + '}' != t[s:e])
    check("inner is still the stripped str (call sites unpack)",
          isinstance(F.placeables('{ $x }')[0][2], str))
    check("{\"\"} span covers all 4 chars", F.placeables('{""}') == [(0, 4, '""')])
    check("unterminated placeable is NOT emitted", F.placeables('hi { $x') == [])
    nested = '{ $toggle -> [0] off { $key } *[other] on }'
    sp = F.placeables(nested)
    check("nested selector yields exactly 1 top-level span", len(sp) == 1)
    check("that span covers the whole selector", (sp[0][0], sp[0][1]) == (0, len(nested)))
    multi = 'a { $x } b { -term } c'
    sp = F.placeables(multi)
    check("multiple spans ascending + non-overlapping",
          [x[0] for x in sp] == sorted(x[0] for x in sp) and sp[0][1] <= sp[1][0])
    check("every span re-slices to a brace-delimited token",
          all(multi[a:b][0] == '{' and multi[a:b][-1] == '}' for a, b, _ in sp))


def test_placeable_tokens():
    """The 0.3.0 containment model. WHY: a placeholder span is a MASK, so the rule is
    semantic — a span must never contain translatable text — and the form worth testing is
    its equivalent: THE COMPLEMENT OF THE SPANS IS EXACTLY THE TRANSLATABLE TEXT. Under the
    old one-span-per-construct model a selector masked its own variant bodies, deleting real
    prose from the reviewable corpus with nothing to flag it."""
    print("[placeable tokens — selector flattening (contract 0.3.0)]")
    import export_bundle as EB
    t = '{ $n ->\n[1] one apple\n*[other] { $n } apples\n}'
    toks = F.placeable_tokens(t)
    kinds = [s for _a, _b, s, _p in toks]
    check("selector flattens: head + 2 keys + closer + the var inside a body",
          kinds == ['selector-head', 'selector-key', 'selector-key', 'placeable',
                    'selector-close'])
    check("tokens are in ascending start order",
          [a for a, _b, _s, _p in toks] == sorted(a for a, _b, _s, _p in toks))
    check("head token is the syntax only, payload = the switched variable",
          (t[toks[0][0]:toks[0][1]], toks[0][3]) == ('{ $n ->', 'n'))
    check("variant key token INCLUDES the '*' of the default",
          (t[toks[2][0]:toks[2][1]], toks[2][3]) == ('*[other]', 'other'))
    check("closer is the bare '}'", t[toks[4][0]:toks[4][1]] == '}')
    check("NO token is the whole construct any more (the 0.2.0 shape is gone)",
          not any(a == 0 and b == len(t) for a, b, _s, _p in toks))
    # the operational invariant, run as an operation
    phs = [{'start': a, 'end': b, 'kind': 'selector'} for a, b, _s, _p in toks]
    comp = ''.join(c for _a, _b, c in EB.complement(t, phs))
    check("complement holds the prose", 'one apple' in comp and 'apples' in comp)
    check("complement holds NO Fluent syntax",
          not EB.complement_syntax(t, [dict(p, token='') for p in phs]))

    # THE case that raises no flag: a selector in the MIDDLE of a sentence. The unit is not
    # fully masked, so no coverage metric fires — yet 'only one' sits inside the mask.
    mid = 'Gave { $n ->\n[1] only one\n*[other] { $n }\n} of { $t } items.'
    comp = ''.join(c for _a, _b, c in EB.complement(
        mid, [{'start': a, 'end': b} for a, b, _s, _p in F.placeable_tokens(mid)]))
    check("mid-sentence selector: 'only one' survives into the complement", 'only one' in comp)
    check("mid-sentence selector: the sentence around it survives too",
          'Gave ' in comp and ' of ' in comp and ' items.' in comp)

    # nesting is handled by recursion, not by a containment hierarchy
    nest = '{ $a ->\n[one] x { $b ->\n[one] y\n*[other] z\n}\n*[other] w\n}'
    ntoks = F.placeable_tokens(nest)
    check("a selector nested in a variant body is flattened too, to any depth",
          [s for _a, _b, s, _p in ntoks].count('selector-head') == 2)
    check("nested tokens still never overlap",
          all(ntoks[i][1] <= ntoks[i + 1][0] for i in range(len(ntoks) - 1)))
    check("nested prose stays exposed",
          all(w in ''.join(c for _a, _b, c in EB.complement(
              nest, [{'start': a, 'end': b} for a, b, _s, _p in ntoks]))
              for w in ('x ', 'y', 'z', 'w')))

    # a literal bracket in prose is NOT a variant key: Fluent requires a line end before one
    lit = '{ $n ->\n[one] press [F] now\n*[other] press [F] now\n}'
    keytoks = [lit[a:b] for a, b, s, _p in F.placeable_tokens(lit) if s == 'selector-key']
    check("'[F]' mid-line is prose, not a variant key", keytoks == ['[one]', '*[other]'])
    check("non-selectors are untouched by flattening",
          F.placeable_tokens('a { $x } b { -t }') ==
          [(2, 8, 'placeable', '$x'), (11, 17, 'placeable', '-t')])


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
    check("selector head labeled kind=selector origin=fluent",
          labels.label_selector_piece('selector-head', 'n')[:3] == ('selector', 'fluent', 'n'))
    check("selector closer carries no detail",
          labels.label_selector_piece('selector-close', None)[:3] == ('selector', 'fluent', ''))
    check("a variant key still defers to the registry (CLDR -> fluent)",
          labels.label_selector_piece('selector-key', 'other')[:3] == ('selector', 'fluent', 'other'))
    check("an unrecognised variant key stays DRIFT even as selector syntax",
          labels.label_selector_piece('selector-key', 'plural')[1] == 'unknown')
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


def test_export_bundle():
    """The bundle contract. WHY: source_text is NORMATIVE — every stored annotation is an
    offset into it — so the two things that must never drift silently are the identity
    (a pure function of native_ref, not of line numbers) and the payload bytes."""
    print("[export bundle — contract + byte stability]")
    import tempfile, export_bundle as EB
    d = tempfile.mkdtemp()
    open(os.path.join(d, 'fix.ftl'), 'w', encoding='utf-8').write(FIX)
    rows, per_file, stats, kinds, origins, problems, root = EB.build_rows(d)
    files = EB.build_files_index(d, root, per_file)
    check("build: 0 span/inner disagreements", not problems)
    check("self-check clean on the fixture", not EB.verify_rows(rows, files))
    check("container message with no value is not a row",
          all(r['source_text'] != '' for r in rows))
    check("{\"\"} row is empty:true with a literal placeholder",
          any(r.get('empty') and r['placeholders'][0]['kind'] == 'literal' for r in rows))
    ctx = [r['context'] for r in rows if 'context' in r]
    check("context is an OBJECT, never a bare string", all(isinstance(c, dict) for c in ctx))
    check("context carries the section", any(c.get('section') == 'Dialogue' for c in ctx))
    check("context carries the comment too", any('comment' in c for c in ctx))
    check("context keys stay inside the producer's vocabulary",
          all(set(c) <= {'comment', 'section'} for c in ctx))
    check("origin is mapped to the contract enum (fluent -> spec)",
          all(p['origin'] in EB.ORIGINS for r in rows for p in r['placeholders']))
    check("TAIL-style project origin survives the map", EB.ORIGIN_MAP['project'] == 'project')
    check("unknown origin passes through UNCHANGED", EB.ORIGIN_MAP['unknown'] == 'unknown')
    # identity purity: shifting every line must not move a single line_id
    d2 = tempfile.mkdtemp()
    open(os.path.join(d2, 'fix.ftl'), 'w', encoding='utf-8').write('\n\n\n' + FIX)
    rows2 = EB.build_rows(d2)[0]
    check("line_id is a pure function of native_ref (line shift changes nothing)",
          [r['line_id'] for r in rows] == [r['line_id'] for r in rows2])
    check("...and line_no DID move (so the test is not vacuous)",
          [r['line_no'] for r in rows] != [r['line_no'] for r in rows2])
    check("line_id unique", len({r['line_id'] for r in rows}) == len(rows))
    payload = EB.serialize(rows)
    check("payload: LF only, no BOM, exactly one trailing newline",
          not EB.verify_payload_bytes(payload))
    check("payload is byte-stable across two serialisations", EB.serialize(rows) == payload)
    check("payload has no literal newline inside a row",
          len(payload.split(b'\n')) - 1 == len(rows))

    if not os.path.isdir(REAL):
        return
    print("[export bundle — real-corpus pins]")
    rows, per_file, stats, kinds, origins, problems, root = EB.build_rows(REAL)
    files = EB.build_files_index(REAL, root, per_file)
    check("7131 rows (6359 non-empty + 772 blank)", len(rows) == 7131 and stats['empty'] == 772)
    check("424 container messages skipped", stats['skipped_absent_value'] == 424)
    check("48 files in the inventory", len(files) == 48)
    # 1411 = the 1267 constructs of the 0.2.0 model, minus nothing, plus 79 selector syntax
    # pieces (26 heads + 53 keys + 26 closers, less the 26 whole-construct spans they replace)
    # plus 65 vars that were previously BURIED inside a selector mask and are now visible.
    check("1411 placeholder tokens", stats['placeholders'] == 1411)
    check("kinds pinned (selector 26 constructs -> 105 syntax tokens; var 454 -> 519)",
          dict(kinds) == {'var': 519, 'selector': 105, 'term-ref': 13,
                          'function': 1, 'literal': 773})
    check("origins pinned (1410 spec + 1 project)", dict(origins) == {'spec': 1410, 'project': 1})
    check("0 drift: no unknown origin, no role=other",
          stats['unknown_origin'] == 0 and stats['role_other'] == 0)
    # Was (772, 24) under 0.2.0. The 23 that left were never really fully masked — a selector
    # merely happened to span their whole value. Note this metric ALSO missed every partial
    # case, which is why complement_syntax, not this counter, is the invariant we enforce.
    check("entirely one placeable: 772 empty + 1 non-empty (was 24 under 0.2.0)",
          (stats['fully_masked_empty'], stats['fully_masked_nonempty']) == (772, 1))
    check("real corpus self-check clean", not EB.verify_rows(rows, files))
    check("no unit leaks Fluent syntax into its complement",
          not [x for r in rows for x in EB.complement_syntax(r['source_text'], r['placeholders'])])
    check("3979 rows carry a section, 11 a comment",
          stats['with_section'] == 3979 and stats['with_comment'] == 11)
    # TWO pins, deliberately separate. source_text is the NORMATIVE string every stored
    # annotation is an offset into; the payload additionally carries the placeholder model.
    # Splitting them is what makes "re-pin deliberately, never reflexively" checkable: a
    # contract change moves the payload hash ALONE, and the source_text hash standing still
    # is the proof that no annotation re-anchored. If both move, a parser edit came along
    # for the ride — stop and find out which.
    sha = __import__('hashlib').sha256
    check("source_text corpus sha256 pinned (UNCHANGED across the 0.2.0 -> 0.3.0 bump)",
          sha(''.join(r['source_text'] + '\x1e' for r in rows).encode('utf-8')).hexdigest() ==
          'd3df6b67ef81eb0718f4de7223e7993e4fa8c8b5968bc1f059a8729c4ad2b1e9')
    check("payload sha256 pinned (moved WITH the 0.3.0 placeholder model, by intent)",
          sha(EB.serialize(rows)).hexdigest() ==
          '3196a0557ebbf7b651694d3b4b45a3a074e89f05dddfdd5456a08572bdc0d7a0')
    check("bundle_version declares 0.3.0 — the only discriminator a consumer has",
          EB.BUNDLE_VERSION == '0.3.0')


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
    test_parser(); test_placeables(); test_placeable_spans(); test_placeable_tokens()
    test_translatable_units(); test_validate()
    test_labels(); test_cross_locale(); test_export_bundle(); test_real_corpus()
    print("\n--- drift audit (labels) ---"); test_real_corpus_drift()
    print(f"\n{n['pass']} passed, {n['fail']} failed")
    sys.exit(1 if n['fail'] else 0)
