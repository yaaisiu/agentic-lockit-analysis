---
type: dev-state
updated: 2026-07-06
phase: 6
active_lockit: veloren
---

# STATE — you are here

**Phase 6. Session 002 DONE — the generality test PASSED.** Two lockits now fully mapped +
tooled: Wesnoth (gettext, 32 domains) and **Veloren (Fluent `.ftl`)** — different formats,
same pipeline, GATE 0/1/2 all cleared, 50 tests, skill packaged, all-locale defect report.
The library sped intake (recogniser/ruler-out) and gained new assets. **Next session: intake
a third, still-untested-structure lockit — a TABULAR `.xlsx`/`.csv`** (key + char-limit
columns are the one §5 part neither gettext nor Fluent exercised). Retro promotions pending
Marcin's approval (see below). See `docs/next-session-kickoff.md`.

## Active — Veloren (Fluent `.ftl`) — GATE 0 + GATE 1 cleared, 2026-07-06
- **Intake done (Mode B):** sparse+shallow clone of `gitlab.com/veloren/dev/veloren`
  `assets/voxygen/i18n/` into gitignored `sources/veloren/`. GPL-3.0, licence-clean.
- **GATE 0 scope:** English source = 48 `en/**/*.ftl` + `en/_manifest.ron` in
  `data/veloren/en/` (gitignored). 4,241 messages (0 id collisions), 3,312 attrs, 2 terms.
- **GATE 1 cleared** (dossier `data/veloren/gate1-review.md`, gitignored; Marcin answered
  inline). Vault written: `profile.md` (confirmed), `structure.md`, `variables.md`,
  `open-questions.md`. Anatomy: Fluent keyed tree; identity = unique message id; **3
  attribute roles** (metadata `.desc/.stat` · variant-arrays `.aN` · **gender
  `.fem/.masc/.neut`** ← echoes Wesnoth gender/agreement); inline selectors; `{ $var }`;
  terms; `{""}` empties; Veloren-custom `TAIL()`; no markup family.
- **Library payoff:** ✅ `gettext-detection` (not gettext) · ✅ `markup-families` (no markup)
  · ⚠️ `inline-context-prefix`/`po_parse_template` don't fit → **new Fluent reader** needed.
- **GATE 2 cleared — toolkit built, tested, packaged.** 9 dependency-free scripts in
  `scripts/veloren/` (parser, report, inventory, extract, gender_pairs, validate,
  validate_placeholders, report_all_locales, labels) + tests; **50 tests pass**. Skill
  `lockit-veloren-toolkit` packaged; `toolkit.md` indexes it.
