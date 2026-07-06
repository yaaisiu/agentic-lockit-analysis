---
type: lockit-profile
lockit: veloren
format: fluent-ftl
locales: [en]
row_count: 4241
profiled_at: 2026-07-06
session: "002"
status: confirmed
---

# Veloren — profile (the chart)

Confirmed at GATE 1 (Marcin, 2026-07-06; decisions in [[open-questions]]). Second lockit,
the Phase-6 generality test: **Fluent (`.ftl`)**, a non-gettext, non-tabular keyed message
tree. Source locale profiled = **`en`** (48 files + `_manifest.ron`); 39 other locale dirs
exist but are out of scope (reserved for the cross-locale capability, [[cross-locale-invariants]]).

## Shape
- **Not tabular** — no rows×columns. Unit = a **message**; sub-units = **attributes**.
- **4,241 messages** (ids globally **unique**, 0 cross-file collisions → the 48 files form
  one Fluent bundle namespace), **3,312 attributes**, **2 terms**. UTF-8, **no BOM**.
- Many messages are **containers**: empty value, all content in attributes (gender / variant
  parents). Honest counts: report **total** (msg/attr/term) **and translatable** (excluding
  the 771 `{""}` intentional-empties); exact translatable tally is a `/toolkit` parser job
  (multiline values + containers).

## String types (FOUR attribute roles — the crux, T-V1; labeled, T-V5)
An `.attr =` (indented) is a translatable sub-string of its message, detected in 4 roles.
Every role is **labeled with an origin** (fluent-native vs project-native) in the documented
registry `scripts/veloren/labels.py`; unrecognised names surface as **unknown** (drift). See
[[open-questions]] T-V5.
1. **Metadata** — `.desc` (2,172), `.stat` (8). Description / formatted stat line. (project)
2. **Variant arrays** — `.a0 .a1 … .aN` (485). Alternative lines the engine **random-picks**
   (`npc.ftl:214 npc-speech-villager_under_attack` = 80; `main.ftl:95 loading-tips` = 22). (project)
3. **Grammatical gender** — `.fem` (303) / `.masc` (303) / `.neut` (10). Gender-inflected
   forms. **Concept-match to Wesnoth's gender/agreement family** (different mechanism: here an
   attribute, in Wesnoth an inline `female^` prefix) — cross-format reuse to note at /retro. (project)
4. **Enum lookup** — named keys the engine selects by a runtime enum (31): families
   buff-kind (`.burning`…), weapon-kind (`.sword`…), hire-period, time-unit. Distinct from
   `.aN` (keyed by NAME, not index). **Discovered by the drift audit at GATE 2.** (project)

## Key conventions (with the confirmed exception)
- Ids are **lowercase, `-`-namespaced** (first segment ≈ feature/domain: `common`(840),
  `weapon`(677), `hud`(633), `armor`(440), `name`(313), `command`(294)…), `_` within a segment
  (`hud-owned_by_for_secs`). Namespace is convention, not Fluent-enforced. No `^` context
  prefix (unlike [[inline-context-prefix]]); no `msgctxt` (unlike [[gettext-po]]).
- **Outlier (project-rule check):** `tutorial-*` and `achievement-*` (49 ids) use **PascalCase**
  final segments (`tutorial-Move`, `achievement-Jumped`) mirroring internal code enum names.

## Variables & placeholders → see [[variables]]
`{ $x }` runtime args (448 refs incl. **119 on attribute values** — track both), 26 inline
selectors, 2 `TAIL()` custom-function calls, 13 `{ -term }`/`{ msg }` references, 771 `{""}`
empties. All non-translatable except the text between them; **preserve verbatim**.

## Numbers
No numeric key columns, no char-limit metadata (Fluent has none). Numbers appear only in
selector variant keys (`[0]`,`[1]`) and inside `$var`-formatted values.

## Conventions & control codes
- **Selectors/plurals inline** (T-V2): `{ $x -> [1] … *[other] … }`, keep intact as one value.
  CLDR categories + explicit numbers; `*` = default. Good for grammar/plural QA cross-locale.
- **Terms**: `-server`/`-client` shared snippets, included via `{ -term }`.
- **`TAIL($noun)`**: Veloren-custom, strips a noun's article (`noun.ftl:1`). Preserve.
- **`{""}`**: intentional blank (Fluent forbids bare `msg =`); track, exclude from translatable.
- **`<` `>` `&`**: ordinary text in Fluent (no XML/c-format meaning); only `{`,`}` special
  (`{"{"}` for a literal). No markup family present (Pango/DocBook/POD all absent).

## Limits
None declared in-file (no max-length/char-limit column — a UI-xlsx feature Fluent lacks).

## Open questions resolved
All T-V1..T-V4 + terms/empties/functions/`<>`/key-outliers resolved at GATE 1 — see
[[open-questions]]. **Still open:** T-V5 (tag attribute sub-kinds in the toolkit?) — deferred
to `/toolkit`, where the value can be shown before deciding.
