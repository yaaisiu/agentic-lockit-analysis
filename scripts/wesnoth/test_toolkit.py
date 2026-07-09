#!/usr/bin/env python3
# scripts/wesnoth/test_toolkit.py
# source: profile wesnoth (GATE 1) — tests for the toolkit.
"""
WHY these tests look the way they do:
- **Synthetic fixtures, no lockit content.** `data/**` is gitignored (client/GPL data), so
  committed tests must never depend on it. Every unit test builds a tiny made-up PO string
  that exercises one behaviour. This keeps tests runnable on a fresh clone AND licence-clean.
- **One optional integration test** re-checks the real .pot counts, but SKIPS itself when the
  files aren't present — so CI/fresh clones stay green, while a local run re-validates reality.
Run:  pytest scripts/wesnoth/    (or: python -m pytest scripts/wesnoth/test_toolkit.py -q)
"""
import os, sys, textwrap
try:                                  # pytest optional — see __main__ runner below
    import pytest
except ImportError:                   # minimal shim so `python test_toolkit.py` also works
    class _Mark:
        def skipif(self, cond, reason=""):
            def deco(fn):
                fn.__skip__, fn.__skipreason__ = bool(cond), reason
                return fn
            return deco
    class _P:
        mark = _Mark()
    pytest = _P()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import po_parse, po_tokens, validate_markup, validate_placeholders as vph, completeness
from list_context_prefixes import family as prefix_family

HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n'
# translation header carries a Plural-Forms line (de-style: nplurals=2)
TR_HEADER = (HEADER + '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n')


def write_po(tmp_path, body, name="synthetic.pot"):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(HEADER + "\n" + textwrap.dedent(body), encoding="utf-8")
    return str(p)


def write_pair(tmp_path, src_body, tr_body):
    """Write a source .pot and a translation .po (with Plural-Forms header) → (src, tr)."""
    src = write_po(tmp_path, src_body, "dom/dom.pot")
    p = tmp_path / "dom" / "de.po"
    p.write_text(TR_HEADER + "\n" + textwrap.dedent(tr_body), encoding="utf-8")
    return src, str(p)


# ---------- po_parse ----------

def test_header_retained_and_strings_excludes_it(tmp_path):
    path = write_po(tmp_path, '''
        msgid "Hello"
        msgstr ""
    ''')
    recs = po_parse.parse_file(path)
    assert len(recs) == 2                    # header + 1 string
    assert po_parse.strings(recs)[0]["msgid"] == "Hello"
    assert recs[0]["is_header"] is True
    assert len(po_parse.strings(recs)) == 1


def test_caret_context_split(tmp_path):
    path = write_po(tmp_path, '''
        msgid "female^Ranger"
        msgstr ""
    ''')
    r = po_parse.strings(po_parse.parse_file(path))[0]
    assert r["context_prefix"] == "female"
    assert r["display"] == "Ranger"
    assert r["msgid"] == "female^Ranger"     # whole msgid kept (it's the key)


def test_multiline_msgid_concatenates(tmp_path):
    path = write_po(tmp_path, '''
        msgid ""
        "part one "
        "part two"
        msgstr ""
    ''')
    # first non-header entry has empty leading msgid then continuations
    strings = po_parse.strings(po_parse.parse_file(path))
    assert strings[0]["msgid"] == "part one part two"


def test_msgctxt_and_plural(tmp_path):
    path = write_po(tmp_path, '''
        msgctxt "menu"
        msgid "%d file"
        msgid_plural "%d files"
        msgstr[0] ""
        msgstr[1] ""
    ''')
    r = po_parse.strings(po_parse.parse_file(path))[0]
    assert r["msgctxt"] == "menu"
    assert r["msgid_plural"] == "%d files"


def test_internal_id_unique_stable_and_line_independent(tmp_path):
    a = write_po(tmp_path, '''
        msgid "Alpha"
        msgstr ""

        msgid "Beta"
        msgstr ""
    ''', "d1/a.pot")
    # same domain name 'a', same msgid, DIFFERENT line position → same internal id
    # (line is a locator, not the id). Separate subdirs so the files don't collide.
    b = write_po(tmp_path, '''
        msgid "Zeta filler line"
        msgstr ""

        msgid "Alpha"
        msgstr ""
    ''', "d2/a.pot")
    ra = {r["msgid"]: r for r in po_parse.strings(po_parse.parse_file(a))}
    rb = {r["msgid"]: r for r in po_parse.strings(po_parse.parse_file(b))}
    assert ra["Alpha"]["internal_id"] != ra["Beta"]["internal_id"]
    assert ra["Alpha"]["internal_id"] == rb["Alpha"]["internal_id"]  # stable across reorder


def test_unescape():
    assert po_parse.unescape(r"line\nbreak\ttab") == "line\nbreak\ttab"
    assert po_parse.unescape(r'quote\"end') == 'quote"end'


