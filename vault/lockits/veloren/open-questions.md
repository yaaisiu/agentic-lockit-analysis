---
type: lockit-open-questions
lockit: veloren
updated: 2026-07-06
---

# Veloren — open questions & resolutions

Second lockit (Phase 6 generality test): a **non-gettext, Fluent (`.ftl`)** localisation
system. Purpose is to test whether the accumulated `library/` speeds intake and where a
genuinely new format forces fresh inference. See [[STATE]], session note 002. GATE 1
decisions came from Marcin's inline answers in `data/veloren/gate1-review.md` (gitignored).

## Resolved

### Q0 — Scope → resolved (GATE 0)
Lockit = English source `data/veloren/en/` = 48 `.ftl` + `_manifest.ron`. 39 translation
locales out of scope (reserved for cross-locale capability). Mode B, GPL-3.0.
`decided_by`: Marcin · `decided_at`: 2026-07-06 · gate: **GATE 0**

### T-V1 — Attribute model → resolved (GATE 1)
Attributes (`.attr =`, indented) are translatable sub-strings of a message, in **three**
detected roles: **(a) metadata** `.desc`(2172)/`.stat`(8); **(b) variant arrays** `.aN`
(485; engine random-picks — `npc-speech-villager_under_attack` has 80); **(c) grammatical
gender** `.fem`(303)/`.masc`(303)/`.neut`(10) — links [[markup-families]]?→no; links the
Wesnoth **gender/agreement** family (concept match, different mechanism). Extraction unit =
`(message_id, attribute|"value")`, id-only identity, `file` kept as searchable provenance.
Many messages are **containers** (empty value, all content in attributes).
`decided_by`: Marcin · `decided_at`: 2026-07-06 · gate: **GATE 1**

### T-V2 — Selectors / plurals → resolved (GATE 1)
Inline `{ $x -> [key] … *[other] … }`, 26 total. Keep the selector value **intact as one
unit** (don't split). Variant keys mix CLDR categories (`one`/`other`) + explicit numbers
(`[0]`,`[1]`); `*` = default. Marcin: *"nice feature for grammar issues"* → document
examples + good practices (see profile.md); a validator can check variant-key validity and
cross-locale plural arity ([[cross-locale-invariants]]). `decided_at`: 2026-07-06 · GATE 1

### T-V3 — Variables `{ $x }` → resolved (GATE 1)
Non-translatable runtime args; **preserve verbatim**. 448 refs (329 on values + **119 on
attribute values** — track both, per Marcin). 115 unique names. Charset outliers confirm
regex must allow hyphen/upper: `\{\s*\$([A-Za-z][A-Za-z0-9_-]*)\s*\}`. New placeholder class
for the library (no [[markup-families]] coverage; partial precursor = Wesnoth `{brace}`).
`decided_at`: 2026-07-06 · gate: **GATE 1**

### T-V4 — `_manifest.ron` → resolved (GATE 1)
RON loader metadata (locale id, fonts). **Excluded** from string inventory; documented as
structure only. `decided_by`: Marcin ("Confirm") · `decided_at`: 2026-07-06 · GATE 1

### Terms `{ -term }` → resolved (GATE 1)
2 terms (`-server`,`-client`), referenced 13×. **Included** as translatable units (id starts
`-`). Marcin: *"important mechanics to keep track of."* `decided_at`: 2026-07-06 · GATE 1

### Empties `{""}` → resolved (GATE 1)
771 `{""}` (mostly `.desc` of internal fragments) = intentionally blank. **Excluded** from
the *translatable* count but **tracked and reported** (Marcin: "inform user about all counts
properly" → report total vs translatable). `decided_at`: 2026-07-06 · gate: **GATE 1**

### Functions `{ TAIL() }` → resolved (GATE 1)
`TAIL()` is **Veloren-custom** (strips a noun's article), self-documented `noun.ftl:1`,
`dialogue.ftl:45`. Not a Fluent built-in (`NUMBER`/`DATETIME` are). Preserve verbatim.
`decided_at`: 2026-07-06 · gate: **GATE 1**

### `<` `>` / escaping → resolved (GATE 1, Marcin's question answered)
In Fluent `<`,`>`,`&` are **ordinary text** (no XML/c-format meaning); only `{`,`}` are
special (`{"{"}` for a literal brace). Veloren uses `<…>` as literal decoration/metasyntax
(`hud/trade.ftl:32`, `main.ftl:116`). No markup family, nothing to balance/escape.

### Key-naming outliers → resolved (GATE 1, Marcin's standing rule applied)
Keys are lowercase `-`-namespaced + `_` within segments, EXCEPT **`tutorial-*` /
`achievement-*`** (49 ids) which use **PascalCase** final segments mirroring code enum
names (`tutorial-Move`). Documented as a known exception. `decided_at`: 2026-07-06 · GATE 1

## Resolved (continued)

### T-V5 — Label attribute sub-kinds (with origin) → resolved (GATE 2)
Marcin: *"label them, they may be fluent native or current project native — anyhow we need it
labeled and labeling documented so it's easy to catch when something changes or is unknown to
our system."* → **Decision: LABEL every construct with an ORIGIN** (`fluent` = format spec /
`project` = Veloren / `unknown` = flag), in a **documented registry** (single source of truth:
`scripts/veloren/labels.py`), with an **`unknown` bucket + drift audit** (`labels.py --audit`)
so new/unrecognised constructs surface instead of being silently mis-handled.
- **The rule immediately paid off:** the audit flagged **31 uncatalogued attributes** → a
  **4th attribute role, `enum`** (named lookup keys: buff-kind/weapon-kind/hire-period/time-unit),
  now catalogued by family. New keys will re-surface as unknown (drift detection intact).
- `decided_by`: Marcin · `decided_at`: 2026-07-06 · gate: **GATE 2**

### Cross-locale validator → built (GATE 2), scope extended
Cross-locale placeholder/gender check (`validate_placeholders.py`, Fluent instance of library
[[cross-locale-invariants]] + [[validate_placeholders]]) — Marcin: *"always needed, our core
thing."* Scope extended past GATE 0 to pull `de` + `pl` into `data/veloren/` (translations,
gitignored). **Pilot found real upstream defects, 0 false positives:** de `loading-tips.a19`
dropped `$gameinput-roll`; pl `main-login-banned` / `main-login-kicked` dropped `$reason`
(verified against source). We surface, never fix (GPL upstream). `decided_at`: 2026-07-06 · GATE 2

## Standing rule captured this session (→ harden at /retro)
- **Targeted outlier / consistency checks are a project rule** when analysing any lockit
  (Marcin, C2): don't assume uniformity — actively probe key naming, variable syntax,
  attribute shapes for outliers and report them. Candidate `library/heuristics` or SOP
  promotion at [[retro]] (propose→approve→apply).

## Library payoff (running)
✅ `gettext-detection` (not gettext) · ✅ `markup-families` (no angle markup) · ⚠️
`inline-context-prefix` N/A · ⚠️ `po_parse_template` doesn't fit → new Fluent reader ·
🆕 gender attributes echo Wesnoth **gender/agreement** (concept reuse across formats).
