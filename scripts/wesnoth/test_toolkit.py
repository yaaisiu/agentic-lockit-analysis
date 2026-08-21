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
import os, sys, json, textwrap
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


# ---------- export_bundle (the BILINGUAL bundle contract) ----------
# WHY these tests exist at all: the bundle's `segment_id` is a JOIN KEY. A wrong id does not
# crash anything — it produces a bundle that validates, looks right, and matches nothing on
# the other side. So identity is pinned by VECTORS computed independently of this repository,
# and stability is pinned by mutating everything the id must NOT depend on.
import export_bundle as EB

PO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                       "sources", "wesnoth", "po")

# Computed outside this repository. If one of these moves, the id function moved, and every
# bundle ever exported has been orphaned — that is the failure this table is here to catch.
ID_VECTORS = [
    ("wesnoth-httt", None, "Konrad",                                   "wesnoth-httt:53bdcea5c81e"),
    ("wesnoth-lib",  None, "Save Game",                                "wesnoth-lib:2ce0248a1bf6"),
    ("wesnoth",      None, "female^Elvish Sorceress",                  "wesnoth:74e03e832707"),
    ("wesnoth-httt", None, "You retrieve $amount_gold pieces of gold.", "wesnoth-httt:e6439148218a"),
]


def test_segment_id_vectors():
    for domain, ctx, msgid, expected in ID_VECTORS:
        got = EB.segment_id(domain, ctx, msgid)
        assert got == expected, f"{domain}/{msgid!r}: {got} != {expected}"
        assert len(got.split(":", 1)[1]) == 12
        assert got.split(":", 1)[1] == got.split(":", 1)[1].lower()


def test_segment_id_is_not_internal_id():
    """po_parse mints an id of the SAME SHAPE and a DIFFERENT value (10 chars, domain and
    plural hashed in behind 0x1f). Reusing it is the failure mode this whole test guards."""
    internal = po_parse._internal_id("wesnoth-httt", None, "Konrad", None)
    assert internal != EB.segment_id("wesnoth-httt", None, "Konrad")
    assert len(internal.split(":", 1)[1]) == 10


def test_segment_id_ignores_line_number_and_plural(tmp_path):
    """Shift every entry's line number and give one entry a msgid_plural: no id may move."""
    body = '\nmsgid "Alpha"\nmsgstr "A"\n\nmsgid "Beta"\nmsgstr "B"\n'
    a = tmp_path / "d1" / "pl.po"; a.parent.mkdir(parents=True)
    a.write_text(TR_HEADER + body, encoding="utf-8")
    shifted = ("# pad\n" * 7) + TR_HEADER + "\n\n\n" + body.replace(
        'msgid "Beta"\nmsgstr "B"',
        'msgid "Beta"\nmsgid_plural "Betas"\nmsgstr[0] "B"\nmsgstr[1] "Bs"')
    b = tmp_path / "d2" / "pl.po"; b.parent.mkdir(parents=True)
    b.write_text(shifted, encoding="utf-8")

    def ids(path):
        return [EB.segment_id("dom", r["msgctxt"], r["msgid"])
                for r in po_parse.strings(po_parse.parse_file(str(path), "dom"))]
    assert ids(a) == ids(b)


