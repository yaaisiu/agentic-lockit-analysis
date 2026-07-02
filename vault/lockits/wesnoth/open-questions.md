---
type: lockit-open-questions
lockit: wesnoth
updated: 2026-07-01
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

## Still open / tracked (revisit with more domains)
- **T2 — command-help angle placeholders (Q2):** whether inner words are ever translated
  (no cited Wesnoth rule; currently preserve all).
- **T3 — help markup `<ref>/<command>` (C5.2):** semantics clearer with help/manual domains.
- **T4 — prefix registry growth:** new `^` prefixes as more domains/files are ingested.
