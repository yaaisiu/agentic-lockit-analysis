---
type: lockit-structure
lockit: hoi4
format: clausewitz-pseudo-yaml
encoding: utf-8-bom
profiled_at: 2026-07-08
---

# HoI4 — recon snapshot (deterministic)

> **Proprietary Paradox content.** This note is git-tracked → **aggregate stats + syntax only,
> no real strings**. Real examples with `file:line` pointers live in the gitignored dossier
> `data/hoi4/gate1-review.md`. Scope = the GATE 0 **5-file slice** (`data/hoi4/en/`), not all 206.

## Format & encoding
- **Paradox Clausewitz pseudo-YAML** — line-oriented, **not valid YAML** (do NOT use PyYAML).
- Every file: **UTF-8 with BOM** (`EF BB BF`) — read with `encoding="utf-8-sig"`.
- One `l_english:` language-database header per file (line 1); all entries below belong to it.
  Slice: **5 headers, all `l_english`** (no mixed-language blocks in this slice).

## Entry grammar (field-guide regex matched **100%** of the slice — 0 malformed, 0 multi-line)
```
<indent> KEY : [VERSION] "VALUE" [# comment]
```
- `KEY` — `[A-Za-z0-9_.\-]+`. `:` — mandatory. `VERSION` — optional integer (see Numbers).
- `VALUE` — double-quoted; extract **greedy first-quote → last-quote** on the line.
- `#` is a comment **only outside quotes**; never hand-split on `#` or `,`.
- Regex used (from `sources/hoi4/research.md`, verified):
  `^(\s*)([A-Za-z0-9_.\-]+):\s*(\d+)?\s*"(.*)"\s*(?:#.*)?$`

## Slice inventory
| file | entries | version-tagged | notable |
|---|--:|--:|---|
| `countries_l_english.yml` | 5,837 | 0 | plain `TAG_ideology` keys → proper nouns; `$VAR$` only |
| `focus_l_english.yml` | 2,488 | 2,316 | version-integer carrier; `§`, `$VAR$`, `\n` |
| `events_l_english.yml` | 3,409 | 0 | narrative; densest `[scope]` (925) + `\n` (550); dotted keys; 2 empty values |
| `game_rules_l_english.yml` | 843 | 30 | `@TAG` flag carrier (51) |
| `decisions_l_english.yml` | 290 | 0 | `£icon` carrier (63); `$VAL\|mod$` coloured vars |
| **TOTAL** | **12,867** | **2,346** | |

## Integrity (slice)
- **0 malformed lines**, **0 multi-line/unterminated-quote values**, **0 duplicate keys**
  (within-file and across the 5 files).
- **2 genuinely empty values** (`""`), both in `events`.
- **§ colour open/close balanced** on every line (0 imbalance) within the slice.

## Constructs present (entries containing — slice; syntax detailed in `variables.md`)
`§`colour 399 · `£`icon 63 · `@`flag 53 · `$VAR$` 304 · `[scope.fn]` 1,081 · `\n` 672 ·
escaped `\"` **0** · `\\` **0**.

## Drift preview — slice does NOT exercise the full construct space (for toolkit `--audit`)
- **§ colour letters:** slice sees only **Y R G H**. Full 206 also contain **L T W O** and
  lowercase **g b** and **B** (counts only, no content). The toolkit `--audit` must run across
  all 206 to catalogue the tail; the slice is not exhaustive on colour letters.
- **Escaped `\"`:** 0 in the slice; field guide reports ~21 in all 206 — a genuine tail, deferred
  to `--audit`.
- HoI4 is the **OLD-style dialect** (`§Y…§!`, `£icon`, `@TAG`), NOT the CK3/Vic3 `#key…#!` dialect.
