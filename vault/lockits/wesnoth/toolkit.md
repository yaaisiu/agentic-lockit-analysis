---
type: lockit-toolkit
lockit: wesnoth
skill: lockit-wesnoth-toolkit
updated: 2026-07-02
---

# Wesnoth — toolkit index (how & why)

The deterministic tools for this lockit, packaged as the `lockit-wesnoth-toolkit` skill
(`.claude/skills/lockit-wesnoth-toolkit/SKILL.md`). Scripts live in `scripts/wesnoth/`.
Built + tested at GATE 2 (2026-07-02). Companion chart: [[profile]], [[variables]],
[[structure]], [[context-prefixes]].

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
| `po_parse.py` | **foundation** reader → uniform records (+ internal id); `--summary/--jsonl/--check` | `python3 scripts/wesnoth/po_parse.py data/wesnoth/pot/wesnoth-lib.pot --check` | ✅ unit + real (2026-07-02) |
| `po_tokens.py` | shared token regexes + known-tag set | (imported) | ✅ via `test_token_detection` |
| `list_placeholders.py` | inventory `$vars`/markup/entities/escapes/printf | `… list_placeholders.py data/wesnoth/pot/*.pot` | ✅ matches recon |
| `list_context_prefixes.py` | `^`-prefix registry (families, counts, first-seen) | `… list_context_prefixes.py data/wesnoth/pot/*.pot --family gender` | ✅ 105 prefixes |
| `extract_by_type.py` | slice by domain / prefix / substring / token class | `… extract_by_type.py data/wesnoth/pot/wesnoth-units.pot --prefix female` | ✅ 63 female forms |
| `validate_markup.py` | Pango balance + stray `\` + unescaped `&`-in-markup | `… validate_markup.py data/wesnoth/pot/*.pot` | ✅ 0 hard issues |
| `report.py` | coverage snapshot ("what we know / don't") | `… report.py data/wesnoth/pot/*.pot` | ✅ |
| `test_toolkit.py` | dual-mode tests (pytest or plain python) | `python3 scripts/wesnoth/test_toolkit.py` | ✅ 10 passed |

## Validated facts (from `report.py`, 4-domain subset)
- 5,258 strings; **internal ids 5,258/5,258 unique**; 48 pluralizable; 105 `^`-prefixes.
- Token coverage: wml_var 384, markup 462, text_attr 27, entity 3, escape 684, printf 11.
- **60% of strings (3,134) have neither `^`-prefix nor `#. id`** → identity must rest on
  the msgid text; confirms the GATE 1 key decision.
- `validate_markup`: source is clean (0 hard issues); 30 non-markup angle tokens tracked (T2).

## Not yet built
- `validate_placeholders.py` (cross-locale consistency) — needs `.po` translations; planned
  with pilot languages (spec Phase 6). See [[open-questions]] deferred items.
