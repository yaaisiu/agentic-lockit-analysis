---
type: lockit-profile
lockit: a-dark-forest
format: csv
locales: [en, zh, fr, pt, pl, ua, th, es]
row_count: 676
profiled_at: 2026-07-07
session: 003
status: confirmed
---

# A Dark Forest — profile (the chart)

Godot 4 CSV translation table from `github.com/TinyTakinTeller/GodotProjectZero`
(`assets/i18n/localization.csv`). **First genuinely tabular lockit** in this system
(Wesnoth = gettext, Veloren = Fluent — both keyed trees). Structure confirmed at GATE 1
(dossier `data/a-dark-forest/gate1-review.md`, gitignored; Marcin confirmed all claims +
answered Q1–Q5, 2026-07-07). **Licence:** loc content is CC-BY-NC-SA 4.0 (not MIT) —
gitignored, non-commercial, test-only; never ships, never enters `library/`.

## Shape
- One CSV, one sheet, comma-delimited (Godot `.import` `delimiter=0`), UTF-8 no BOM, LF-only.
- 1 header row + **676 data rows × 10 columns**, perfectly rectangular (0 ragged rows).
- Columns: `key`, `description`, then 8 locales `en zh fr pt pl ua th es` (`en` = source).
- `description` is **not** a locale — it's a context/annotation column (see String types).
  (Godot quirk: the engine still compiles it as `localization.description.translation`.)

## String types
No `type` column; the string-type axis is the **key namespace** (prefix before `:`), ~24 of
them: `ui_label` (126), `substance_text` (116), `event_data_text` (70),
`resource_generator_{label,title,flavor,display_name,max_flavor}` (~35 each), `enemy_data_*`,
`npc_event_*`, `worker_role_*`, `credit`, `role`, `scale_settings_info`, `tab_data_titles`, …
Value shapes within a cell:
- **Scalar string** — the common case.
- **JSON-array literal** — 30 keys / 207 cells are quoted JSON lists (tiers, button pairs,
  random flavour), e.g. `tab_data_titles:world` = 13 settlement-tier names; `["Yes","No"]`;
  `["?"]` (×84). All valid JSON; **array length is a cross-locale invariant** (0 mismatches
  in 177 checked pairs). Elements are individually translatable structure.
- **Empty** — intentional iff `description == [EMPTY]` (80 rows, blank in all 8 locales).

## Key conventions
- Identity = `key` = `namespace:name` (exactly one `:` per key). **Not guaranteed unique:**
  `ui_label:heart` is duplicated (rows 6 & 645) — an upstream dead-duplicate bug; Godot keeps
  the first. Toolkit **flags** duplicates (report, don't fix — third-party data). [Q1]
- Charset mostly `[a-z0-9_:]`. Sub-conventions / outliers:
  - `-1`/`-2` **variant suffixes** — `enemy_data_option_title:<enemy>-1|-2` (per-enemy dialogue
    variants); plus `scale_settings_info:-1` (negative-index setting). Not defects.
  - **`X` templated keys** — `ui_label:reborn_X_line_1|2`: `X` is a runtime-substituted number
    in the *key* (one template covers `reborn_<n>_line_…`). `project`-origin key-template
    construct; documented, no special handling — do **not** treat `X` as literal. [Q5, Marcin:
    explicit note because we're not fully certain of the runtime mechanism.]

## Variables & placeholders
See `variables.md` for the full inventory + regexes. Summary:
- **Positional `{0}`–`{3}`** (Godot `String.format`) — 38 cells, max index 3. Must survive
  translation verbatim.
- **Literal `\n`** (backslash-n, an escaped newline inside the cell) — 32 cells.
- **No printf `%s/%d`**, **no `$var`/`@`/entity/other** placeholder styles (drift sweep clean).

## Numbers
- In **keys:** the `-1/-2` variant indices and the `X` numeric template slot (above).
- In **text:** ordinary digits in prose (e.g. timer values in `description`), not a placeholder
  class of their own. Counts/values in UI come via `{0}`-style slots, not baked-in numerals.

## Conventions & control codes
- **`description` annotation DSL** (English, `project`-origin) — closed 4-tag vocabulary:
  `[EMPTY]` (80, intentional blank) · `[noun]` (38, part-of-speech hint) · `[DEPRECATED]`
  (27, dead string) · `[verb]` (5). Optionally followed by free prose context.
  `description` is **excluded** from any "text to translate/extract" output but **kept** as
  metadata and surfaced to translators. [Q2]
- **`[DEPRECATED]`** is a filter axis: deprecated rows are **excluded from extraction by
  default** (opt-in to include) and **counted** in the report. [Q4]
- **No in-game markup family** (no BBCode/HTML/Pango/DocBook). Drift sweep found zero unknown
  structural tokens; only a literal `&` ("Writing & Narrative") in 2 English job titles — plain
  text, not an entity. `[[markup-families]]` does not apply to this lockit.

## Limits
- **No char-limit / max-length column** — this lockit does not exercise that anatomy (it
  remains the one untested §5 part across all lockits; deferred, open-questions Q0.3).
- Only hard structural limit: 10 fixed columns; `{0}`–`{3}` implies ≤4 format args per string.

## Completeness (report this — Marcin, B3)
Empties per column: `key` 0 · `description` 0 · `en` 81 · `zh` 80 · `fr` 94 · `pt` 107 ·
`pl` 107 · **`ua` 362** · `th` 82 · `es` 81. Of `ua`'s 362 blanks, **281 are untranslated**
(en present); ~80 are the intentional `[EMPTY]` rows shared by all locales. So `ua` is a
**partially-translated** locale; the others are ~complete bar the intentional blanks.
The report separates *intentional blank* (`[EMPTY]`) from *untranslated* (locale-only blank).

## Open questions resolved (GATE 1, 2026-07-07)
A1–A3, B1–B3, C1–C2, D1–D2, E1–E2 all **confirmed**; Q1 yes · Q2 yes-both · Q3 yes-both
(parse array elements + enforce element-count parity; per-key order rule — ordered tiers vs
order-free pairs) · Q4 yes · Q5 agreed. D2 re-verified with an explicit hidden-markup drift
sweep (clean). See `open-questions.md` and the dossier.
