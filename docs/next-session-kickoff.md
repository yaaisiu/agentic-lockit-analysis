# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 HoI4 (Clausewitz) — first proprietary lockit. s005 public-release
> prep. s006 went PUBLIC + doc reconciliation. **s007 — the bundle exporter: Cartographer's first
> downstream consumer.**

## Where we are
- **Four lockits, four formats, all gated + tooled.** Plus, new in s007, a **producer** role:
  `scripts/veloren/export_bundle.py` emits a normalized bundle (manifest.json + lines.jsonl) for
  the sibling **Lockit Annotator**, accepted by that project's own importer. Veloren tests 50 → 93.
- **The parser changed and the change was proven, not asserted.** `placeables()` returns
  `(start, end, inner)`; `inventory`/`report`/`validate`/`labels --audit` are byte-identical to a
  baseline captured before the edit. Keep that habit for any future foundation change.
- **Repo is PUBLIC** (`github.com/yaaisiu/agentic-lockit-analysis`). Treat every commit as
  outward-facing. Nothing is pushed yet from s007 — `git push` is `ask`-gated.

## FIRST — 7 library promotions await approval
s007 proposed them; **none are applied**. They are listed with rationale in
`vault/dev/sessions/007-veloren-bundle-exporter.md`. In short: sync the promoted Fluent template's
`placeables()` to spans; a `construct-spans-not-tokens` heuristic; a `byte-stable-artifact`
convention + a `byte_stable_jsonl.py` template; and three updates
(`construct-origin-labeling`, `fluent-ftl`, `outlier-hunting`). Approve/reject each, then apply
and commit citing s007.

## THEN — Marcin's call (no gate mid-flight)
1. **G6 — the converter-GENERATOR skill** (new in the backlog, the biggest idea from s007).
   `export_bundle.py` is a one-off written by hand against one consumer's schemas. G6 inverts it:
   the **consumer publishes an information package** (schemas + a construct-mapping guide) and
   Cartographer *generates* the converter. Open questions are recorded in `vault/dev/backlog.md`.
   Note **F6** (generated-script safety gate) probably gates its output.
2. **Resume lockit work.** A1 (run the prepared cross-locale tools on a real translation — the
   first "our tool caught a real bug in a delivery" report) · the char-limit hunt (F4, the one
   untested §5 anatomy) · a new format (JSON/`.arb`/`.strings`/xliff) · the Polish-audit track.
3. **Security F5/F6** — input hardening (injection-aware profiling) and/or the generated-script
   safety gate. Neither built; F6 is now also a prerequisite for G6.
4. **QA-generators G1/G2** (translator brief, pseudo-loc) or **F7** (doc-freshness check).

## Carried forward from s007
- **Contracts are DRAFT v0.2.** At ratification: re-export and **re-pin the payload sha256** in
  `tests/test_toolkit.py`. Never re-pin reflexively — a moved hash means `source_text` moved.
- **`~/lockit-annotator` is read-only for us.** Marcin is fixing the fixture bug we reported
  (`regenerate.py` hashes `source_id` into `line_id`, contradicting their schema) on that side.
- Per-attribute `line_no` is still the parent entry's line (~4 lines to fix if it ever matters).

## Guardrails
- Proprietary data (HoI4) stays gitignored; committed notes stay synthetic; never a real string ships.
- Library/CLAUDE.md/skill changes are proposed → approved → applied, never silent.
- Bundle output is an extraction artifact → gitignored `data/`. `git push` is `ask`-gated.

## Flow
`/wake` → clear the 7 promotions → pick a track → work it through the gates → commit per verified
unit (attach the proof to the message) → confirm before `git push`.
