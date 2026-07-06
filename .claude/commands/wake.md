---
description: Session-start ritual — load the cornerstone, active lockit notes, and STATE.
argument-hint: [lockit-name]
allowed-tools: Read Glob
---

# /wake

Orient at the start of a session. Do this, then give a 3–5 line "you are here" summary.

1. Read `CLAUDE.md` (the cornerstone) if not already in context.
2. Read `vault/dev/STATE.md` — current phase, active lockit, next step, north-star goals.
3. Read `vault/02_SYSTEM/schema.md` — the note contracts you'll write against.
4. If an active lockit exists (from STATE, or `$1` if given), read its notes:
   `vault/lockits/<name>/` — `profile.md`, `structure.md`, `variables.md`,
   `open-questions.md`, `toolkit.md` (whichever exist).
5. Skim `vault/library/` (conventions, heuristics, script-templates, glossary) so you
   **recognise** known patterns before re-inferring on any new file.
6. Read the most recent `vault/dev/sessions/NNN-*.md` for immediate context.
6b. Read `docs/next-session-kickoff.md` if it exists — it holds the proposed next step
   written by the previous `/retro`. This is the steer for *what to do now* (Marcin can
   override). No pasting needed; `/wake` pulls it in.
7. Skim Claude Code's **volatile** project memory (L1). Per
   `vault/02_SYSTEM/memory-policy.md`, treat it as staging: note anything important that
   lives *only* there and isn't yet hardened into a git-tracked artifact — flag it for
   hardening at `/retro`.

Then summarise: current phase, active lockit (if any), **the proposed next step (from the
kickoff)**, any open questions awaiting Marcin, and any un-hardened memory. Do not start
work past a gate without confirmation.
