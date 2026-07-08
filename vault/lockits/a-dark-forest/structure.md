---
type: lockit-structure
lockit: a-dark-forest
format: csv
encoding: utf-8
profiled_at: 2026-07-07
---

# A Dark Forest — recon snapshot (deterministic)

Source: `data/a-dark-forest/localization.csv` (Godot 4 CSV translation table, from
`github.com/TinyTakinTeller/GodotProjectZero`, `assets/i18n/`). First **tabular** lockit in
this system (Wesnoth = gettext, Veloren = Fluent; both keyed-tree).

## File
- **Format:** CSV, one file, one sheet. Comma-delimited (Godot `.import` `delimiter=0`).
- **Encoding:** UTF-8, **no BOM**. Decodes cleanly. **No CRLF, no lone CR** (LF only).
- **Header row:** 1 (row 1). **Columns:** 10.
- **Rows:** 676 data rows (677 physical incl. header). **Every row has exactly 10 fields**
  (no ragged rows).
- **Sibling files (out of scope):** `localization.*.translation` = Godot's *compiled* binary
  outputs (incl. `localization.description.translation` — Godot compiles the `description`
  column as a pseudo-locale). `localization.csv.import` = import metadata (kept in `data/` for
  the delimiter/locale mapping). Compiled binaries are not source; excluded at GATE 0.

## Columns
| # | name | role (inferred) |
|---|------|-----------------|
| 0 | `key` | record identity — namespaced id (`namespace:name`) |
| 1 | `description` | **developer/translator context**, NOT a locale — annotation DSL + prose |
| 2 | `en` | source locale (English) |
| 3 | `zh` | Chinese (Simplified) |
| 4 | `fr` | French |
| 5 | `pt` | Portuguese (BR) |
| 6 | `pl` | Polish |
| 7 | `ua` | Ukrainian |
| 8 | `th` | Thai |
| 9 | `es` | Spanish |

8 locale columns; `en` is the source. Script variety: Latin, CJK (`zh`), Cyrillic (`ua`),
Thai (`th`) — UTF-8 verified across all.

## Fill / completeness (empties per column)
`key` 0 · `description` 0 · `en` 81 · `zh` 80 · `fr` 94 · `pt` 107 · `pl` 107 · **`ua` 362**
· `th` 82 · `es` 81.
- 80 empties are **intentional** (`description == [EMPTY]`, all 8 locales blank — confirmed).
- `ua` is a **partially-translated** locale: 362 empty, of which **281 have `en` present**
  (genuinely untranslated) vs ~80 intentional. Other locales hover ~80–107 (≈ the intentional
  empties + a few gaps).

## Key column
- **675 unique of 676** — **one duplicate:** `ui_label:heart` appears twice (rows 6 & 645),
  identical `en`/`pl`, only `description` differs. → key alone is **not** a unique identity.
- **Namespace = prefix before first `:`** — ~24 namespaces, largest: `ui_label` (126),
  `substance_text` (116), `event_data_text` (70), `resource_generator_*` (5×35), etc.
  Every key contains exactly one `:` (0 keys without a colon).
- **Charset:** mostly `[a-z0-9_:]`. Outliers: 23 keys carry `-` (systematic `-1`/`-2` variant
  suffixes, e.g. `enemy_data_option_title:rabbit-2`; and `scale_settings_info:-1`); 2 keys
  carry a literal `X` template slot (`ui_label:reborn_X_line_1/2`).

## Value shapes
- **Scalar strings** — the common case.
- **JSON-array literals** — 30 keys, **207 cells** are quoted JSON lists, e.g.
  `["Yes","No"]`, `["?"]` (×84), `[" Wilderness "," Forest Hovel ",…]` (settlement tiers).
  **All 207 parse as valid JSON**; cross-locale **element count matches in all 177 checked
  pairs (0 mismatches)** — array length is an invariant.
- **Empties** — see completeness above (intentional `[EMPTY]` vs untranslated).

## Placeholders / control codes / markup
- **Positional placeholders `{0} {1} {2} {3}`** (Godot `String.format`) — 38 cells, max index 3.
- **Literal `\n`** (backslash-n, escaped, not a real newline) as in-string line break — 32 cells.
- **printf `%s/%d`** — **none** in locale columns (`%` appears only as the word "percent" in
  `description` prose).
- **In-game markup (BBCode/HTML/Pango)** — **none**. All `[...]` in locale columns are JSON
  arrays; all `[...]` in `description` are annotation tags (below). No markup family applies.

## `description` column — annotation DSL (closed tag set + prose)
Not a locale. English developer/translator notes. Bracket tags (closed set of 4):
`[EMPTY]` (80) · `[noun]` (38) · `[DEPRECATED]` (27) · `[verb]` (5), optionally followed by
prose context ("automated prestige timer …", "in-game tab title"). Godot nonetheless compiles
it as a pseudo-locale.

## CSV-escaping (first exercise of this anatomy)
- **631 cells contain a comma** and **287 contain a `"`** → real quoting/escaping in use;
  `csv` module parses to a perfectly rectangular 676×10 table (quotes doubled, well-formed).
- **0 cells contain an embedded newline.** So multiline-cell handling is *not* exercised here.

See `data/a-dark-forest/gate1-review.md` (gitignored) for the GATE-1 dossier with evidence.
