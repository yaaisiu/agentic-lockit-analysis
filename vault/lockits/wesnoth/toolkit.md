---
type: lockit-toolkit
lockit: wesnoth
skill: lockit-wesnoth-toolkit
updated: 2026-07-02
---

# Wesnoth — toolkit index (how & why)

The deterministic tools for this lockit, packaged as the `lockit-wesnoth-toolkit` skill
(`.claude/skills/lockit-wesnoth-toolkit/SKILL.md`). Scripts live in `scripts/wesnoth/`.
Built + tested at GATE 2 (session 000); **extended corpus-wide in session 001** — DocBook +
po4a markup families, `{brace}` + hex-entity classes, refined `$var`, and the cross-locale
`validate_placeholders.py`. Companion chart: [[profile]], [[variables]], [[structure]],
[[context-prefixes]].

## Design principles (the *why*, for whoever runs this next — incl. a cheaper model)
- **Discover once, extract forever.** The LLM inferred structure at GATE 1; these scripts
  now do the repeatable work with no model calls — reproducible, free, testable.
- **One parser, one token source.** Everything imports `po_parse` (records) and
  `po_tokens` (patterns), so a fix propagates and code never drifts from [[variables]].
- **Lossless + non-ambiguous identity.** Every field preserved separately; identity is
  `(domain, msgctxt, msgid[,plural])` + a reorder-proof `sha1` internal id (line = locator).
- **Rationale-first.** Each script opens with a plain-language *why* header.
- **Dependency-free.** No polib/pandas/pytest required — runs in a minimal env and under
  cheaper models (supports the API-runner goal). Tests run under plain `python3` too.

## Scripts

| script | what it does | example | tested |
|---|---|---|---|
| `po_parse.py` | **foundation** reader → uniform records (+ internal id); `--summary/--jsonl/--check` | `python3 scripts/wesnoth/po_parse.py sources/wesnoth/po/wesnoth-lib/wesnoth-lib.pot --check` | ✅ unit + real |
| `po_tokens.py` | shared token regexes + markup families (pango/docbook/po4a) + `brace_var` | (imported) | ✅ via token/family tests |
| `list_placeholders.py` | inventory `$vars`/markup/entities/escapes/printf/`{brace}` | `… list_placeholders.py sources/wesnoth/po/*/*.pot` | ✅ matches recon |
| `list_context_prefixes.py` | `^`-prefix registry (families, counts, first-seen) | `… list_context_prefixes.py sources/wesnoth/po/*/*.pot --family gender` | ✅ 129 prefixes |
| `extract_by_type.py` | slice by domain / prefix / substring / token class | `… extract_by_type.py sources/wesnoth/po/wesnoth-units/wesnoth-units.pot --prefix female` | ✅ female forms |
| `validate_markup.py` | **per-family** balance (Pango/DocBook/po4a) + stray `\`; **ERROR** (structural) vs **WARN** (unescaped `&`-in-markup) | `… validate_markup.py sources/wesnoth/po/*/*.pot` | ✅ 0 error, 1 warn, 0 FP |
| `validate_placeholders.py` | **cross-locale** consistency: `$var`/`{brace}`/printf/markup/plural-arity, source vs a translation `.po` | `… validate_placeholders.py …/wesnoth-lib.pot …/wesnoth-lib/de.po` | ✅ 8 real defects on de/pl |
| `report.py` | coverage snapshot ("what we know / don't") | `… report.py sources/wesnoth/po/*/*.pot` | ✅ |
| `test_toolkit.py` | dual-mode tests (pytest or plain python) | `python3 scripts/wesnoth/test_toolkit.py` | ✅ **21 passed** |

## Validated facts — corpus-wide (`report.py`, all 32 domains, session 001)
- **26,312 strings; internal ids 26,312/26,312 unique; 0 collisions** — the GATE 1 identity
  model is lossless at full scale. 54 pluralizable; **129 `^`-prefixes** (712 entries).
- Token coverage: wml_var 686, markup_tag 4064, text_attr 47, entity 90, escape 3206,
  printf 17, **brace_var 286**.
- **20,206 strings (77%) have neither `^`-prefix nor `#. id`** → identity rests on the msgid
  text; confirms the GATE 1 key decision at corpus scale.
- **Markup families:** tag = 26,096, po4a = 216. `validate_markup` → 1 real source defect
  (unescaped `&` in a Pango span), 0 false positives.
- **Multi-language (de/pl pilot, 4 domains):** `validate_placeholders` found 8 real defects
  (misspelled/dropped/wrong `$vars`), 0 false positives.

## Deferred / candidate extensions (see [[open-questions]])
- **DONE (B3):** `family()` now has a `gender/agreement` family (was misfiled under other/UI).
- **T6 (deferred, post-English):** run `validate_placeholders` across more locales / all 32
  domains (corpus QA sweep).
- **T7:** give `$(…)` WML formula / `$x[$i]` index their own handling only if needed.
