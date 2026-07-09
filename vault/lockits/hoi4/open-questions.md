---
type: lockit-open-questions
lockit: hoi4
updated: 2026-07-09
---

# HoI4 — open questions

## GATE 1 — structure confirmed by Marcin (2026-07-09)
- **Dossier:** `data/hoi4/gate1-review.md` (gitignored; real content). All claims A1–A4, B1–B3,
  C1–C6, D1–D2, E1 **confirmed**. Two "look closer" items resolved empirically across all 206:
  - **C4 — `$VAR|fmt$` `|` = format spec, NOT colour-only.** 7,780 occurrences; modifiers mix
    colour letters (`H`/`Y`/`R`/`G`/`U`) with number formatting (`%`, `.0`, `+=`/`=+`, precision).
    Same `|fmt` in `[scope.fn|+=%]`. **decided_by:** Marcin · **decided_at:** 2026-07-09 · GATE 1.
  - **D1 — `KEY:N` = version counter, NOT a variant selector.** All 206: values only {0,1,2,3,4},
    0 dominant; **no key ever carries two different N**. **decided_by:** Marcin · **at:** 2026-07-09.
- **A3/Q1 — keep unescaped inner `"` raw** in extracted values (lossless). Confirmed.
- **B1/B2/Q2 — catalogue** the key tags + suffix vocab (`_DEF`/`_desc`) and event parts
  (`t`/`d`/`desc`/`a`…) as `project` constructs. Confirmed → do at toolkit stage.
- **Q4 — non-translatable set** = `§X`/`§!`, `£icon`, `@TAG`, `$VAR$`/`$VAR|fmt$`, `[scope.fn]`,
  `\n`. Confirmed.

## E1 — soft length reference for limit-less lockits (Marcin's idea, GATE 1) — TRACKED
- HoI4 has no char-limit column. **Idea:** compare **localised vs source string length** as an
  informational reference (not a hard limit). → build a `--length-ref` mode into `validate` at
  toolkit stage; **propose as a library heuristic at `/retro`** (applies to any limit-less lockit).

## Q-INFL — how does HoI4 handle plurals / gender / case-inflection? — RESOLVED (2026-07-09)
- **status:** resolved (investigated with the toolkit across all 206 files) · **asked_by:** Marcin
- **Finding — HoI4 pushes morphology OUT of the loc string** (opposite of gettext/Fluent):
  - **Case / definiteness / adjective → engine functions (~25.4k calls) + variant keys.** Names
    aren't stored inflected; the string calls a function and the engine returns the form:
    `GetAdjective` (6619), `GetNameDef` (5840, definite "the X"), `GetNameDefCap` (3272),
    `GetName` (5777), `GetNameWithFlag`, `GetAdjectiveCap`. Backed by precomputed variant KEYS
    `_DEF` (≈3240) and `_ADJ` (≈2575).
  - **Gender → engine pronoun functions (~230 calls), scoped to a character:** `GetHerHis` (99),
    `GetSheHe` (76), `GetSheHeCap`, `GetHerHim`, `GetHerselfHimself`, `GetFuhrerGenderedName`;
    e.g. `[FROM.GetLeader.GetSheHe]`. Gender lives on the game object, not the string. Only ONE
    `_female` key exists — gender is not a key-variant axis.
  - **Plurals → NO grammatical plural system.** 0 plural functions, 0 count-based selection, 0
    in-string selector operators (no Fluent `{ $n -> }`, no gettext `msgid_plural`, no
    `$VAR|plural$`; the `$VAR|fmt$` modifiers are colour + number-format only). The 62 `_plural`
    keys are just a second fixed label game-script picks (52/62 have a singular base key).
- **Implication (downstream Polish audit):** richly-inflected targets (Polish: 3 plural forms,
  7 cases) have **no in-loc machinery** to decline nouns after numbers or case-inflect names
  mid-sentence — only fixed `[X.GetNameDef]` forms + bare `$VAR$` numbers with no agreement. A
  real limitation, and it is **visible from the English source** (read off the function API +
  absence of any selector syntax). → carry into the Polish-audit lockit downstream.
- **→ FLAGGED FOR /retro (promotion candidate):** a cross-lockit heuristic
  **`morphology-location`** — *"where does a format carry plural/gender/case: as IN-STRING
  selectors (gettext `msgid_plural`/`female^`, Fluent `{$n->}`/`.masc/.fem`) or delegated to
  ENGINE FUNCTIONS + variant keys (Clausewitz `GetNameDef`/`GetSheHe`, `_DEF`/`_ADJ`/`_plural`)?"*
  The answer predicts how much morphological control a translator has, and is inferable from the
  source locale alone. first_seen would cite wesnoth/veloren/hoi4 as the three contrasting points.

