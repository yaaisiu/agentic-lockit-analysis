---
type: convention
id: clausewitz-pdx-yaml
status: accepted
first_seen: hoi4
also_seen: []
promoted_session: "004"
---

# Convention: the Paradox Clausewitz pseudo-YAML lockit (conventions AS DATA)

**Recognise → don't re-infer.** The keyed-line counterpart to gettext ([[gettext-po]]), Fluent
([[fluent-ftl]]), and tabular CSV ([[csv-tabular]]), for the **Paradox** family. Detect with
[[clausewitz-detection]], read with [[clausewitz_parse_template]] (a line-regex reader — **never
PyYAML**), then fill in the **per-game profile row** below and the dialect.

## Anatomy (game-independent)
- **Files:** `<name>_l_<language>.yml`, **UTF-8-BOM** (`utf-8-sig`). Line 1 = `l_<language>:`
  header; every entry below belongs to the current language. A file MAY switch language
  mid-stream — trust the header, not the filename.
- **Entry grammar:** `KEY:[VERSION] "VALUE"`. Regex (verified 100% on HoI4):
  `^(\s*)([A-Za-z0-9_.\-]+):\s*(\d+)?\s*"(.*)"\s*(?:#.*)?$`. **Not valid YAML** — that's the point.
- **Identity = the key** (per language). May or may not be globally unique — verify; a
  `replace/` folder overrides keys (LIOS), so cross-file duplicates are meaningful at scale.
- **Version integer `KEY:N`** — optional, deprecated **revision counter**, NEVER identity, NEVER
  a selector (HoI4: values only {0..4}, no key ever has two). Capture as metadata; don't rely on it.
- **Values:** double-quoted; contain **unescaped inner `"`** (dialogue) → extract **greedy
  first-quote → last-quote**; the outer pair strips, inner quotes stay. `#` is a comment **only
  outside quotes** — never hand-split on `#`/`,`. Escapes seen: `\n`, `\t`, `\\`, `\"` (rare).
  Real embedded newlines don't occur (single-line values); log-and-skip anything malformed.

## Two formatting dialects (the profile records which)
- **Old-style** (EU4, HoI4, Stellaris): `§X…§!` colour (letter+`§!`), `£icon` (HoI4:
  whitespace-terminated, **no closing `£`**), `@TAG` flag, `$VAR$`/`$VAR|fmt$`, `[scope.fn]`.
- **New-style** (CK3, Vic3, EU5): `#key … #!` formatting (stackable), `@icon!` text icons,
  `[concept|E]` game-concept tooltips, `[Scope.Fn|modifier]` data functions.
- **Shared:** `$OTHER_KEY$` key reuse; `[scope.fn]` data functions with `|fmt` modifiers where
  **`fmt` is colour AND/OR number formatting** (`%`, `.0`, `+=`, precision) — not colour-only.

## Morphology is ENGINE-DELEGATED (not in-string) — see [[morphology-location]]
Plural/gender/case are handled by engine functions + variant keys, NOT selectors: `[X.GetNameDef]`
(definite), `[X.GetAdjective]`, `[C.GetSheHe]`/`[C.GetHerHis]` (gender), and precomputed `_DEF`/
`_ADJ`/`_plural` keys. **No plural system** (no count-based selection). Implication: translators
into richly-inflected languages get little in-loc control — carry this into a downstream audit.

## Conventions AS DATA — the per-game profile row (the reusable payoff)
Record each game+build as a **profile row** so the next title is an added row, not a re-inference:

| field | HoI4 (first row) |
|---|---|
| loc folder spelling | `localisation` (British, `s`) |
| extra `game/` level | no |
| per-language subfolders | yes (`localisation/<lang>/`) |
| encoding | UTF-8-BOM |
| base language set | english, french, german, spanish, braz_por, polish, russian, japanese, simp_chinese (9) |
| colour/format dialect | **old-style** `§X…§!` |
| icon syntax | `£icon` (no closing £) + `@TAG` flags |
| colour letters seen | Y G R H L T W O g b B (audit the full set — slice under-samples) |
| version integer | present (~2%), deprecated |
| replace folder | yes (LIOS override) |
| DLC loc storage | `dlcNNN.zip` (+ some loose, ownership-gated) |

(Fields from `sources/hoi4/research.md` §5; validated against the real files. Add a row per game.)

## Guidance for tooling
One shared line-regex reader ([[clausewitz_parse_template]]); a labels registry with a **two-tier
drift audit** ([[construct-origin-labeling]] — tier-1 unknown vs tier-2 expected tail); the key
style(s) and colour-letter set live in the per-lockit toolkit, not here. Enumerate DLC `.zip`
members alongside loose files if profiling a full install. **Legal:** Paradox content is
proprietary/non-commercial — surface aggregate facts, never redistribute string dumps.

**first_seen:** hoi4 (session 004) — old-style dialect; 206 files / 129,087 entries; 0 dup keys,
0 parse warnings, tier-1 drift = 0 over the whole corpus.