# ---------- po_tokens ----------

def test_token_detection():
    f = po_tokens.find(r"Ask $unit.name| for <b>help</b> &amp; wait %d min\n")
    assert "$unit.name|" in f["wml_var"]
    assert "<b>" in f["markup_tag"] and "</b>" in f["markup_tag"]
    assert "&amp;" in f["entity"]
    assert "%d" in f["printf"]
    assert r"\n" in f["escape"]


def test_angle_tokens_kinds():
    kinds = {(n, k) for _, n, k in po_tokens.angle_tokens("<span color='red'>x</span><img src='a'/>")}
    assert ("span", "open") in kinds and ("span", "close") in kinds
    assert ("img", "selfclose") in kinds


# ---------- validate_markup ----------

def test_markup_balance_and_ampersand_gating():
    assert validate_markup.check_string("<b>ok</b>") == []
    assert validate_markup.check_string("Save & Quit") == []          # plain text: & is fine
    assert any(sev == "ERROR" and ("unbalanced" in m or "unclosed" in m)
               for sev, m in validate_markup.check_string("<b>oops"))
    # '&' inside a markup string is a WARN, not a hard ERROR (decided session 001, B1)
    res = validate_markup.check_string("<b>bad & tag</b>")
    assert any(sev == "WARN" and "unescaped" in m for sev, m in res)
    assert all(sev != "ERROR" for sev, m in res)


# ---------- markup families: DocBook + po4a + brace/hex (corpus-scale extension) ----------

def test_markup_family_detection():
    assert po_tokens.markup_family("<b>x</b>") == "tag"
    assert po_tokens.markup_family("<emphasis>x</emphasis>") == "tag"
    assert po_tokens.markup_family("B<bold> I<italic>") == "po4a"
    # a po4a path: '</var/run…>' is span content, not a close tag → stays po4a
    assert po_tokens.markup_family("B</var/run/socket>") == "po4a"
    # a Pango string that happens to contain 'P<' but has a real close tag → tag
    assert po_tokens.markup_family("HP<b>10</b>") == "tag"


def test_docbook_balance():
    assert validate_markup.check_string("<emphasis>hi</emphasis>") == []
    assert validate_markup.check_string("<link>a</link> <literal>b</literal>") == []
    # pre-seeded DocBook inline tag (session 001 B4) balances too
    assert validate_markup.check_string("<guimenuitem>Load</guimenuitem>") == []
    assert any(sev == "ERROR" and ("unclosed" in m or "unbalanced" in m)
               for sev, m in validate_markup.check_string("<emphasis>oops"))
    # <imagedata …> is empty/self-closing — must NOT report as unclosed
    assert validate_markup.check_string(
        "<imageobject><imagedata fileref='a.png'/></imageobject>") == []
    assert validate_markup.check_string(
        "<imageobject><imagedata fileref='a.png'></imageobject>") == []


def test_po4a_markup_ok_and_defects():
    assert validate_markup.check_string("B<bold> and I<italic> and E<lt>x E<gt>") == []
    assert validate_markup.check_string("B</var/run/wesnothd/socket>") == []
    # missing '>' → unbalanced po4a
    assert any(sev == "ERROR" and "unbalanced po4a" in m
               for sev, m in validate_markup.check_string("B<bold and I<italic>"))
    # a bare '<' should have been E<lt>
    assert any(sev == "ERROR" and "bare '<'" in m
               for sev, m in validate_markup.check_string("E<lt> then a bare < oops"))


def test_brace_var_and_hex_entity():
    f = po_tokens.find("main={prefix}{suffix} and &#0x7B; and &#x7D; and &#38;")
    assert "{prefix}" in f["brace_var"] and "{suffix}" in f["brace_var"]
    assert "&#0x7B;" in f["entity"] and "&#x7D;" in f["entity"] and "&#38;" in f["entity"]
    # hex/0x entities must NOT be flagged as unescaped '&' inside a markup string
    assert validate_markup.check_string("<b>brace &#0x7B; here</b>") == []


def test_bare_cli_metasyntax_not_errored():
    # bare <side>/<nickname> are argument slots (metasyntax), not markup → no hard issue
    assert validate_markup.check_string("Usage: --side <side> for <nickname>") == []


def test_prefix_family_gender_agreement():
    # gender + agreement variants all land in one translation-critical family (session 001 B3)
    for p in ["female", "male", "gender", "female_speaker", "female_addressed",
              "self_female", "race+female", "friend_is_female", "friend_is_male",
              "addressed_plural", "plural", "race+plural"]:
        assert prefix_family(p) == "gender/agreement", p
    # bare 'race' is a race-name context, NOT agreement; others keep their families
    assert prefix_family("race") == "other/UI"
    assert prefix_family("prefix_kilo") == "SI number units"
    assert prefix_family("addon_state") == "add-ons"


# ---------- validate_placeholders: cross-locale (multi-language) ----------