- **T-V5 resolved — LABELING system built (Marcin's rule):** every construct tagged origin
  `fluent`/`project`/`unknown` in documented registry `labels.py`; `--audit` drift catcher
  found a 4th attribute role (`enum`). 4 attribute roles total (metadata/variant/gender/enum).
- **Cross-locale sweep done (all 39 locales):** `data/veloren/technical-defects.md` (gitignored)
  — **81 real technical defects, 0 false positives** (dominant: `$reason` dropped in
  `main-login-banned/kicked` across ~16 locales; `$min_combo` in it axe descs; version skew
  in zh-Hant). FP fixes: engine `*_gender` vars + `.aN` index mismatch excluded.
- **Standing rule captured (→ harden at /retro):** targeted outlier/consistency checks are a
  project rule when analysing any lockit (found PascalCase key outliers, gender attrs, enum role).
- **NEXT — `/retro`:** propose library promotions (approve→apply): `fluent-ftl` convention,
  `ftl_parse_template`, and the **origin-labeling + drift-audit** idea (format-general); write
  session 002 note (already drafted as living log) + next-session kickoff.

## Done
- Repo scaffolded per spec §6; `git init` done (first commit: scaffold only).
- `.claude/settings.json` — deny-leaning permissions (spec §9 / App. D), verified
  against current Claude Code docs. Note: spec's `Write(/**)`/`Edit(/**)` deny rules
  were **omitted** — with current path semantics a single leading slash is
  project-root-relative, so those would deny *all* in-repo writes; Claude Code already
  confines writes to the project dir.
- Commands: `/intake`, `/profile`, `/toolkit`, `/wake`, `/retro`.
- `vault/02_SYSTEM/schema.md` — note frontmatter contracts, incl. the telemetry seam.
- `vault/library/` seeded empty (conventions/ heuristics/ script-templates/ + glossary).

## In progress — Wesnoth (GATE 0 + GATE 1 cleared)
- **Intake done (Mode B):** sparse/shallow clone of `wesnoth/wesnoth` `po/` in gitignored
  `sources/wesnoth/`; 32 gettext textdomains, ~26.3k English strings, 60+ langs.
- **GATE 0:** scope = 4 `.pot` (English source): `wesnoth-lib`, `wesnoth`, `wesnoth-units`,
  `wesnoth-httt`, copied to `data/wesnoth/pot/`.
- **GATE 1 cleared:** structure confirmed via review dossier (`data/wesnoth/gate1-review.md`,
  gitignored). Identity = `(domain, msgctxt, msgid[,plural])` + sha1 internal id, lossless.
- **Phase 3 done — vault notes written:** `profile.md` (confirmed), `structure.md`,
  `variables.md`, `context-prefixes.md` (105-prefix registry, script-generated),
  `open-questions.md` (decisions + tracked T1–T4).
- **Phase 4/5 DONE — toolkit built, tested, packaged.** 8 scripts in `scripts/wesnoth/`
  (parser, tokens, list_placeholders, list_context_prefixes, extract_by_type,
  validate_markup, report, tests); **10 tests pass** (dual-mode). Skill
  `lockit-wesnoth-toolkit` packaged; `toolkit.md` indexes it. GATE 2 cleared.
- **Library seeded (applied at /retro):** conventions `gettext-po`, `inline-context-prefix`,
  `list-grammar-cldr`; heuristics `gettext-detection`, `review-dossier`; script-template
  `po_parse_template.py` (verified on real files).
## Session 001 DONE — Option A (corpus-wide + multi-language), 2026-07-06
- **Generality confirmed:** toolkit ran across **all 32 domains**, no re-profiling —
  26,312 strings, **ids 26,312/26,312 unique, 0 collisions**. Anatomy holds.
- **Toolkit extended (Marcin-approved):** 3 markup families (Pango/DocBook/po4a) with
  per-family + ERROR/WARN validation; `{brace}` + hex-entity classes; refined `$var`
  tokenizer; `gender/agreement` prefix family (129-prefix registry regenerated).
- **Multi-language capability built:** `validate_placeholders.py` (cross-locale) — de/pl
  pilot found **8 real upstream defects, 0 false positives**. Framed as a *prepared* tool;
  focus stays on English analysis.
- **Tests 10 → 21, all pass.** Vault notes (profile/variables/structure/context-prefixes/
  open-questions/toolkit) updated in-session.
- **Human-in-the-loop review** (`data/wesnoth/session001-review.md`): A1–A4 confirmed;
  B1 (`&`→WARN), B3 (gender/agreement family) applied; B4 (DocBook pre-seed, CLI-collision
  names excluded); T5 resolved; T6/T7 tracked.
- **Library promotions applied (Marcin approved in review C1):** heuristic `markup-families`,
  convention `cross-locale-invariants`, template `validate_placeholders.py`.

- **NEXT — Phase 6 (Option B):** intake a **second, differently-structured (non-gettext)
  lockit** (`.xlsx`/`.csv`/`.ftl`/`.json`) to test whether the library made intake faster —
  does `gettext-detection` correctly say "not gettext", does `review-dossier` speed GATE 1,
  do new formats seed new library assets? See `docs/next-session-kickoff.md`.

## Policy added this session (from Marcin's guidance)
- **Memory is two-layer + hardened.** `vault/02_SYSTEM/memory-policy.md`: volatile
  Claude memory is staging only; the ritual (`/retro`) hardens durable facts into
  git-tracked SOPs/library/CLAUDE.md. `/wake` now surfaces un-hardened memory.
- **Document the *why* + harden working code.** Scripts carry plain-language rationale
  for less-capable agents; validated, broadly useful code is promoted to
  `vault/library/` principles. Folded into `/toolkit`, `/retro`, `schema.md`.
- **CLAUDE.md pointer to memory-policy + why-docs — APPLIED** (session 000 retro). No
  cornerstone changes pending.

## North-star goals (design toward; raise at decision points)
1. **Cheaper models can do the job.** Profiles, conventions, and library must be
   explicit, deterministic, model-agnostic — the scripts carry the load, the model
   reads the chart. Bias every artifact toward being followable by a small model.
2. **Portable to an API runner.** Keep steps, prompts, and contracts clean enough to
   lift out of interactive Claude Code into code orchestrating LLMs via API.
3. **Telemetry & token/cost awareness.** Metering seam reserved in `schema.md` (design
   only so far). Wire it so each pipeline step can report calls/tokens/cost, enabling
   deliberate cheap-vs-expensive routing.
4. **Public release.** Intended to be shared publicly under a licence that invites
   others to pick up the idea. **Open decision — licence not yet chosen** (candidates:
   Apache-2.0 for code + CC-BY-4.0 for docs; or MIT; or a source-available/ethical
   licence). Decide before first public push. No client data ever ships (`data/**`,
   `sources/**` gitignored).

## Hard gates (never pass without Marcin's confirmation)
- **GATE 0** — confirm which located files are the lockit (Mode B intake).
- **GATE 1** — confirm/correct inferred structure before documenting.
- **GATE 2** — review generated toolkit before packaging as a skill.
