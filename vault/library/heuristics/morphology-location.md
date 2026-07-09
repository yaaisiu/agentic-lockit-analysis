---
type: heuristic
id: morphology-location
status: accepted
first_seen: hoi4
also_seen: [wesnoth, veloren]
promoted_session: "004"
---

# Heuristic: where does the format carry morphology — in-string, or engine-delegated?

**The question to ask of every lockit:** how are **plural, gender, and case/agreement** handled?
There are two fundamentally different designs, and which one a format uses **predicts how much
grammatical control a translator has** — a first-order fact for any inflecting target language
(Polish, Russian, Finnish…). It is **inferable from the source locale alone** (you read it off the
presence/absence of selector machinery), so determine it during profiling, before translation.

## The two designs
- **IN-STRING selectors** — the morphology lives in the loc string, for the translator to fill:
  - gettext ([[gettext-po]]): `msgid_plural` + `Plural-Forms` arity; gender via a `female^`
    msgctxt convention.
  - Fluent ([[fluent-ftl]]): `{ $n -> [one]… *[other]… }` selectors; gender/variant `.masc`/
    `.fem`/`.neut` attributes.
  → the translator has **full** control: they write each plural form and can select on gender.
- **ENGINE-DELEGATED** — the morphology lives in game code + data, referenced by function/key:
  - Clausewitz ([[clausewitz-pdx-yaml]], HoI4): case/definite/adjective via engine functions
    `[X.GetNameDef]`, `[X.GetAdjective]` (+ precomputed `_DEF`/`_ADJ` variant keys); gender via
    pronoun functions `[C.GetSheHe]`, `[C.GetHerHis]` scoped to a character; **plurals: none** —
    no count-based selection; a `_plural` key is just a second fixed label game-script picks.
  → the translator gets **little in-loc control**: one fixed form per function, bare `$VAR$`
    numbers with **no agreement**. Rich inflection must be worked around (neutral phrasings).

## How to detect (deterministic, from the source)
- **Selectors present?** search for the format's selector syntax (`msgid_plural`, `{ $x ->`,
  `.fem`/`.masc` attrs, `female^`). Present ⇒ in-string.
- **Function/variant machinery instead?** enumerate data-function calls (`GetName`, `GetAdjective`,
  `GetSheHe`, pronoun getters) and variant key suffixes (`_DEF`, `_ADJ`, `_plural`, `_male`).
  Present with **no** in-string selectors ⇒ engine-delegated.
- **Plural specifically:** count-form selection anywhere (`nplurals`, `{ $n ->`, `|plural`)? If
  none and numbers are plain `$VAR$`/`%d`, the format has **no grammatical plural** — flag it.

## Why it matters (carry into the translation-phase audit)
- An engine-delegated format is a **structural limitation** for inflecting languages: the tooling
  cannot check plural arity or gender agreement because the format doesn't express them; the QA
  focus shifts to "did the translator find an acceptable fixed phrasing?" not "are the N plural
  forms present?".
- It also tells you **which cross-locale invariants apply** ([[cross-locale-invariants]]): plural
  arity is meaningless for Clausewitz; token preservation (`$var`/`[scope.fn]`) is the real one.

**first_seen contrast set:** wesnoth (gettext, in-string) · veloren (Fluent, in-string) · hoi4
(Clausewitz, engine-delegated, no plural system) — three points that make the axis concrete.