def _fixture_corpus(tmp_path):
    """A two-domain synthetic corpus with the shape the exporter expects. No lockit content:
    every string here is invented, so this runs licence-clean on a fresh clone."""
    src = ('msgid "Konrad"\nmsgstr "Konrad"\n\n'
           'msgid "female^Sorceress"\nmsgstr "Czarodziejka"\n\n'
           'msgid "Gold: $gold"\nmsgstr "Zloto: $glod"\n\n'
           'msgid "Nothing here"\nmsgstr ""\n\n'
           '#, fuzzy\nmsgid "Maybe"\nmsgstr "Moze"\n\n'
           'msgid "Line one\\nLine two"\nmsgstr "Wiersz\\njeden"\n\n'
           'msgid "one orc"\nmsgid_plural "$count orcs"\n'
           'msgstr[0] "ork"\nmsgstr[1] "$count orki"\nmsgstr[2] "$count orkow"\n')
    pot = ('msgid "Konrad"\nmsgstr ""\n')
    for dom in ("wesnoth-lib", "wesnoth-units"):
        d = tmp_path / dom
        d.mkdir(parents=True, exist_ok=True)
        (d / (dom + ".pot")).write_text(HEADER + "\n" + pot, encoding="utf-8")
        (d / "pl.po").write_text(
            HEADER.replace('"Content-Type', '"PO-Revision-Date: 2026-01-01 00:00+0000\\n"\n"Plural-Forms: nplurals=3; plural=(n==1 ? 0 : 2);\\n"\n"Content-Type')
            + "\n" + src, encoding="utf-8")
    return str(tmp_path)


def test_export_rows_contract(tmp_path):
    root = _fixture_corpus(tmp_path)
    domains, missing = EB.corpus_inventory(root, "pl")
    assert domains == ["wesnoth-lib", "wesnoth-units"] and missing == []
    assert EB.structural_problems(root, "pl", domains) == []
    rows, stats, census, dates = EB.build_rows(root, "pl", domains)

    assert len(rows) == 14 and stats["rows"] == 14
    assert EB.verify_rows(rows) == []                       # the self-checks are the contract
    assert [r["seq"] for r in rows] == list(range(14))      # dense, 0-based, global
    assert dates == {"wesnoth-lib": "2026-01-01 00:00+0000",
                     "wesnoth-units": "2026-01-01 00:00+0000"}

    by = {r["source_en"]: r for r in rows if r["textdomain"] == "wesnoth-lib"}
    # caret prefix surfaces as a DERIVED msgctxt while source_en keeps the whole raw msgid
    assert by["female^Sorceress"]["msgctxt"] == "female"
    assert by["female^Sorceress"]["string_class"] == "ui/gender_agreement"
    assert by["Konrad"]["msgctxt"] is None and by["Konrad"]["string_class"] == "ui/plain"
    # …and the id is over the RAW msgid, prefix included, with the RAW msgctxt (None)
    assert by["female^Sorceress"]["segment_id"] == EB.segment_id(
        "wesnoth-lib", None, "female^Sorceress")

    # target_pl is null, never "", when untranslated; display tracks null exactly
    assert by["Nothing here"]["target_pl"] is None
    assert by["Nothing here"]["target_pl_display"] is None
    assert by["Nothing here"]["pool"] == "untranslated"
    # fuzzy keeps its text but is NOT eval, and `fuzzy` survives as its own boolean
    assert by["Maybe"]["fuzzy"] is True and by["Maybe"]["pool"] == "untranslated"
    assert by["Maybe"]["target_pl"] == "Moze"
    assert by["Konrad"]["pool"] == "eval" and by["Konrad"]["fuzzy"] is False

    # placeholder_check is a VERDICT, never a refusal
    assert by["Gold: $gold"]["placeholder_check"] == "mismatch"
    assert by["Gold: $gold"]["placeholders"] == ["$gold"]
    assert by["Konrad"]["placeholder_check"] == "not_applicable"

    # plural: one row, both sides, nplurals from the HEADER not from len()
    pf = by["one orc"]["plural_forms"]
    assert pf["source_plural"] == "$count orcs" and pf["target_nplurals"] == 3
    assert len(pf["target_forms"]) == len(pf["target_forms_display"]) == 3
    assert by["one orc"]["target_pl"] == "ork"        # singular pair stays coherent
    assert by["Konrad"]["plural_forms"] is None

    # neighbours never cross a file boundary
    assert rows[0]["neighbours"]["prev"] is None
    assert rows[6]["neighbours"]["next"] is None      # last row of wesnoth-lib
    assert rows[7]["neighbours"]["prev"] is None      # first row of wesnoth-units

    assert by["Konrad"]["char_limit"] is None and by["Konrad"]["last_changed"] is None


