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
import po_parse, po_tokens, validate_markup

HEADER = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n'


def write_po(tmp_path, body, name="synthetic.pot"):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(HEADER + "\n" + textwrap.dedent(body), encoding="utf-8")
    return str(p)


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
    assert any("unbalanced" in i or "unclosed" in i
               for i in validate_markup.check_string("<b>oops"))
    assert any("unescaped" in i
               for i in validate_markup.check_string("<b>bad & tag</b>"))  # & inside markup


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
