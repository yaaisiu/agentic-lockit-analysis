---
type: lockit-profile
lockit: hoi4
format: clausewitz-pseudo-yaml
locales: [en]
row_count: 12867
profiled_at: 2026-07-09
session: "004"
status: confirmed
---

# HoI4 — profile (data dictionary)

> **Proprietary Paradox content — this note is git-tracked.** Aggregate stats + syntax +
> **synthetic** examples only; **no real strings**. Real, navigable examples with `file:line`
> live in the gitignored dossier `data/hoi4/gate1-review.md`. Structure **confirmed by Marcin at
> GATE 1** (2026-07-09). Scope = the 5-file slice (`data/hoi4/en/`, 12,867 entries); construct
> *coverage* is completed by the toolkit `--audit` across all 206 files at scale.

## Shape
- **Paradox Clausewitz pseudo-YAML**: line-oriented `key "value"`, **not valid YAML** → line-regex
  parser, **never PyYAML**. UTF-8-**BOM** (`utf-8-sig`). One `l_english:` header per file.
- Entry grammar (matched **100%** of the slice — 0 malformed, 0 multi-line):
  `<indent> KEY : [VERSION] "VALUE" [# comment]`
  regex `^(\s*)([A-Za-z0-9_.\-]+):\s*(\d+)?\s*"(.*)"\s*(?:#.*)?$`.
- **Identity = the key** (per language). Unique across the slice (0 collisions); cross-file
  duplicates are *possible* at 206-scale (replace-folder overrides) → checked, not assumed.
- Value = double-quoted, extracted **greedy first-quote → last-quote** (see control codes).

## String types
Distinguished by **file** and **key style**, not by a type column:
- **Proper-noun tables** (e.g. country names) — flat keys, short values, near-zero formatting.
- **Focus-tree strings** — title/desc pairs, heavy `$VAR$`, carry the version integer.
- **Event narrative** — long prose, dotted keys, dense `[scope.fn]` + `\n`, embedded quotes.
- **UI / rules / decisions** — short labels; icons `£`, flags `@`, coloured values `$VAR|fmt$`.

## Key conventions (TWO styles — both confirmed; catalogue at toolkit stage)
1. **Underscore keys** `UPPER_SNAKE` / `lower_snake`, with meaningful suffixes. Country names
   follow `<TAG>_<ideology>` with grammatical variants — synthetic: `XXX_fascism`,
   `XXX_fascism_DEF` (definite-article form). Other suffixes: `_desc`, `_OPTION_*`.
2. **Dotted event keys** `<namespace>.<id>.<part>` — synthetic: `mynamespace.42.t` (title),
   `mynamespace.42.desc` (body), `mynamespace.42.a` (option a). The **integer id sits mid-key**;
   trailing tokens (e.g. `…_variantname`) mark conditional variant text.
   Part vocabulary observed: `t` · `d`/`desc` · `a`/`b`/… (options).
- **Marcin (GATE 1):** *catalogue the tags + suffix/part vocabularies* as project constructs.

## Variables & placeholders (the OLD-style dialect; full inventory in `variables.md`)
- `§X … §!` — colour (open `§`+letter, close `§!`). Slice: Y R G H; full 206 also L T W O g b B.
- `£icon` — icon, **whitespace-terminated, NO closing `£`** (correction to the field guide's
  `£icon£`). Detect `£(\w+)`.
- `@TAG` — flag icon (`@`+3-letter country tag), renders a flag before text.
- `$VAR$` — variable/key interpolation; **`$VAR|fmt$`** carries a **format spec** (colour letter
  **and/or** number formatting: `%` percent, `.0` decimals, `+=`/`=+` sign, digit precision) —
  **not colour-only** (confirmed empirically, C4).
- `[scope.fn]` — engine data functions, 4 sub-forms: dotted `[Root.GetName]` (case varies:
  `Root`/`ROOT`/`From`/`FROM`/`GER`…), nested `[From.From.GetName]`, bare global `[GetDateText]`,
  optional-scope `[?scope.chain.Fn]`, with trailing `|fmt` modifier `[scope.fn|+=%]`.
- `\n` — literal two-char newline escape (no real multi-line values exist).
- **Non-translatable set** (Marcin Q4): `§X`/`§!`, `£icon`, `@TAG`, `$VAR$`/`$VAR|fmt$`,
  `[scope.fn]`, `\n`. Everything else is translatable text.

## Numbers
- **Version integer `KEY:N`** — optional, deprecated **revision counter**, *never* identity.
  Empirically (all 206): values only **{0,1,2,3,4}**, 0 dominant; **no key ever has two different
  N** → it is a version counter, **not** a variant selector (C4/D1 resolved). Present ~2% of
  entries overall (97% of the slice's version tags are in `focus`).
- **Event-id integer** mid-key (`…​.42.…`) is part of identity — a *different* number from the
  version integer. Numbers inside values are literal content.

## Conventions & control codes
- `#` is a comment **only outside quotes** — never hand-split on `#` or `,`.
- Values contain **unescaped inner `"`** (dialogue), **not** `\"` (escaped `\"` = 0 in the slice;
  ~21 in all 206 = a tail). Greedy first→last-quote extraction keeps inner quotes, strips only the
  outer pair (verified lossless). 2 genuinely empty `""` values in the slice.
- Malformed lines → **log-and-skip with a warning** (don't silently truncate).

## Limits
- **No char-limit / max-length / status column** — the format has no columns. The deferred §5
  "char-limit column" anatomy is **not** exercised by HoI4 either.
- **Marcin (E1) — soft reference for limit-less lockits:** compare **localised vs source string
  length** as an informational signal (no hard limit exists). → build into `validate`; propose as
  a library heuristic at `/retro`.

## Open questions resolved (see `open-questions.md`)
Q0.1 GATE 0 slice · A1–A4, B1–B3, C1–C6, D1–D2, E1 confirmed at GATE 1 · C4 (`|`=format not
colour) + D1 (`:N`=version not selector) resolved empirically across all 206.
