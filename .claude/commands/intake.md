---
description: Acquire a lockit — a provided file (Mode A) or a game repo/folder to search (Mode B). Ends at GATE 0.
argument-hint: <file-path | folder-path | git-url>
allowed-tools: Read Glob Grep Bash
---

# /intake $ARGUMENTS

Acquire a lockit into `data/<name>/`. **Security is day-one (spec §9): read sources
read-only; never egress; `data/**` and `sources/**` are gitignored; never copy lockit
content into `library/` or a skill.** Pick a kebab-case `<name>` and confirm it with Marcin.

## Detect the mode from `$ARGUMENTS`

**Mode A — a file (or files).** A path to a `.xlsx/.csv/.po/.json/...` file.
- Copy the confirmed file(s) into `data/<name>/`. Do not open/parse deeply yet — that's `/profile`.
- Confirm with Marcin that this is the intended lockit → this is **GATE 0** for Mode A.

**Mode B — a game repo/folder to search.**
- If a **local folder**: search it **read-only** — do not modify anything in it.
- If a **Git URL**: cloning is **`ask`-gated**. Confirm with Marcin, then clone into
  the gitignored `sources/<name>/`. Never clone without confirmation.
- Search for localisation/lockit files by extension and heuristics:
  `.po` `.pot` · lang `.txt` · `.ftl` · `.properties` · `.strings` · `.resx` · `.json`
  · `.csv` · `.xlsx` (also `.tsv`, `.xliff`, `.arb`, `.yaml` if present).
  Heuristics: locale codes in path/name (`en`, `en-US`, `pl`), folders like
  `loc/`, `localization/`, `lang/`, `strings/`, `i18n/`; header rows with `key`/`source`/
  locale columns; many short strings with placeholder tokens.
- Present the candidates as a table: path · format · size/rows (if cheap to get) · a
  one-line reason each. **Do not profile yet.**

## GATE 0 — Marcin confirms scope

Wait for Marcin to confirm **which** files are in scope. Then copy *only those* into
`data/<name>/`. Record the decision in `vault/lockits/<name>/open-questions.md`
(create the folder). Update `vault/dev/STATE.md` (`active_lockit`, `phase`).

Then hand off to `/profile <name>`.
