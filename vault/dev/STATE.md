---
type: dev-state
updated: 2026-07-02
phase: 5
active_lockit: wesnoth
---

# STATE — you are here

**Phase 0 complete (scaffold built). No lockit intaken yet. Awaiting `/intake`.**

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
- **NEXT — Phase 6 (generality test):** see `docs/next-session-kickoff.md`. Option A: run
  toolkit across all 32 domains + pull pilot `.po` (de/pl) → build `validate_placeholders.py`.
  Option B: intake a differently-structured (non-gettext) lockit to test library speedup.
- **Awaiting approval:** small CLAUDE.md addition (pointer to memory-policy + why-docs).

## Policy added this session (from Marcin's guidance)
- **Memory is two-layer + hardened.** `vault/02_SYSTEM/memory-policy.md`: volatile
  Claude memory is staging only; the ritual (`/retro`) hardens durable facts into
  git-tracked SOPs/library/CLAUDE.md. `/wake` now surfaces un-hardened memory.
- **Document the *why* + harden working code.** Scripts carry plain-language rationale
  for less-capable agents; validated, broadly useful code is promoted to
  `vault/library/` principles. Folded into `/toolkit`, `/retro`, `schema.md`.
- **Proposed CLAUDE.md addition (NOT yet applied — needs approval):** a short pointer to
  the memory-policy + why-docs principle, so the cornerstone references them.

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
