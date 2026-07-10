# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 HoI4 (Clausewitz) — first proprietary lockit. s005 public-release
> prep (licences, attribution, README, field guide; pushed private). **s006 — went PUBLIC + doc
> reconciliation.**

## Where we are
- **Repo is PUBLIC:** `github.com/yaaisiu/agentic-lockit-analysis` — flipped 2026-07-10 after a clean
  pre-flight. Description ✓, Apache-2.0 ✓, 10 discoverability topics ✓. Marcin does the LinkedIn post
  in another tool. (Cosmetic open item: the "Unknown licence" badge — `LICENSE-docs.md` is prose, not
  verbatim CC-BY text; rename-out-of-glob fix deferred, Marcin's call.)
- **The release track is closed.** Four lockits, four formats, all gated + tooled + QA-capable.
  Library: 3 recognisers, 4 conventions, reader templates, origin-labeling + two-tier drift,
  morphology-location, length-reference. No client data ever ships (`data/**`, `sources/**` gitignored).

## THE NEXT SESSION — Marcin's call (no gate mid-flight)
Pick one; all are prepared:

1. **Resume lockit work (the deferred track).** Any of: the **char-limit hunt** (the one untested §5
   anatomy — needs a clean source); a **new format** (JSON/`.arb`/`.strings`/xliff) to keep testing
   library speed-up; **run the prepared cross-locale tools on a real translation** (backlog A1 — the
   first "our tool caught a real bug in a delivery" report); or start the **Polish-audit** track
   (morphology-location makes HoI4 a sharp test case).

2. **Security hardening (F5/F6).** Input side (F5: delimit/quote samples at the discover step; an
   injection-pattern scanner over sampled strings) and/or output side (F6: an AST safety linter for
   generated scripts + a GATE-2 checklist, ideally via a scoped script-reviewer subagent). Both
   documented in `vault/dev/backlog.md`; neither built.

3. **QA-generators (Theme G) — the "help the process" deliverables.** G1 translator-brief generator
   (auto-produce the reference doc clients never provide — column/construct meanings, rules, and what
   the format *can't* control, e.g. Polish case/gender from morphology-location); G2 pseudo-loc
   generator. High-value, deterministic, stdlib-only.

4. **Hygiene (small):** build **F7** (doc-freshness / repo-truth check) so doc-vs-reality drift like
   s006's stale "private" claims is caught automatically at `/wake` + `/retro`.

## Guardrails carried forward
- Proprietary data (HoI4) stays gitignored; committed notes stay synthetic; never a real string ships.
- Library/CLAUDE.md/skill changes are proposed → approved → applied, never silent.
- The repo is public now — treat every commit as outward-facing; `git push` is `ask`-gated, confirm first.

## Flow
`/wake` → confirm with Marcin which track (lockit / security / QA-gen / hygiene) → work it through the
gates → commit per unit → confirm before `git push`.
