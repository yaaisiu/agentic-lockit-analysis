# CLAUDE.md — Lockit Cartographer (the hearthstone)

<!-- The cornerstone Claude returns to every session. Auto-loaded by Claude Code. Keep it simple; detail lives in the spec. -->
<!-- changelog: v1 — genesis (Claude Code) -->

## What this is

A human-guided system, running in **Claude Code**, that takes any game **lockit** (the tabular localisation file) — and, by the same method, any tabular dataset — and: maps its structure, **documents** it in this Obsidian vault, and **generates reusable deterministic scripts/skills** to extract and work with its data. **No matter what file we provide, it should build the toolkit and the structured data — guided by Marcin.** It gets better each time, by learning from corrections and from accumulated patterns. See @docs/initial-spec.md.

The system is **scaffolded first, with no lockit**; the lockit is then brought in as the first real step — either a **file** you provide, or a **game repo/folder** the system searches to *locate* the loc files (confirmed by you at GATE 0). It is **not** a translator or the Polish auditor — those are downstream. This is the foundation: turning an unknown file into a documented, queryable, tool-equipped dataset.

## How to work with Marcin (adapt to him — the heart of this file)

- **Language.** Mirror the language Marcin writes in. Polish when he writes Polish; English for specs, code, and deliverables. Don't switch away from the language he chose.
- **Verbosity.** Concise by default. Match the dial he sets — "more", "tl;dr", "just do it". Don't pad.
- **Explain on ask.** Default is *do the thing, then note it briefly*. When he asks **why**, give the full reasoning and trade-offs.
- **Ask sparingly.** One question at a time, and address what you already can first.

## The working principle: discover with the model, extract with scripts

- The **model discovers and judges** — infers column meaning, recognises variables vs control codes, spots conventions, flags ambiguity.
- **Deterministic Python extracts and transforms** — reproducible, fast, free, testable. Once structure is confirmed, write a script, not a per-run LLM call.
- **The scripts and the documentation are the durable artifacts.** The chat is not. Leave every file with a chart (its profile) and a toolkit (its scripts/skill).

## Human guidance is the steering mechanism

Marcin's guidance isn't a fallback — it's how any unknown file becomes tractable. Use plan-and-approve. Three hard gates: **GATE 0** (in repo-intake mode, confirm which located files are the lockit before profiling), **GATE 1** (confirm the inferred structure before documenting), **GATE 2** (review the generated toolkit before packaging). Propose; don't proceed past a gate without his confirmation.

## Memory lives in the vault (and the skills)

This repo holds the memory. Per file: `vault/lockits/<name>/` (profile, structure, variables, open-questions, toolkit). Cross-file: `vault/library/` (conventions, heuristics, script-templates) — the thing that makes the next file faster. **Consult `library/` first** (recognise before re-inferring). **When something important changes, its note changes in the same session.** A provided game repo/folder to search lives in `sources/<name>/`; the acquired lockit file(s) + outputs live in `data/<name>/` (both gitignored — client/third-party data).

## How the system learns

- **From Marcin:** corrections at the gates → captured, then distilled into `library/` so the mistake isn't repeated.
- **From the processes:** recurring patterns and reusable scripts → **promoted** into `library/conventions`, `library/heuristics`, `library/script-templates`.
- **Guardrail:** never silently rewrite `library/`, a skill, or this file. Promotions are **proposed at reflection, approved by Marcin, then applied** — each committed with the lockit/session id that produced it.

## Security (day one)

Lockits are NDA-bound client data. Deny-leaning `.claude/settings.json` (no `curl`/`wget`, deny reading `.env*`, confine writes to the repo, `ask` before `push` and `git clone`). Prefer a **local** game repo for intake; read sources **read-only** and copy only confirmed loc files into `data/`. **Never put lockit content into `library/` or any shared skill** — the library holds *generalised conventions*, not content. `data/**` and `sources/**` are gitignored. Scripts read/write local files only; no network. Only run skills you/Anthropic authored; our generated skills are trusted only after GATE 2.

## Rituals

Start a session with `/wake` (read this file + the active lockit's notes + `vault/dev/STATE.md`). End with `/retro` (write `vault/dev/sessions/NNN-*.md` + the next-session kickoff). Task commands: `/intake <file-or-repo>` (acquire a lockit), `/profile <lockit>`, `/toolkit`. (Full pipeline: spec §4.)