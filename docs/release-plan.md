# Public release plan — Lockit Cartographer → GitHub

> Steer for the next session (s005). Goal: make this repo a clean, welcoming public project that
> anyone can pick up, understand, and run from the three seed files — and improve the primer so a
> newcomer starting cold has an easier job. Decisions below are **locked with Marcin** (2026-07-09).

## Decisions (locked)
- **Licence — permissive open source + courtesy note** (Marcin: "I want it open source"; the seed
  is reproducible from the prompts, so a restrictive licence adds friction and false security).
  - **Code → Apache-2.0** (`LICENSE`). Patent grant + NOTICE for clean attribution. (MIT acceptable
    if Marcin prefers minimal.)
  - **Docs/vault → CC-BY-4.0** (`LICENSE-docs.md` or a header note). Attribution.
  - **README courtesy note** — phrased as *a request, not a licence term*: "Apache-2.0, free for
    commercial use; as a courtesy I'd love to hear if you build something commercial with it —
    open an issue / reach out." Keeps the licence cleanly permissive/OSI.
  - **Get a ~30-min legal sanity check before pushing** (AI-assisted authorship is legally fuzzy;
    the human-authored parts — spec, HITL direction, selection/arrangement — are what's licensed).
- **Repo shape — ship POPULATED + a SEED section.** Publish with the 4 worked lockits (vault notes,
  skills, populated library) as **examples + head-start**, plus a "start your own / reset to seed"
  section. Explain what-is-what and how we got here (provenance). Nothing proprietary ships.

## Pre-flight safety checklist (re-run at release; current status noted)
- [x] **Git history clean** — nothing under `data/`/`sources/` ever committed except `.gitkeep`.
- [x] **No PII / absolute paths** in tracked files (`yasiu071@…`, `/home/yasiu` → 0 hits).
- [x] **`settings.local.json` gitignored**; committed `settings.json` is the deny-leaning example (safe).
- [ ] **Content-licence audit of committed notes** (the one real to-do):
  - HoI4 notes = synthetic/engine-API only ✓ (verified). Keep it that way.
  - **A Dark Forest (CC-BY-NC-SA)** — scrub/minimize the few real illustrative fragments (e.g.
    `"Writing & Narrative"`); keep only keys/tags (identifiers) + synthetic examples.
  - Wesnoth/Veloren (GPL) analysis is shareable **with attribution**.
  - Add **`ATTRIBUTION.md` / NOTICE** crediting all four upstreams + their licences.
- [ ] Confirm skills referencing gitignored `data/…` paths are explained in the README as *method
      exemplars* (a cloner won't have the data — that's expected).

## Deliverables (next session)
1. `LICENSE` (Apache-2.0) + docs licence (CC-BY-4.0) + `ATTRIBUTION.md`.
2. **README.md rewrite** (outline below).
3. **Primer reflective pass** — fixes folded into the seed files (below).
4. Publish the Clausewitz **field guide** (`sources/hoi4/research.md`) into `docs/` — it's
   content-free, cross-game, and a genuinely useful adoption asset (currently gitignored only
   because it sits under `sources/`).
5. (Optional) `CONTRIBUTING.md` / a short "how to extend the library" note.

## README outline (what it is · build your own · how to use · what for)
1. **What it is** — one-liner + the working principle: *discover with the model, extract with
   scripts; the durable artifacts are files (docs + tools), not chat.*
2. **How it works** — the pipeline + the three gates (0 intake / 1 structure / 2 toolkit) +
   library-first (recognise before re-inferring). A diagram or the 5-command loop.
3. **Quickstart — build your own from the three seed files** — `CLAUDE.md`,
   `docs/initial-spec/…-spec.md`, `docs/initial-spec/initial-prompt.md`; then `/wake` →
   `/intake` → `/profile` → `/toolkit` → `/retro`. How to reset to a clean seed (empty
   `vault/lockits/*`, keep or clear `vault/library`).
4. **Current state / worked examples** — 4 lockits, 4 formats (Wesnoth gettext · Veloren Fluent ·
   A Dark Forest Godot-CSV · HoI4 Clausewitz), each with a chart + a tested skill; the library
   recognisers/templates that make the next file faster.
5. **What it's for** — turning an unknown loc file into a documented, queryable, tool-equipped
   dataset; **and** the loc-QA value we can now demonstrate: completeness (translated/fuzzy/
   untranslated), reference integrity (dangling `$key$`), cross-locale placeholder preservation,
   length reference, drift audit. Point at `vault/dev/backlog.md` for where it's headed.
6. **What it's NOT (yet)** — not a translator, not the Polish auditor; it's the foundation.
7. **Security / data discipline** — `data/`/`sources/` gitignored; never commit client strings;
   proprietary-vault discipline; only run trusted skills. **Prompt-injection awareness (must-have):**
   lockit content is *untrusted external text* fed to an LLM at the "discover with the model" step,
   so a crafted string can attempt to hijack the model — anyone running this must be aware. State
   the risk plainly and name what mitigates it (deterministic scripts do the bulk work; deny-leaning
   permissions; human gates). See backlog **F5** for the hardening roadmap.
8. **Licence** + the courtesy note.

## Primer reflective pass — make onboarding easier (spec-as-written vs system-as-built)
Read `initial-prompt.md`, the spec, `CLAUDE.md`, and sessions 000–004; fold these learned lessons
back into the SEED so a newcomer gets them for free:
- **Fix the path bug:** `CLAUDE.md` references `@docs/initial-spec.md`, but the file is
  `docs/initial-spec/lockit-cartographer-spec.md`. (First thing a newcomer hits.)
- **Bake in the proprietary-vault discipline from day one** — committed notes = synthetic examples;
  real content only in the gitignored dossier. We only learned this at HoI4 (s004); a newcomer with
  NDA data on file #1 would trip. Belongs in the spec + CLAUDE.md (see [[proprietary-vault-discipline]]).
- **Add the recurring principle: "a slice under-samples — audit the full corpus."** It bit us on
  both the drift audit and reference integrity; state it once as a rule.
- **Foreground the crown jewels** — the gates + library-first loop are the core value but are a bit
  buried in the spec; lift them into the primer/README front matter.
- **Refresh "what it's for"** — the spec framed it as map/document/tool; the QA/completeness/
  reference-integrity value is now demonstrable and should be named as an outcome.
- Sanity-check the spec's assumptions against 4 lockits: what did we over-specify / under-specify?
  (e.g. the char-limit column is still the one untested §5 anatomy — say so honestly.)
- Consider a one-line "two-tier drift audit" + "origin-labeling" mention so the library's maturity
  is discoverable from the seed.

## Deferred (post-release, unchanged)
Lockit-target options still open for a later session: char-limit hunt (last untested §5 anatomy),
a new format (JSON/`.arb`/`.strings`/xliff), the downstream Polish-audit track. North-stars still
open besides the licence (now decided): telemetry wiring (#3), API-runner portability (#2).
