---
type: system-doc
id: memory-policy
status: active
updated: 2026-07-01
---

# Memory policy — two layers, and the hardening ritual

The system's knowledge must survive machines, sessions, and model swaps. Volatile
convenience memory cannot be trusted to do that. So we run **two layers**, and a ritual
that continuously moves durable facts from the volatile layer to the git-tracked one.

## L1 — Volatile memory (staging scratchpad)
Claude Code's per-project memory (`~/.claude/projects/<proj>/memory/`).
- Machine-local, **outside the repo, not versioned, resettable**.
- Fast to write; good for capturing a fact *the moment* it appears so it isn't lost
  mid-session.
- **Never the system of record.** Nothing important may live *only* here.

## L2 — Durable memory (system of record, git-tracked)
Everything in the repo:
- `CLAUDE.md` — the cornerstone: how to work with Marcin, standing principles.
- `.claude/commands/` — the **SOPs** (rituals: `/wake` `/intake` `/profile` `/toolkit` `/retro`).
- `vault/library/` — generalised, client-free conventions / heuristics / script-templates
  (the reusable **system principles**).
- `vault/02_SYSTEM/` — schemas, this policy.
- `vault/lockits/<name>/`, `vault/dev/STATE.md`, `vault/dev/sessions/` — per-file charts,
  state, session logs.

## The hardening ritual (part of `/retro`; surfaced by `/wake`)
1. **Review L1.** Read the volatile memories and this session's new facts.
2. **Route each durable fact to its L2 home:**
   - how-to-work-with-Marcin / standing principle → **CLAUDE.md** (propose; approved).
   - generalised convention / detection rule / reusable script → **`vault/library/`**.
   - a procedure or ritual change → **`.claude/commands/`** (the SOP) or `vault/02_SYSTEM/`.
   - project state / vision / decision → **`vault/dev/STATE.md`** + the session note.
3. **Propose → approve → apply → commit.** Guardrail (spec §8, CLAUDE.md): never
   silently rewrite CLAUDE.md, a skill, or `vault/library/`. Marcin approves; each
   applied change is committed citing the session/lockit that produced it.
4. **Leave a pointer.** The L1 memory can remain as a short pointer to its L2 home, but
   the L2 artifact is now authoritative.

**Test of done:** if the volatile memory dir were wiped, no important knowledge would be
lost — it all lives in git.
