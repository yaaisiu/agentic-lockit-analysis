---
type: session
id: "003"
date: 2026-07-08
lockit: a-dark-forest
gates_cleared: [GATE 0, GATE 1, GATE 2]
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 003 — A Dark Forest (Godot CSV): the tabular generality test

## Goal
Close the one untested §5 anatomy: a **genuinely tabular** lockit — explicit key column,
context/metadata column, many locales as columns in one file, CSV quoting/escaping. (Char-limit
column was the stretch goal; deferred — see below.)

## What happened

### Scouting (3 parallel agents)
Fanned out three web scouts (Godot CSV games · xlsx/rich-column · larger CSV/TSV). Verified
licences + real structure. Shortlist: **A Dark Forest** (real Godot game), **Polyglot Master
Sheet** (CC0, ~25 locales), Sum Zero (BBCode). **No clean source with a char-limit column
exists** — Godot CSV only supports `?context`/`?plural`; the one open sheet that had it is
410-gone; **LocJAM 3 xlsx turned out to be board-game maps, not a lockit** (dropped at intake).

### GATE 0 — intake (Mode B)
Sparse+shallow clone of `github.com/TinyTakinTeller/GodotProjectZero` → `sources/a-dark-forest/`.
Scope = `assets/i18n/localization.csv`, copied to `data/a-dark-forest/`. **Licence correction:**
scouts called it "MIT", but only `*.gd` code is MIT — the **loc content is CC-BY-NC-SA 4.0**
(surfaced to Marcin; accepted as gitignored non-commercial test-only data). *Lesson: a repo's
code licence ≠ its content licence — check the content licence specifically at intake.*

### GATE 1 — structure (review dossier, all confirmed)
676 rows × 10 cols, UTF-8/LF, rectangular. `key` = `namespace:name` (~24 ns, **1 dup**
`ui_label:heart`). `description` = context column + closed 4-tag DSL
(`[EMPTY]`/`[noun]`/`[verb]`/`[DEPRECATED]`), **not a locale** (Godot compiles it as a
pseudo-locale though). 8 locales, `en` source, `ua` partial. **JSON-array cells** (30 keys /
207 cells) = multi-value shape, length is a cross-locale invariant. Placeholders `{0}`–`{3}` +
literal `\n`. **No markup.** Q1–Q5 answered; B3 (completeness stats) + D2 (hidden-markup drift
sweep — ran it, clean) honoured.

### GATE 2 — toolkit (8 scripts, 31 tests, packaged)
`csv_parse` (shared reader) · `labels` (origin registry + `--audit`) · `report` (completeness:
intentional/untranslated/active) · `inventory` · `extract` (`[DEPRECATED]` excluded by default) ·
`arrays` (element expansion + length parity) · `validate` · `validate_placeholders` (cross-locale
{N}+array-length). Dual-mode tests: **31/31**. Skill `lockit-a-dark-forest-toolkit` packaged.

## Real defects surfaced (report, don't fix — third-party data)
1. Duplicate key `ui_label:heart` (rows 6 & 645).
2. **3 malformed `es` array cells** — `npc_event_options:cat_talk_A{1,2,3}` = `["?"],` (stray
   trailing comma) vs `en` `["?"]`. **Caught by the toolkit, missed by the manual GATE-1 scan**
   (which only compared cells where both sides parsed as arrays) — validates "extract with
   scripts, not eyeballs".
3. `ua` is the **only genuinely partial locale** (256 active untranslated); fr/pt/pl's
   "untranslated" counts were entirely `[DEPRECATED]` strings → excluding deprecated, all
   locales but `ua` are complete.

## Library payoff (recognise-before-infer)
✅ `gettext-detection` → not gettext · ✅ `markup-families` → none · ✅ `cross-locale-invariants`
→ {N}+array-length · ✅ `outlier-hunting` → dup/arrays/active-vs-deprecated · ✅
`construct-origin-labeling` → generalised cleanly to columns/tags (origin `format` = the
generalisation of `fluent`/`gettext`). **Gap confirmed:** no `csv-detection` recogniser, no CSV
reader template → proposed below.

## Promotions proposed (pending Marcin approval → apply)
1. convention `csv-tabular` (first_seen a-dark-forest)
2. heuristic `csv-detection` (fills the recogniser gap)
3. script-template `csv_parse_template.py` (dependency-free reader + why)
4. update `construct-origin-labeling` also_seen +a-dark-forest; note `format` origin generalises
   `fluent`/`gettext`
5. update `outlier-hunting` also_seen +a-dark-forest
6. update `cross-locale-invariants` also_seen +a-dark-forest; add JSON-array-length invariant

## Open threads
- **Char-limit column still untested** (Q0.3) — needs a dedicated hunt for a file that has it.
- `sources/locjam3/` left on disk (gitignored; `rm` was denied — harmless).
- North-star still open: licence choice (#4), telemetry wiring (#3).
