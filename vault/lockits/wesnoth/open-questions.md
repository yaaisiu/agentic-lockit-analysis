---
type: lockit-open-questions
lockit: wesnoth
updated: 2026-07-02
---

# Wesnoth — open questions & decisions

## Resolved

### GATE 0 — scope of first profiling pass
- **Decision:** Representative subset of **4 gettext textdomains**, **English source
  (`.pot`) only**: `wesnoth-lib` (UI), `wesnoth` (core), `wesnoth-units` (units/gender),
  `wesnoth-httt` (campaign dialogue). Format anatomy is uniform gettext across all 32
  domains, so the toolkit is expected to generalize corpus-wide; deep-profile these 4,
  spot-check the rest later.
- **Also decided:** GATE 1 will be delivered as a **review dossier** (`data/wesnoth/
  gate1-review.md`, gitignored) — each claim paired with a `file:line` pointer + reasoning
  so Marcin can navigate and verify before confirming. New patterns he spots get folded in.
- **Deferred:** `.po` translations (60+ languages) staged for the later multi-language
  phase; when we get there, start with a few pilot languages for cross-locale validation.
- decided_by: Marcin · decided_at: 2026-07-01 · gate: GATE 0

### GATE 1 — structure confirmed (2026-07-02)
All Round-1 claims confirmed with corrections below; full evidence in
`data/wesnoth/gate1-review.md` (gitignored). decided_by: Marcin · gate: GATE 1.

- **Identity (Q1, C1.1, C1.3) — DECIDED.** Natural key = `(textdomain, msgctxt, msgid[,
  msgid_plural])` (standard gettext key; `msgctxt` always empty in Wesnoth, so
  `(domain, msgid)` is unique — proven 5,258/5,258). Plus our own reorder-proof internal
  id `"<domain>:" + sha1(domain ⋮ msgctxt ⋮ msgid ⋮ msgid_plural)[:10]`. **Every field is
  preserved separately, never merged/dropped** (msgid, plural, `^`-context, all `#.`, all
  `#:`, flags; line = locator only). Rationale: `^`-prefix and `#.[tag]:id` are both
  partial and non-unique, so neither can be the key.
- **C3.1 gender — corrected.** `female^` (×80), `male^` (×1), `gender^` (×3). Female is
  marked via caret; base string = default. Only-`msgid_plural` plurals (no `_pl/_sg`).
- **C5.3 escapes — corrected.** `\n`, `\t`, `\"`, `\\` all present (not just `\n`).
- **Q2 rare `<…>` tags — classified & TRACKED.** command-help metasyntax
  (`<side>`, `<var>=<value>`) / Pango (`<small>`) / literal (`<unknown>`). Approach:
  preserve metasyntax verbatim; revisit translate-inner-word with more files.
- **Q3 `&x` — resolved.** XML/Pango entities `&quot; &lt; &gt;` (escaping in markup
  strings), not a placeholder/mnemonic class. Preserve verbatim.
- **Q4 `^`-prefix taxonomy — DECIDED.** 105 distinct prefixes / 350 entries in subset.
  Maintain an **evidenced, growing registry** (`context-prefixes.md`); note convention +
  families. Corpus ≈520k tokens → corpus work is **scripted**, LLM for judgment.

### GATE 2 poking — confirmed (2026-07-02, decided_by Marcin)
- **SI number prefixes.** `^`-prefixes `prefix_kilo…yotta`, `prefix_milli…yocto`,
  `infix_binary` hold one-char magnitude symbols (`k M G … m µ n …`, binary `i`). Preserve
  verbatim; flag the few a locale may localize (`µ`, binary infix). Craft note in [[variables]].
- **List grammar.** `conjunct`/`disjunct` × `pair/start/mid/end` = CLDR-style list assembly;
  rebuild per target language, don't translate literally. **Documented as library candidate
  [[list-grammar-cldr]] (status: proposed → accept at /retro).**
- **T1 — RESOLVED.** Dotted `$obj.attr` are **runtime WML object properties** (`unit.name`,
  `unit.language_name`, `unit.side`, `ally_leader.*`), not references to lockit ids. No
  id↔id link. But a **value-level cross-domain dependency** exists: `$unit.language_name`
  expands to a localized unit name from `wesnoth-units` inserted mid-sentence → gender/case
  agreement hazard. Recorded in [[variables]].

