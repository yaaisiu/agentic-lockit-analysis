---
description: Session-end ritual — harden volatile memory, propose library promotions (approve → apply), write session note + next-session kickoff.
argument-hint: [lockit-name]
allowed-tools: Read Write Edit Glob Grep Bash
---

# /retro

Close the session so the next one resumes cleanly and the system is a little smarter.
Guardrail: **never silently rewrite CLAUDE.md, a skill, or `vault/library/`** — propose,
Marcin approves, then apply, committed citing the session/lockit (spec §8).

## 1. Harden volatile memory (L1 → durable L2)
Per `vault/02_SYSTEM/memory-policy.md`: review Claude Code's volatile project memory and
this session's new facts. Route each durable fact to its git-tracked home — CLAUDE.md
(principles), `.claude/commands/` (SOPs), `vault/library/` (conventions/heuristics/
templates), `vault/dev/` (state/vision). Anything living *only* in volatile memory that
matters must be promoted. Test: if the volatile dir were wiped, nothing important is lost.

## 2. Propose promotions to the library (PROPOSALS ONLY)
Review what this session learned. Propose — don't silently write — any:
- **convention** recurring/reusable across files → `vault/library/conventions/<id>.md`
- **heuristic** the inference step should consult → `vault/library/heuristics/<id>.md`
- **script template** that will help the next file → `vault/library/script-templates/<id>.py`
Promote **the *why* alongside the code**: a validated, broadly useful script becomes a
template *and* carries a plain-language rationale so a less-capable agent can reuse it.
Never put lockit *content* into the library. Present each as a proposal with rationale;
Marcin approves; then apply.

## 3. Update state + write the session note
- Update `vault/dev/STATE.md` (phase, active lockit, next step; refresh goals if needed).
- Write `vault/dev/sessions/NNN-<slug>.md` (schema in `02_SYSTEM/schema.md`): what
  happened, decisions at each gate, what was hardened, promotions proposed/applied, open
  threads. Fill the `telemetry` block if data is available; else leave nulls (seam reserved).

## 4. Write the next-session kickoff
Write/refresh `docs/next-session-kickoff.md` — a ready-to-paste prompt: current state,
the immediate next gated step, and either "refine this toolkit" or "intake a second,
differently-structured file/repo to test whether the library made it faster" (spec Phase 6).

## 5. Commit (if Marcin approves)
Stage vault + `.claude/` + scripts changes (never `data/**`/`sources/**`) and commit with
a message citing the session/lockit. `git push` is `ask`-gated — confirm first.
