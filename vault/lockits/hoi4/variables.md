---
type: lockit-variables
lockit: hoi4
updated: 2026-07-09
---

# HoI4 — placeholder / control-code inventory

> Git-tracked → **synthetic examples only**. Origins per [[construct-origin-labeling]]: all here
> are **`format`** (Clausewitz old-style dialect) unless noted `project`. Slice-confirmed; the
> toolkit `--audit` completes coverage across all 206 (esp. colour letters). Detection regexes are
> the deterministic rules the toolkit encodes.

## `§X … §!` — colour code · origin `format` · NOT translatable (preserve verbatim)
- **Syntax:** `§` + one letter opens; `§!` closes. Synthetic: `§YGold text§!`.
- **Letters:** slice = Y R G H; **full 206 also L T W O and lowercase g b and B** → `--audit` must
  enumerate across all files (slice is not exhaustive).
- **Detect:** open `§([A-Za-z])`, close `§!`. Balance check: `#§[A-Za-z]` == `#§!` per string.
- **Meaning:** the letter is a colour id (partly community-reverse-engineered; treat map as approximate).

## `£icon` — text icon · origin `format` · NOT translatable
- **Syntax:** `£` + icon name, **whitespace-terminated, NO closing `£`** (HoI4 shape; ≠ Stellaris
  `£icon£`). Synthetic: `£command_power §Y15§!`.
- **Detect:** `£(\w+)`. Do **not** use `£…£` (would span to the next icon / colour code).

## `@TAG` — flag icon · origin `format` · NOT translatable
- **Syntax:** `@` + 3-letter country tag; renders a flag before following text. Synthetic:
  `@XXX Countryname`.
- **Detect:** `@([A-Z]{3})` (tag = uppercase). Rare (53 in slice, concentrated in game_rules).

## `$VAR$` and `$VAR|fmt$` — variable interpolation · origin `format` · token NOT translatable
- **Syntax:** `$NAME$` interpolates an engine value or another key. A `|` introduces a **format
  spec** — **colour and/or number formatting** (confirmed C4): colour letters (`H`,`Y`,`R`,`G`,`U`)
  mixed with `%` (percent), `.0` (decimals), `+=`/`=+` (signed), digit precision. Synthetic:
  `$FACTOR$`, `$VALUE|H$`, `$VALUE|+=%1$`.
- **Detect:** whole token `\$([^$]+)\$`; split name/fmt on first `|` → `name`, `fmt`.
- **Note:** word order *around* the token is translatable; the token itself is not.

## `[scope.fn]` — engine data function · origin `format` · NOT translatable
- **Four sub-forms** (synthetic):
  - dotted scope chain + fn: `[Root.GetName]`, `[From.GetAdjective]` (scope case varies:
    `Root`/`ROOT`/`From`/`FROM`/`GER`…)
  - nested scope: `[From.From.GetName]`
  - bare global fn (no scope, no dot): `[GetDateText]`, `[GetYear]`
  - optional/nullable scope prefix `?`: `[?scope.chain.GetNameDefCap]`
  - trailing format modifier `|fmt` (same grammar as `$VAR|fmt$`): `[scope.fn|+=%]`
- **Detect:** `\[([^\]]+)\]`; then classify: leading `?` = optional; contains `.` = scoped else
  bare; trailing `|…` = format modifier.

## `\n` — literal newline escape · origin `format` · translatable position, keep the token
- **Syntax:** two chars `\` + `n` inside a single-line value (no real line breaks exist).
- **Detect:** `\\n`. Distinguish from `\\` (backslash, 0 in slice) and `\"` (escaped quote, 0 in
  slice / ~21 in all 206 — `--audit` tail).

## Key-embedded constructs · origin `project` (catalogue at toolkit stage — Marcin GATE 1)
- **Underscore keys:** `<TAG>_<ideology>` + grammatical suffixes (`_DEF` definite article,
  `_desc`, `_OPTION_*`). Suffix set to be enumerated.
- **Dotted event keys:** `<namespace>.<id>.<part>`; part ∈ {`t`,`d`,`desc`,`a`,`b`,…}; mid-key
  integer = event id (identity); trailing `_variant` tokens = conditional text.

## Drift / audit targets (route to `unknown` bucket per [[construct-origin-labeling]])
- Any `§` letter outside the known set; any unclosed `§X`/missing `§!`.
- Any `\X` escape other than `\n` / `\\` / `\"`.
- Any `$…$` / `[…]` shape the classifier can't place; any new `|fmt` token.
- Escaped `\"` occurrences (tail — surface where they appear).
