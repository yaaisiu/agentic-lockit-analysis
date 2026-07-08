---
type: lockit-variables
lockit: a-dark-forest
updated: 2026-07-07
---

# A Dark Forest — placeholder / construct inventory

One entry per construct: syntax · meaning · where · detection regex · translatable? ·
origin ([[construct-origin-labeling]]: `format` = CSV/Godot spec, `project` = this lockit's
convention). Confirmed at GATE 1. The drift sweep (2026-07-07) found **no other constructs** —
this inventory is complete for the current corpus.

## Placeholders in translatable text (locale columns)

### `{N}` — positional format slot
- **Syntax:** `{0} {1} {2} {3}` (contiguous from 0; max index seen = 3).
- **Meaning:** Godot `String.format` argument slot — engine substitutes a runtime value.
- **Where:** 38 cells across locales, e.g. `ui_label:offline_1` en = `You were away for {0}. \n\n`.
- **Detection:** `\{(\d+)\}`
- **Translatable?** No — preserve verbatim; every `{N}` in `en` must appear in each translation
  (cross-locale invariant, [[cross-locale-invariants]]). Order in the sentence may change; the
  set of indices may not.
- **Origin:** `format` (Godot).

### `\n` — literal escaped newline
- **Syntax:** backslash-n (two characters `\` + `n`) inside the cell — **not** a raw newline.
- **Meaning:** in-string line break, expanded by the engine at display.
- **Where:** 32 cells, e.g. `ui_label:harvest_forest` = `Harvest\nForest`; often trailing
  (`… {0}. \n\n`).
- **Detection:** `\\n`  (in a raw-string regex; matches backslash then n)
- **Translatable?** No (control code) — but its *placement* is translator's discretion.
- **Origin:** `format` (Godot / C-style escape).

## Value-shape constructs (locale columns)

### JSON-array literal — multi-value cell
- **Syntax:** a whole cell that is a JSON list, e.g. `["Yes","No"]`,
  `[" Wilderness "," Forest Hovel ",…]`, `["?"]`.
- **Meaning:** a set the game indexes at runtime — ordered tiers (`tab_data_titles:*`),
  button/answer pairs, or random-pick flavour.
- **Where:** 30 keys / 207 cells; present in every locale for those keys.
- **Detection:** cell where `stripped.startswith('[') and endswith(']')` **and** `json.loads`
  yields a `list`. (Do not regex-match — parse, to avoid catching prose brackets.)
- **Translatable?** Yes — **each element** is translatable text. Invariant: **element count**
  must match `en` across locales (0 mismatches today). **Order rule is per-key:** ordered for
  tiers (must align), order-free for interchangeable pairs/random-pick (like Veloren `.aN` —
  don't per-index diff). [Q3]
- **Origin:** `project` (this game's runtime convention; the JSON literal itself is `format`).

## Annotation constructs (the `description` column — never player-facing)

### `[TAG]` — closed 4-tag annotation DSL
- **Syntax / vocabulary (exhaustive):**
  - `[EMPTY]` (80) — the string is intentionally blank in all locales.
  - `[noun]` (38) — part-of-speech hint for translators.
  - `[verb]` (5) — part-of-speech hint.
  - `[DEPRECATED]` (27) — dead string; excluded from extraction by default, counted in report.
- **Where:** `description` column only; may be followed by free-prose context.
- **Detection:** `^\[(EMPTY|noun|verb|DEPRECATED)\]` (anchor at cell start); general census
  `\[[^\]]+\]` on `description` should only ever yield these four — anything else = **drift,
  flag it** ([[construct-origin-labeling]] unknown bucket).
- **Translatable?** No — `description` is context metadata, excluded from translate/extract output.
- **Origin:** `project`.

## Key-embedded constructs (the `key` column)

### `-N` variant suffix · `X` template slot
- **`-1`/`-2`:** variant index on `enemy_data_option_title:<enemy>-{1,2}` (per-enemy dialogue
  variants) and `scale_settings_info:-1`. Detection: `-(-?\d+)$` on the name part. `project`.
- **`X`:** runtime numeric template slot inside the key — `ui_label:reborn_X_line_{1,2}`. One
  template key stands for many runtime keys. Detection: literal `X` token between `_`
  boundaries. Do **not** treat as literal at lookup. `project`. [Q5 — explicit note requested.]

## Not present (confirmed absent — drift sweep 2026-07-07)
printf `%s/%d` · `$var`/`${var}` · `@var` · `{{…}}` · HTML/Pango/BBCode/DocBook markup ·
HTML entities `&…;` · pipe/caret/tilde/backtick tokens · invisible/zero-width/control chars.
Only a literal `&` ("and") appears in 2 English job titles — plain text.
