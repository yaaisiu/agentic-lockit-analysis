---
description: Recon → consult library → infer lockit structure → GATE 1 → document in the vault.
argument-hint: "<lockit-name>"
allowed-tools: "Read Write Edit Glob Grep Bash"
---

# /profile $ARGUMENTS

Turn the acquired lockit `data/$1/` into a documented *chart*. Discover with the model,
but do all file-opening deterministically (bash/Python). **Wait at GATE 1.**

## 1. Recon (deterministic — no guessing)
Open the lockit with Python and report, factually:
- format, encoding; sheets/tabs or files; columns/fields per sheet; row counts;
  delimiters, header rows, merged cells; a few sample rows per sheet.
Write findings to `vault/lockits/$1/structure.md` (schema in `vault/02_SYSTEM/schema.md`).

## 2. Consult the library FIRST (recognise before inferring)
Read `vault/library/conventions/`, `heuristics/`, `script-templates/`. Note any known
convention this file appears to match — cite it rather than re-deriving it.

## 3. Infer the anatomy (LLM judgment — spec §5)
Work the checklist: column/field semantics · string types (type column? key prefixes?
separate sheets?) · key-naming conventions (namespaces, gender/number markers, variants)
· variables & placeholders (every style: syntax, meaning, where, translatable?) ·
numbers (in keys? text? columns?) · control codes & markup · limits/constraints.
**Flag every ambiguity as an explicit question** — do not silently guess.

## 4. GATE 1 — Marcin confirms/corrects
Present: the inferred structure + a numbered list of open questions. Wait for decisions.
Record every decision in `vault/lockits/$1/open-questions.md` (status, decision,
decided_at, gate).

## 5. Document (only after GATE 1)
Write, per the schema:
- `vault/lockits/$1/profile.md` — the data dictionary (`status: confirmed`).
- `vault/lockits/$1/variables.md` — placeholder inventory with detection regexes.
- Update `structure.md` / `open-questions.md`.
Update `vault/dev/STATE.md`. Then hand off to `/toolkit`.

Do **not** write library notes here — promotions happen at `/retro`, proposed and approved.
