---
type: session
id: 005
date: 2026-07-10
lockit: none
gates_cleared: []
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 005 — Public release prep (executed; pushed to private repo)

Not a lockit session. Worked `docs/release-plan.md` top-to-bottom and shipped the repo to a
**private** GitHub remote. No profiling gates; the "gates" here were Marcin's review points.

## What happened

**Track 1 — legal/safety gate.** Re-ran pre-flight (git history clean, no PII/absolute paths,
`data/`+`sources/` gitignored, `settings.local` gitignored). Content-licence audit of committed
notes: found and scrubbed the single real CC-BY-NC-SA fragment (`"Writing & Narrative"` job title
in a-dark-forest `profile.md`) → synthetic; HoI4 notes re-confirmed synthetic; scripts/tests clean.
Added `LICENSE` (Apache-2.0), `LICENSE-docs.md` (CC-BY-4.0), `ATTRIBUTION.md` (Wesnoth/Veloren GPL,
A Dark Forest MIT-code / CC-BY-NC-SA-content, HoI4 proprietary-not-shipped).

**Track 2 — seed reflective/universalisation pass.** Pinned the pristine originals at annotated git
tag `seed-v1-original` **before** editing. Mined all four toolkits (via an Explore agent) for the
universal patterns and encoded them as a new spec §7 "toolkit shape" section. Reframed spec §3
from "Claude Code" to "any agentic coding harness" (six requirements + a binding table). Foregrounded
the cheap/local-model rationale tied to proprietary/pre-release data. Folded in the day-one
disciplines (proprietary-vault, prompt-injection), "a slice under-samples," the honest char-limit
gap, and the QA outcomes. Fixed the `@docs/initial-spec.md` path bug in CLAUDE.md + initial-prompt.md.

**Track 3 — README + field guide.** Full README rewrite, led by Marcin's why (13-year localisation
specialist; help the process, don't replace translators). Published the content-free Clausewitz
field guide into `docs/` with a provenance header. Added a "how it remembers and improves" section
(wake/retro rhythm + the two learning loops) after Marcin flagged it was missing. Then addressed his
5 inline `[C:]` review comments, and — on a follow-up — surfaced the original-vs-improved seed
distinction as a prominent Quickstart callout (it had been a buried parenthetical).

## Decisions (Marcin)

- **Push authorized to the private repo** `git@github.com:yaaisiu/agentic-lockit-analysis` (main +
  tag `seed-v1-original` pushed). **Repo stays PRIVATE**; public flip deferred to his ~30-min legal
  sanity check (AI-authorship is legally fuzzy; the human-authored spec/direction/arrangement is
  what's licensed).
- **Copyright line** = "Lockit Cartographer contributors" (not his legal name).
- **Author voice** in README = named (Marcin "yasiu" Serkies) + MobyGames + LinkedIn; contact via
  GitHub issues + LinkedIn; added a hire-me note in the courtesy paragraph.
- **Provenance approach** = revise seed in place, preserve originals via git tag, tell readers.
- **New idea → backlog** (not built): a safety gate over the generated scripts (F6).

## Hardened / promoted

- **Memory:** `about-marcin.md` (user memory) — who he is + philosophy + public links.
- **Backlog:** F5 (prompt-injection awareness + defence — input hardening) and F6 (generated-script
  safety gate — output verification; AST linter + sandbox + determinism via the script-reviewer
  subagent the spec anticipates). F5 ↔ F6 framed as two halves of the same defence.
- **No `vault/library/` promotions** — no lockit was profiled; Track 2's generalisations went into
  the seed (spec/CLAUDE.md), which Marcin reviewed and approved.

## Open threads

- **Public flip pending Marcin's legal check** — outward + irreversible; his call.
- Deferred lockit work still parked: char-limit hunt, a new format, cross-locale on a real
  translation (A1), the Polish-audit track.
- F5/F6 security hardening unstarted (documented only).