def test_display_is_unescape_of_raw(tmp_path):
    """The round trip that makes _display safe to hand to a model: derived, never invented."""
    rows, _s, _c, _d = EB.build_rows(_fixture_corpus(tmp_path), "pl",
                                     ["wesnoth-lib", "wesnoth-units"])
    touched = 0
    for r in rows:
        assert r["source_en_display"] == po_parse.unescape(r["source_en"])
        assert (r["target_pl"] is None) == (r["target_pl_display"] is None)
        if r["target_pl"] is not None:
            assert r["target_pl_display"] == po_parse.unescape(r["target_pl"])
        if r["source_en_display"] != r["source_en"]:
            touched += 1
        pf = r["plural_forms"]
        if pf:
            assert pf["target_forms_display"] == [po_parse.unescape(f) for f in pf["target_forms"]]
    assert touched == 2          # the two "\n" rows — escaping decisions do touch real rows


def test_markup_flags_and_string_class():
    assert EB.markup_flags("<b>Bold</b>") == ["pango"]
    assert EB.markup_flags("<emphasis>x</emphasis>") == ["docbook"]
    assert EB.markup_flags("B<bold> text") == ["po4a"]
    assert EB.markup_flags("a &amp; b") == ["entity"]
    assert EB.markup_flags("wesnoth <side>") == ["metasyntax"]
    assert EB.markup_flags("one\\ntwo") == ["newline"]
    assert EB.markup_flags("plain") == []
    for flags in (EB.markup_flags("<b>a\\nb &amp; c</b>"),):
        assert set(flags) <= EB.MARKUP_FLAGS and flags == sorted(flags)
    assert EB.string_class("wesnoth-httt", None) == "campaign/plain"
    assert EB.string_class("wesnoth-lib", "female") == "ui/gender_agreement"
    assert EB.string_class("wesnoth-manpages", None) == "manpages/plain"
    assert EB.string_class("wesnoth-brand-new-campaign", None) == "unknown"
    assert EB.STRING_CLASSES >= {"unknown", "ui/plain", "campaign/gender_agreement"}


def test_placeholder_check_verdicts():
    assert EB.placeholder_check("Gold: $gold", ["Zloto: $gold"]) == "ok"
    assert EB.placeholder_check("Gold: $gold", ["Zloto"]) == "source_only"
    assert EB.placeholder_check("Gold", ["Zloto: $gold"]) == "target_only"
    assert EB.placeholder_check("$a and $b", ["$a i $c"]) == "mismatch"
    assert EB.placeholder_check("Gold", ["Zloto"]) == "not_applicable"
    assert EB.placeholder_check("Gold: $gold", [""]) == "not_applicable"   # untranslated
    # a singular plural form legitimately omits the count var — union, not per-form
    assert EB.placeholder_check("one orc", ["ork", "$count orki"]) == "target_only"


def test_payload_is_byte_stable_and_pinned(tmp_path):
    """The byte contract, pinned on a SYNTHETIC corpus so it runs on a fresh clone."""
    root = _fixture_corpus(tmp_path)
    rows, _s, _c, _d = EB.build_rows(root, "pl", ["wesnoth-lib", "wesnoth-units"])
    payload = EB.serialize(rows)
    assert EB.verify_payload_bytes(payload) == []
    assert payload[:3] != b"\xef\xbb\xbf" and b"\r" not in payload
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    assert payload.count(b"\n") == len(rows)
    import hashlib as _h
    assert _h.sha256(payload).hexdigest() == \
        "805ebc514eb97ce3e7394a2ed7253e8d9ea60ca820e1760c8b5a904b76dc4947", _h.sha256(payload).hexdigest()
    # re-export is byte-identical (this is what --check asserts against the real corpus)
    rows2, _s, _c, _d = EB.build_rows(root, "pl", ["wesnoth-lib", "wesnoth-units"])
    assert EB.serialize(rows2) == payload
    # key order is the schema's order, not sorted() — reordering would move the hash
    first = json.loads(payload.split(b"\n")[0].decode("utf-8"))
    assert list(first) == list(EB.ROW_KEYS)


