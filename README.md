# Lockit Cartographer

A human-guided system, running in **Claude Code**, that takes any game **lockit** (a
tabular localisation file) — or any tabular dataset — and:

1. **maps** its structure (columns, string types, key conventions, variables, control
   codes, limits),
2. **documents** it in an Obsidian vault (the *chart*), and
3. **generates reusable deterministic Python scripts**, packaged as Claude Code skills
   (the *toolkit*), so any later session can query the file cleanly.

It gets better each time by promoting recurring patterns into a cross-file **library**.

## Principle

> **Discover with the model; extract with deterministic scripts.**
> The LLM infers and judges structure and *writes* the tools; Python *runs* them —
> reproducibly, for free, forever after. The scripts and docs are the durable
> artifacts; the chat is not.

## Design goals

- **Cheaper models can follow it.** Artifacts are explicit and model-agnostic.
- **Portable to an API runner.** Steps and contracts are clean enough to lift into code.
- **Cost-aware.** A telemetry seam is reserved so each step can report tokens/cost.

## Layout

- `CLAUDE.md` — the cornerstone (auto-loaded each session).
- `.claude/` — permissions, commands (`/intake` `/profile` `/toolkit` `/wake` `/retro`),
  skills, subagents.
- `vault/` — the memory: per-lockit notes (`lockits/`), the cross-file `library/`,
  dev state and session logs, and `02_SYSTEM/schema.md`.
- `scripts/` — generated per-lockit extraction scripts.
- `data/`, `sources/` — **gitignored**: acquired lockits and game repos to search.
  Client/third-party data never leaves the machine.

See `docs/initial-spec/` for the full spec.

## Status

Proof of concept. Scaffold complete; awaiting first lockit intake.

## Licence

Not yet chosen — this project is intended for public release under a licence that
invites others to build on the idea. **No client data is ever committed.**
