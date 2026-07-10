# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 HoI4 (Clausewitz) — first proprietary lockit. **s005 — public
> release prep: licences + attribution, seed universalised (tag `seed-v1-original`), README rewrite
> + Clausewitz field guide published, backlog F5/F6 (security). Pushed to a PRIVATE GitHub repo.**

## Where we are
- **Repo is PUBLIC** (flipped 2026-07-10, s006): `git@github.com:yaaisiu/agentic-lockit-analysis` (main + tag
  `seed-v1-original` pushed). Release artifacts all in place: `LICENSE` (Apache-2.0), `LICENSE-docs.md`
  (CC-BY-4.0), `ATTRIBUTION.md`, rewritten `README.md`, `docs/clausewitz-loc-field-guide.md`.
- **The one thing standing between here and public: Marcin's ~30-min legal sanity check.** Publishing
  is outward-facing + irreversible; do the check first, then flip.
- Four lockits, four formats, all gated + tooled + QA-capable. Library: 3 recognisers, 4 conventions,
  reader templates, origin-labeling + two-tier drift, morphology-location, length-reference.

## THE NEXT SESSION — Marcin's call (no gate mid-flight)
Pick one; all are prepared:

1. **Go public (after the legal check).** Flip the repo to public. Optional polish first: a short
   `CONTRIBUTING.md` / "how to extend the library" note (release-plan deliverable 5, still optional);
   a final skim that skills referencing gitignored `data/…` paths read as *method exemplars* (the
   README already says so). This is the natural close of the release track.
2. **Resume lockit work (the deferred track).** Any of: the **char-limit hunt** (the one untested §5
   anatomy — needs a clean source); a **new format** (JSON/`.arb`/`.strings`/xliff) to keep testing
   library speed-up; **run the prepared cross-locale tools on a real translation** (backlog A1 — the
   first "our tool caught a real bug in a delivery" report); or start the **Polish-audit** track
   (morphology-location makes HoI4 a sharp test case).
3. **Security hardening (F5/F6).** Start the input side (F5: delimit/quote samples at the discover
   step; an injection-pattern scanner over sampled strings) and/or the output side (F6: an AST safety
   linter for generated scripts + a GATE-2 checklist, ideally via a scoped script-reviewer subagent).
   Both are documented in `vault/dev/backlog.md`; neither is built.

## Guardrails carried forward
- **Public flip is irreversible** — legal check first; the push to *public* is the real gate (the
  private push is done). No client data ever ships (`data/**`, `sources/**` gitignored).
- Proprietary data (HoI4) stays gitignored; committed notes stay synthetic; never a real string ships.
- Library/CLAUDE.md/skill changes are proposed → approved → applied, never silent.

## Flow
`/wake` → confirm with Marcin which track (public / lockit / security) → work it through the gates →
commit per unit → `git push` is authorized to the private repo, but **confirm before making the repo
public.**
