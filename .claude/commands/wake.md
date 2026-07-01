---
description: Session-start ritual — load the cornerstone, active lockit notes, and STATE.
argument-hint: "[lockit-name]"
allowed-tools: "Read Glob"
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

Then summarise: current phase, active lockit (if any), the next gated step, and any
open questions awaiting Marcin. Do not start work past a gate without confirmation.
