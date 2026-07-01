---
type: dev-state
updated: 2026-07-01
phase: 0
active_lockit: none
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

## Next
- **Phase 1 — Intake → GATE 0.** Marcin brings the lockit: a file (Mode A) or a game
  repo/folder to search (Mode B). Then recon → infer → GATE 1.

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
