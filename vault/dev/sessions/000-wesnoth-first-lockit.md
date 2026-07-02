---
type: session
id: "000"
date: 2026-07-02
lockit: wesnoth
gates_cleared: [GATE 0, GATE 1, GATE 2]
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 000 — scaffold + first lockit (Wesnoth)

Started 2026-07-01, closed 2026-07-02. First run of the full pipeline: built the system,
then mapped one lockit end-to-end. Mission (Marcin): a system that helps *developers* handle
localization with **awareness of the craft and detail** — Wesnoth first (English source),
growing to more languages + more analysis modes.

## What happened (Phases 0–5)
- **Phase 0 — scaffold.** Repo/vault skeleton (spec §6), deny-leaning `.claude/settings.json`
  (dropped spec's `Write(/**)`/`Edit(/**)` deny — would block all in-repo writes; verified
  against current Claude Code docs), commands `/intake /profile /toolkit /wake /retro`,
  `schema.md` (+ telemetry seam). `git init`, first commit.
- **Guidance hardened into SOPs (Marcin):** two-layer **memory policy** (volatile = staging;
  harden into git) → `02_SYSTEM/memory-policy.md`, `/retro` step 1, `/wake` step 7;
  **document the *why* + promote validated code** → `/toolkit`, `/retro`, `schema.md`.
- **Phase 1 — intake (Mode B).** Sparse/shallow clone of `wesnoth/wesnoth` `po/` →
  gitignored `sources/`. **GATE 0:** scope = 4 `.pot` (English source).
- **Phase 2 — recon + infer → GATE 1.** Delivered as a **review dossier**
  (`data/wesnoth/gate1-review.md`); Marcin verified each claim against `file:line`. Two
  research subagents (Claude Code config; gettext/Wesnoth mechanics) informed it.
- **Phase 3 — document.** `profile.md` (confirmed), `structure.md`, `variables.md`,
  `context-prefixes.md` (script-generated 105-prefix registry), `open-questions.md`.
- **Phase 4/5 — toolkit → GATE 2 → package.** 8 scripts in `scripts/wesnoth/` (parser,
  tokens, list_placeholders, list_context_prefixes, extract_by_type, validate_markup,
  report, tests). **10 tests pass.** Packaged as `lockit-wesnoth-toolkit` skill; indexed in
  `toolkit.md`. Poking round (SI prefixes, list grammar, T1) confirmed with Marcin.

## Key decisions (evidence in open-questions.md / gate1-review.md)
- **Identity:** `(domain, msgctxt, msgid[, plural])` + sha1 internal id; every field
  preserved (nothing merged). Driven by evidence: 60% of strings have neither `^`-prefix nor
  `#.id`; `(domain,msgid)` unique 5,258/5,258.
- **Corrections caught at review:** `male^`/`gender^` exist; escapes `\n \t \" \\`; `&` were
  Pango entities. **T1 resolved:** dotted vars = runtime WML object properties; value-level
  cross-domain dependency via inserted localized nouns (agreement hazard).
- **Data size:** subset ≈105k tokens; full corpus ≈520k → corpus work is scripted, LLM for
  judgment (cost-aware routing, north-star #3).

## Memory hardened (L1 → L2)
Volatile memories (project-vision, licence discipline, document-why, memory-hardening) are
all reflected in git-tracked artifacts (STATE goals, CLAUDE.md security, memory-policy.md,
the SOP commands). Nothing important lives only in volatile memory.

## Promotions applied (library gains — success criterion #4, exceeded)
- conventions: `gettext-po` (standard gettext), `inline-context-prefix`, `list-grammar-cldr`.
- heuristics: `gettext-detection`, `review-dossier`.
- script-template: `po_parse_template.py` (dependency-free PO reader; verified on real files).

## Proposed, NOT yet applied (needs Marcin)
- **CLAUDE.md addition** — a 2-line pointer to `memory-policy` + the *why-docs* principle.
  Left unapplied per the guardrail (don't silently edit the cornerstone).

## Open threads
- Tracked T2 (command-help metasyntax), T3 (help markup), T4 (prefix registry growth).
- `validate_placeholders.py` deferred until pilot `.po` languages.

## Telemetry note (seam, north-star #3)
Session-level token/cost not yet metered (nulls above). Only metered figures this session:
research subagents' output tokens ≈ 98.5k (config) + 28.9k (gettext). Wiring per-step
metering is a future task; the seam is reserved in `schema.md`.
