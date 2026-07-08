---
type: convention
id: csv-tabular
status: accepted
first_seen: a-dark-forest
also_seen: []
promoted_session: "003"
---

# Convention: the tabular key+locale-columns lockit (CSV/TSV)

**Recognise → don't re-infer.** Many UI lockits are a single **table**: one row per string,
one column per locale, plus metadata columns. This is the tabular counterpart to gettext
([[gettext-po]]) and Fluent ([[fluent-ftl]]) keyed trees. Detect it with [[csv-detection]],
then read it with the [[csv_parse_template]] reader and expect the anatomy below.

## The columns (a string-type axis lives in the key, not a `type` column)
- **Key column** (`key`/`id`/`string_id`, usually first): the record identity. Commonly
  **namespaced** (`namespace:name`, or `SCREEN_ELEMENT`) — the prefix groups strings by UI
  surface / system and IS the string-type axis (like a textdomain). **Do not assume it is
  unique** — verify; a real file had a duplicate key (`ui_label:heart`). Godot keeps the first
  occurrence, so a dup is a dead upstream row → flag, don't fix.
- **Context/metadata column(s)** (`description`/`comment`/`notes`/`context`): translator/dev
  notes, NOT a locale. **Exclude from any "text to translate" output; keep as metadata.**
  (Godot quirk: it may still compile a `description` column as a pseudo-locale — ignore that.)
- **Locale columns**: one per language; the leftmost / a `en`-named one is usually the source.
- **Possible extra columns** (not yet seen, watch for them): `max_length`/`char_limit`
  (→ [[find_over_limit]]-style checks), `screen`/`platform`, a workflow `status`.

## Value shapes inside a cell (branch on these)
1. **Scalar string** — the common case.
2. **Multi-value / JSON-array literal** — a cell whose value is a list, e.g. `["Yes","No"]`,
   tier names, random-pick flavour. **Parse it (json), don't regex.** The translatable unit is
   each element; **element COUNT is a cross-locale invariant** ([[cross-locale-invariants]]).
   Order alignment is **per-key** (ordered tiers must align; interchangeable/random-pick sets
   may reorder — don't per-index diff, like Fluent `.aN`).
3. **Empty** — distinguish **intentional** blank (often flagged by a marker in the context
   column, e.g. `[EMPTY]`, and blank in *all* locales) from **untranslated** (blank in one
   locale, source present). Report them separately — a partially-translated locale is expected,
   not a defect. **Exclude deprecated rows before judging "is this locale done".**

## Escaping / parsing discipline (do not hand-split on commas)
Cells contain commas, doubled quotes, and sometimes embedded newlines. **Always use a real
RFC-4180 CSV reader** (Python `csv`), never `line.split(',')`. A rectangular table (every row
== header width) is a structural invariant; a ragged row means your column assumptions are
wrong — fail loudly. A stray trailing comma inside a value (`["?"],`) breaks a would-be array
into malformed JSON — a real defect the reader/validator should catch.

## Annotation DSLs in the context column
The context column often carries a small **closed-vocabulary tag DSL** (e.g. `[noun]`/`[verb]`
part-of-speech hints, `[DEPRECATED]` status, `[EMPTY]` blank-marker). Catalogue the vocabulary
and route anything outside it to the `unknown` bucket ([[construct-origin-labeling]]) — a new
tag is drift. These tags are `project`-origin (their meaning is lockit-specific).

## Guidance for tooling
Split meta vs locale columns once, in a shared reader. Classify value shape once. Expose
duplicates rather than silently deduping. Exclude `[DEPRECATED]`/deprecated by default in
extraction (opt-in to include) and **report** what was dropped — no silent caps.

**first_seen:** a-dark-forest — Godot 4 `localization.csv`, header
`key,description,en,zh,fr,pt,pl,ua,th,es`; namespaced keys; `description` context column + 4-tag
DSL; JSON-array cells; positional `{N}` placeholders. Reader: [[csv_parse_template]].
