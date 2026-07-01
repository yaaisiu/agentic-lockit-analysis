---
description: Session-end ritual — propose library promotions (approve → apply), write the session note + next-session kickoff.
argument-hint: "[lockit-name]"
allowed-tools: "Read Write Edit Glob Grep Bash"
---

# /retro

Close the session so the next one resumes cleanly and the system is a little smarter.

## 1. Propose promotions to the library (PROPOSALS ONLY)
Review what this session learned. Propose — do **not** silently write — any:
- **convention** recurring/reusable across files → `vault/library/conventions/<id>.md`
- **heuristic** the inference step should consult → `vault/library/heuristics/<id>.md`
- **script template** that will help the next file → `vault/library/script-templates/<id>.py`
Present each as a proposal with rationale. **Marcin approves; then apply.** Never put
lockit *content* into the library. Each applied promotion is committed citing the
lockit/session id that produced it (guardrail — spec §8).

## 2. Update state + write the session note
- Update `vault/dev/STATE.md` (phase, active lockit, next step; refresh goals if needed).
- Write `vault/dev/sessions/NNN-<slug>.md` (schema in `02_SYSTEM/schema.md`): what
  happened, decisions at each gate, promotions proposed/applied, open threads.
  Fill the `telemetry` block if data is available; else leave nulls (seam reserved).

## 3. Write the next-session kickoff
Write/refresh `docs/next-session-kickoff.md` — a ready-to-paste prompt for the next
session: current state, the immediate next gated step, and either "refine this toolkit"
or "intake a second, differently-structured file/repo to test whether the library made
it faster" (spec §11 Phase 6).

## 4. Commit (if Marcin approves)
Stage vault + `.claude/` + scripts changes (never `data/**`/`sources/**`) and commit
with a message citing the session/lockit. `git push` is `ask`-gated — confirm first.