def test_vph_invented_placeholder(tmp_path):
    src, tr = write_pair(tmp_path,
        'msgid "Gold: $gold"\nmsgstr ""\n',
        'msgid "Gold: $gold"\nmsgstr "Zloto: $glod"\n')      # $glod ∉ source
    findings, _, _ = vph.check_pair(src, tr)
    assert any("invented" in m and "$glod" in m for _, _, _, m in findings)


def test_vph_dropped_placeholder_nonplural(tmp_path):
    src, tr = write_pair(tmp_path,
        'msgid "$count/1000 tiles"\nmsgstr ""\n',
        'msgid "$count/1000 tiles"\nmsgstr "/1000 pol"\n')   # $count dropped
    findings, _, _ = vph.check_pair(src, tr)
    assert any("dropped" in m and "$count" in m for _, _, _, m in findings)


def test_vph_plural_form_may_omit_var(tmp_path):
    # the singular form legitimately has no $units_to_slay → must NOT be flagged 'dropped'
    src, tr = write_pair(tmp_path,
        'msgid "Defeat one unit"\nmsgid_plural "Defeat $units_to_slay units"\n'
        'msgstr[0] ""\nmsgstr[1] ""\n',
        'msgid "Defeat one unit"\nmsgid_plural "Defeat $units_to_slay units"\n'
        'msgstr[0] "Besiege eine"\nmsgstr[1] "Besiege $units_to_slay"\n')
    findings, _, _ = vph.check_pair(src, tr)
    assert not any(sev == "ERROR" for sev, _, _, _ in findings)


def test_vph_translation_markup_break(tmp_path):
    src, tr = write_pair(tmp_path,
        'msgid "<b>Bold</b>"\nmsgstr ""\n',
        'msgid "<b>Bold</b>"\nmsgstr "<b>Pogrubienie"\n')     # unclosed <b> in translation
    findings, _, _ = vph.check_pair(src, tr)
    assert any("markup" in m for _, _, _, m in findings)


def test_vph_nplurals_and_trailing_dot_not_a_defect(tmp_path):
    # $version. (var + sentence period) must match across locales — no invented/dropped
    src, tr = write_pair(tmp_path,
        'msgid "Running $version."\nmsgstr ""\n',
        'msgid "Running $version."\nmsgstr "Wersja $version."\n')
    findings, _, npl = vph.check_pair(src, tr)
    assert npl == 2
    assert not any(sev == "ERROR" for sev, _, _, _ in findings)


# ---------- optional integration (skips without real data) ----------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "wesnoth", "pot")


@pytest.mark.skipif(not os.path.isdir(DATA), reason="real .pot not present (gitignored)")
def test_real_counts():
    expect = {"wesnoth-lib": 1682, "wesnoth": 1468, "wesnoth-units": 878, "wesnoth-httt": 1230}
    for dom, n in expect.items():
        path = os.path.join(DATA, dom + ".pot")
        if os.path.exists(path):
            S = po_parse.strings(po_parse.parse_file(path))
            assert len(S) == n
            assert len({r["internal_id"] for r in S}) == n   # ids unique


def test_completeness_entry_state(tmp_path):
    """translated / untranslated / fuzzy / half-filled-plural classification (synthetic)."""
    po = (HEADER +
          '\nmsgid "Done"\nmsgstr "Fertig"\n'                        # translated
          '\nmsgid "Todo"\nmsgstr ""\n'                              # untranslated
          '\n#, fuzzy\nmsgid "Guess"\nmsgstr "Vermutung"\n'          # fuzzy (not done)
          '\nmsgid "one apple"\nmsgid_plural "%d apples"\n'
          'msgstr[0] "ein Apfel"\nmsgstr[1] ""\n')                   # half-filled plural → untranslated
    f = tmp_path / "d.po"; f.write_text(po, encoding="utf-8")
    recs = po_parse.strings(po_parse.parse_file(str(f)))
    states = sorted(completeness.entry_state(r) for r in recs)
    assert states == ['fuzzy', 'translated', 'untranslated', 'untranslated'], states
    total, c = completeness.report_file(str(f))
    assert total == 4 and c['translated'] == 1 and c['fuzzy'] == 1 and c['untranslated'] == 2


# ---------- dependency-free runner (used when pytest isn't installed) ----------

if __name__ == "__main__":
    import tempfile, pathlib, traceback, inspect
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    passed = failed = skipped = 0
    for name, fn in tests:
        if getattr(fn, "__skip__", False):
            print(f"SKIP {name} ({getattr(fn, '__skipreason__', '')})"); skipped += 1; continue
        try:
            if "tmp_path" in inspect.signature(fn).parameters:
                fn(pathlib.Path(tempfile.mkdtemp()))
            else:
                fn()
            print(f"PASS {name}"); passed += 1
        except Exception as e:
            print(f"FAIL {name}: {e}"); traceback.print_exc(); failed += 1
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)
