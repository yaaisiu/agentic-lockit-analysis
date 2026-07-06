---
description: Generate + test deterministic extraction scripts for the profiled lockit → GATE 2 → package as a skill.
argument-hint: <lockit-name>
allowed-tools: Read Write Edit Glob Grep Bash
---

# /toolkit $ARGUMENTS

Turn the confirmed profile of `$1` into tested, reusable tools. Requires a
`status: confirmed` `profile.md` (GATE 1 cleared). **Wait at GATE 2.**

## 1. Generate scripts (deterministic Python; local files only, no network)
Base them on `vault/lockits/$1/profile.md`. Start from `vault/library/script-templates/`
where one fits (adapt, don't reinvent). Typical set (spec §7):
- `profile_lockit.py` — recon, codified.
- `list_placeholders.py` — inventory: each placeholder style, counts, which keys.
- `extract_by_type.py` — pull strings of a given type (prefix/type-col/sheet).
- `find_over_limit.py` — strings exceeding their char limit.
- `validate_placeholders.py` — cross-locale placeholder consistency.
- (add `gender_pairs.py`, `export_subset.py`, etc. as the profile warrants.)
Write them to `scripts/$1/`. **Every script header explains the *why*** — the reasoning
and assumptions behind how it's built — in plain language a *less-capable agent* can
follow and reproduce, not just what it does. Cite the profile + GATE 1. Rationale-first
comments are a deliverable, not decoration (see `vault/02_SYSTEM/memory-policy.md`).

## 2. Run + test each on the ACTUAL lockit
Run every script against `data/$1/<file>`. Show Marcin real output (counts, samples).
Fix until each runs correctly and deterministically. A tool isn't real until it's run.

## 3. GATE 2 — Marcin reviews the toolkit
Present each script: what it does, example invocation, actual output. Refine per feedback.
**Only trust/package generated skills after GATE 2** (spec §9).

## 4. Package (after GATE 2)
- Create `.claude/skills/lockit-$1-toolkit/SKILL.md` — frontmatter `name` +
  `description` (tell Claude *when* to use it: extract/inventory/validate for `$1`).
  Body: point to `vault/lockits/$1/profile.md`, list each script's invocation, and note
  "if structure changed, re-profile before trusting these."
- Index the toolkit in `vault/lockits/$1/toolkit.md`.
- (Optional) expose common queries as `/lockit:*` slash commands.
Update `vault/dev/STATE.md`. Then run `/retro` — where validated, broadly useful scripts
(with their *why*) are proposed for promotion to `vault/library/script-templates/` so the
next file starts from a template, not a blank page.