def test_manifest_shape_and_provenance(tmp_path):
    root = _fixture_corpus(tmp_path)
    domains, _m = EB.corpus_inventory(root, "pl")
    rows, _s, _c, dates = EB.build_rows(root, "pl", domains)
    payload = EB.serialize(rows)
    upstream = {"remote": "https://example.invalid/x.git", "commit": "0" * 40,
                "branch": "master"}
    m = EB.build_manifest("wesnoth", "pl", rows, payload, domains, upstream, dates,
                          generated_at="2026-01-01T00:00:00Z")
    assert EB.verify_manifest(m, rows, payload) == []
    assert list(m) == list(EB.MANIFEST_KEYS)
    assert m["game"] == "battle-for-wesnoth" and m["source_format"] == "gettext-po"
    # po_revision_dates is a MAP keyed by textdomain, not a record
    assert sorted(m["upstream"]["po_revision_dates"]) == domains
    assert len(m["extraction_script_hash"]) == 64
    assert m["content_hash"]["covers"] == "lines.jsonl"
    # a fabricated upstream must not pass
    bad = json.loads(json.dumps(m)); bad["upstream"]["commit"] = "not-a-sha"
    assert EB.verify_manifest(bad, rows, payload)


def test_provenance_is_a_stop_condition(tmp_path):
    """No git checkout -> no bundle. There is no degraded output path by design."""
    try:
        EB.read_upstream(str(tmp_path))
    except EB.ProvenanceError:
        return
    raise AssertionError("read_upstream must raise on a non-checkout")


def test_self_checks_refuse_bad_rows(tmp_path):
    rows, _s, _c, _d = EB.build_rows(_fixture_corpus(tmp_path), "pl",
                                     ["wesnoth-lib", "wesnoth-units"])
    assert EB.verify_rows(rows) == []
    for mutate, needle in (
            (lambda r: r.update(segment_id="wesnoth-lib:abc"), "12 lowercase hex"),
            (lambda r: r.update(target_pl=""), 'must be null'),
            (lambda r: r.update(source_en_display="invented"), "unescape"),
            (lambda r: r.update(pool="reference"), "never written"),
            (lambda r: r.update(string_class="wesnoth-lib"), "outside the vocabulary"),
            (lambda r: r.update(extra_key=1), "outside the schema"),
            (lambda r: r.update(seq=999), "dense"),
    ):
        clone = json.loads(json.dumps(rows))
        mutate(clone[0])
        problems = EB.verify_rows(clone)
        assert any(needle in x for x in problems), (needle, problems[:3])


@pytest.mark.skipif(not os.path.isdir(PO_ROOT), reason="real .po not present (gitignored)")
def test_real_corpus_pins():
    """The pins that only a local run can make: id collisions over the whole corpus, and the
    payload hash. Skips on a fresh clone so CI stays green and licence-clean."""
    domains, missing = EB.corpus_inventory(PO_ROOT, "pl")
    assert len(domains) == 32 and missing == []
    rows, stats, census, _d = EB.build_rows(PO_ROOT, "pl", domains)
    assert stats["rows"] == 26312
    ids = {r["segment_id"] for r in rows}
    assert len(ids) == 26312, f"{26312 - len(ids)} segment_id collision(s)"
    assert stats["derived_msgctxt"] == 712
    assert stats["plural"] == 54
    assert EB.verify_rows(rows) == []
    import hashlib as _h
    assert _h.sha256(EB.serialize(rows)).hexdigest() == \
        "f05b545f75dd22e323bdff09e36aba3f507a3a647bdecca73a95de92ba8b666f"


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