## Source-side completeness / integrity findings (s004, added post-GATE-2) — report, don't fix
Since HoI4 English is source-only (no translation to measure), the toolkit reports source-side
completeness. Across all 206 files (via `report.py` / `validate.py --refs`):
- **40 dangling `$OTHER_KEY$` reference candidates** — a `$name$` that looks like a key reference
  (has lowercase) but matches no key. Real defects to review; e.g. `$sasebo_naval_arsenall$` (a
  double-L typo of its own key `..._arsenall_...`), `$Australia$`, `$Scavenger$`, `$num$`. A few
  are benign (e.g. `$RATIO%$`). **Must be computed on the FULL corpus** — cross-file refs make a
  partial set over-count (slice = 49 false-inflated vs corpus = 40).
- **Event structural coverage:** 245 events with no title part, 130 with no body/desc part (some
  intentional — news/tooltip-only events — some likely defects). Surface for human review.
- Third-party proprietary data → we **surface**, never edit.

## Tracked for toolkit / scale-up (Q3 confirmed) — status: open
- **T-H1 — `--audit` across all 206:** enumerate the construct tail the slice misses — colour
  letters L/T/W/O/g/b/B, escaped `\"` (~21), any unknown `§`/`£`/`@`/`$…$`/`[…]`/`|fmt` forms.
- **T-H2 — cross-file duplicate keys at 206-scale** (replace-folder/override semantics) — report.
- **T-H3 — catalogue** key tags + suffix/part vocabularies (from B1/B2).

## Q0.1 — GATE 0 scope: which files are the lockit? — RESOLVED
- **status:** resolved
- **gate:** GATE 0
- **decided_by:** Marcin
- **decided_at:** 2026-07-08
- **decision:** Profile a **5-file representative slice** of the 206 loose English `.yml`
  (all in gitignored `sources/hoi4/`), chosen from measured construct density (not guessed)
  so every construct is exercised, then scale the toolkit to all 206 (the Wesnoth pattern).
  Copied into `data/hoi4/en/` (gitignored):

  | file | entries | carries (why in slice) |
  |---|--:|---|
  | `focus_l_english.yml` | 2,488 | **version-integer** (2,316 = 97% of all version tags), `§`, `$VAR$`, `\n` |
  | `events_l_english.yml` | 3,409 | narrative; densest **`[scope/fn]`** (925) + **`\n`** (550) |
  | `decisions_l_english.yml` | 290 | the **`£icon£`** carrier (116, densest; compact) |
  | `game_rules_l_english.yml` | 843 | the **`@TAG`** carrier (52 = majority of the rare construct) + version |
  | `countries_l_english.yml` | 5,837 | plain-baseline string type: flat `TAG:` keys → short proper nouns, ~zero formatting |

  Slice total = **12,867 entries** (≈10% of the 129,087-entry corpus). All 5 confirmed **UTF-8-BOM**.
- **Coverage note:** every construct is hit EXCEPT escaped `\"` (only **21 occurrences in all 206
  files** — a genuine tail). Deferred to the `--audit` drift catcher at toolkit stage rather than
  hunting a file for it now.
- **Corrections to the kickoff's guessed slice (from real measurement):**
  - `countries` has **zero `@TAG`** (kickoff assumed it carried them) → added `game_rules` as the real `@TAG` carrier.
  - version-integer construct is **97% concentrated in `focus`** → `focus` is essential for it.

## Q0.2 — Licence / redistribution — CARRIED FORWARD (open)
- **status:** open (standing guardrail, not blocking)
- Proprietary Paradox content (non-commercial Paradox User Agreement, see `sources/hoi4/research.md` §Legal).
  `data/hoi4/**` + `sources/hoi4/**` stay gitignored; **never** a string into `library/`, a skill, or
  any committed note; surface defects, never redistribute dumps. First NDA-class lockit — gitignore
  discipline is load-bearing (verified via `git check-ignore` at GATE 0).

## Tracked (open) — for GATE 1 / toolkit
- **T0.1 — multi-line values?** research flags possible embedded newlines within quotes (distinct
  from literal `\n`); confirm the line-regex parser tolerates or handles them.
- **T0.2 — comments / `#`:** `#` is a comment only OUTSIDE quotes; never hand-split on `#` or `,`.
- **T0.3 — version integer** is optional metadata (~2% of entries) — never rely on it as identity.
