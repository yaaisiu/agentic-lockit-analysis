---
type: lockit-structure
lockit: veloren
format: fluent-ftl (+ ron manifest)
encoding: utf-8 (no BOM)
profiled_at: 2026-07-06
---

# Veloren — structure (recon snapshot)

Deterministic recon of `data/veloren/en/` (scratchpad `recon_ftl.py`). Factual only;
interpretation + confirmation live in the GATE 1 dossier / `profile.md`.

## Files & shape
- **48 `.ftl` files** (UTF-8, **no BOM** — all 48 decode clean; matches the manifest's
  "save without BOM" warning) in a nested tree: top-level (`common`, `main`, `command`,
  `buff`, `npc`, `name`, …) + `hud/` (17), `item/` (armor/, items/, weapon/ …), `quest/`.
- **`en/_manifest.ron`** — a second, non-Fluent format (RON). Declares
  `language_name`/`language_identifier` + per-locale `fonts`. **Not translatable content**;
  it's loader metadata. (T-V4.)

## Fluent is NOT tabular — it's a keyed tree, not rows×columns
Unlike a CSV/xlsx lockit, there are no columns. The unit is a **message**; its "fields" are:
| field | Fluent syntax | count | notes |
|---|---|---|---|
| message id | `ident =` at col 0 | **4,241** (all **unique**, 0 cross-file collisions) | the key |
| value | text after `=` (may be multiline) | 4,241 | 126 messages have multiline values |
| attributes | indented `.attr = …` | **3,312** on **2,597** messages | two roles — see below |
| terms | `-ident =` at col 0 | **2** (`-server`, `-client`) | shared snippets, referenced 13× |

## Attributes serve TWO distinct roles (both translatable, both inline)
1. **Metadata sub-fields** — `.desc`, `.stat` attached to a message.
   `buff.ftl:2 buff-heal = Heal / .desc = Gain health over time. / .stat = { $duration -> … }`
2. **Variant arrays** — `.a0 .a1 .a2 …` many alternative lines the engine random-picks.
   `npc.ftl:214 npc-speech-villager_under_attack` has **80** such attrs; `main.ftl:95
   loading-tips` has 22. This is why the attribute-per-message distribution has a long tail.

## Placeable classes (inside `{ … }`)
- **External variables `{ $x }`** — 567 refs, **115 unique** names (top: `$SP`, `$victim`,
  `$boost`, `$name`, `$key`, `$duration`, `$attacker`, `$site`). Runtime args; non-translatable.
  Some inject another message's value, e.g. `{ $gameinput-togglelantern }`.
- **Selectors `{ $x -> … }`** — 26. Variant keys mix **CLDR plural categories** (`one`,
  `other`) and **explicit numbers** (`[1]`, `[0]`). Plurals are **inline**, not separate
  entries (contrast gettext `msgstr[0..N]`).
- **Function calls** — 2, only `TAIL(…)` (a Veloren custom Fluent function).
- **Message/term references `{ -term }` / `{ msg }`** — 13, mostly the 2 terms.
- **String literals `{ "…" }`** — 773, of which **771 are `{""}`** (intentionally-empty
  value, all `.desc` of modular-component fragments in `item/items/internal.ftl`) + one
  `{"
"}` literal newline. Non-content; exclude from translatable inventory.

## Markup
- **No angle-bracket markup family present** (Pango/DocBook/POD all absent — `markup-families`
  consulted, returns negative). Fluent content is plain text + `{ }` placeables only.

## Contrast with the known gettext anatomy ([[gettext-po]])
| | gettext (Wesnoth) | Fluent (Veloren) |
|---|---|---|
| identity | `(domain, msgctxt, msgid[,plural])` | **message id** (globally unique in bundle) |
| plurals | separate `msgstr[0..N]` rows, per-lang header | **inline** `{ $n -> [one]… *[other]… }` |
| sub-strings | none (1 msgid = 1 string) | **attributes** (`.desc`/`.stat`/`.aN`) |
| context | `msgctxt` / inline `^` prefix | (none — id namespacing instead) |
| vars | `$var`, `%s`, `{brace}` | `{ $var }`, selectors, `{ FUNC() }`, refs |