### Phase 6 — corpus-wide generality + multi-language (2026-07-02, session 001)
Ran the finished toolkit over **all 32 domains** with no re-profiling; extended it (Marcin
approved "cover all 3" families). decided_by: Marcin · gate: post-GATE-2 extension.
- **Anatomy holds corpus-wide — CONFIRMED.** 26,312 strings, **`internal_id` 26,312/26,312
  unique, 0 collisions**. The GATE 1 identity model is lossless at full scale.
  *(s008, 2026-08-21: this result covers `internal_id` and nothing else. The bundle exporter's
  `segment_id` is a different function over a different preimage and was measured on its own —
  also 0 collisions over the same 26,312. Naming the function is part of quoting the number.)*
- **Three markup systems, domain-separated — DOCUMENTED.** Pango (29 game domains),
  **DocBook** (`wesnoth-manual`), **po4a/POD man** (`wesnoth-manpages`). `validate_markup`
  now auto-selects the family; full corpus → 1 real source defect, 0 false positives.
  See [[variables]] §3.
- **`{brace}` name-generator grammar — DOCUMENTED** as a placeholder class (§3b, 286 occ).
- **Hex entities `&#x`/`&#0x` — ADDED** to the entity recogniser (§5).
- **`$var` tokenizer refined** to not swallow a trailing sentence period (fixed 6 false
  cross-locale mismatches). See [[variables]] §1.
- **T2 — RESOLVED (classified).** Bare `<side>`/`<nickname>` are **CLI argument metasyntax**
  (single-token slots), now distinguished from Pango, DocBook, and po4a. Preserve verbatim;
  no balance-check. Inner-word translation still has no cited rule → keep preserving.
- **T3 — RESOLVED.** Help/`<ref>` is Pango (balance-checked); man/DocBook semantics now
  covered by the po4a/DocBook families.
- **T4 — RESOLVED (registry regenerated).** 105 → **129** prefixes / 712 entries, corpus-wide.
  Registry is now script-generated ([[context-prefixes]]); growth is a `git diff`, not manual.
- **Multi-language STARTED (prepared capability).** `validate_placeholders.py` (cross-locale)
  built + tested; de/pl pilot over 4 domains found **8 real defects, 0 false positives**. See
  [[variables]] §10. *Framing (Marcin): the current focus is the **English** lockit analysis +
  tooling; multi-language is a prepared tool, run in earnest later.*

### Review-dossier decisions (2026-07-06, `data/wesnoth/session001-review.md`)
- **A1–A4 CONFIRMED** — markup-family detection, refined `$var`, `{brace}` name-generator
  reading, `&#0x7B;`=`{`. (A1 caveat: not every file eyeballed — revise if something new turns up.)
- **B1 — DECIDED: unescaped `&`-in-markup → `WARN`, not `ERROR`.** Engine tolerates a literal
  `&` used as "and"; flag for a human. `validate_markup` now emits ERROR/WARN. Corpus = 0/1.
- **B3 — DONE: `gender/agreement` family** added to `family()` (12 prefixes) — trace all
  gender/plural mechanics for translators. See [[context-prefixes]]. **T5 RESOLVED.**
- **B4 — DONE: DocBook set pre-seeded** with inline/GUI tags, **excluding** names that collide
  with bare CLI slots (`command`, `option`, …) — that collision would false-flag "unclosed".

## Still open / tracked
- **T6 — corpus multi-locale QA sweep (DEFERRED, post-English):** run `validate_placeholders`
  across more locales / all 32 domains. We surface upstream defects, never fix (GPL data).
- **T7 — `$var` rare constructs (corpus audit):** `$(…)` WML formula (8 occ) and `$x[$i]`
  variable index (6 occ) tokenize imprecisely but safely (no cross-locale false positives).
  Give `$(…)` its own token class only if needed. See [[variables]] §1.
- **T2-residual:** whether a CLI metasyntax inner word is ever translated — still no cited rule.
- **A3-followup (localization phase):** name-generator affix **order** (`{prefix}{suffix}`) is
  grammar-fixed; some languages may need different order/connectors. Revisit with translations.
