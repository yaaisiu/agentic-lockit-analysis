# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 **HoI4 (Clausewitz) — first proprietary lockit; all gates +
> retro; then completeness nodes added (HoI4 source-side + the missing Wesnoth report).**

## THE NEXT SESSION — prepare the repo for a public GitHub release
Full plan in **`docs/release-plan.md`** (decisions locked with Marcin). Not another lockit — a
polish-and-publish session. Three tracks:

1. **Legal/safety gate (do first).**
   - Licence **decided: permissive open source** — **Apache-2.0** (code) + **CC-BY-4.0** (docs) +
     a README **courtesy note** ("free for commercial use; I'd love to hear if you build something
     commercial with it — a request, not a term"). Add `LICENSE`, docs licence, `ATTRIBUTION.md`.
     Recommend a ~30-min legal sanity check before pushing (AI-authorship is fuzzy).
   - Re-run the pre-flight scan (history clean ✓, no PII ✓, settings safe ✓) + the ONE open item:
     **content-licence audit of committed notes** — HoI4 = synthetic ✓; scrub the few tiny real
     A-Dark-Forest fragments (CC-BY-NC-SA); attribute Wesnoth/Veloren (GPL).
2. **Reflective primer pass (the part Marcin most wants).** Diff spec-as-written vs system-as-built
   across s000–s004; fold learned lessons into the SEED so a newcomer gets them free. Known fixes:
   the `CLAUDE.md` → `@docs/initial-spec.md` path bug; bake in the proprietary-vault discipline from
   day one; add "a slice under-samples — audit the full corpus"; foreground the gates + library-first
   loop; refresh "what it's for" with the QA/completeness value. (Details in the release plan.)
3. **README rewrite + "build your own" story.** What it is (discover-with-model / extract-with-
   scripts) → pipeline + gates → quickstart from the three seed files (+ reset-to-seed) → current
   state (4 worked examples + library) → what it's for / not yet → data discipline → licence.
   Ship POPULATED (examples + library as head-start) with a clear seed section. Also publish the
   Clausewitz field guide (`sources/hoi4/research.md`) into `docs/` as an adoption asset.

## Where we are (state)
- **Four lockits, four formats, all gated + tooled**, all with completeness/QA capability now
  (Wesnoth `completeness.py` de 100% / pl 89.2%; Veloren + ADF already had it; HoI4 source-side
  refs + event coverage). Library: 3 recognisers, 4 conventions, reader templates, origin-labeling
  + two-tier drift, `morphology-location`, `length-reference`. Backlog parked in `vault/dev/backlog.md`.
- **North-star #4 (licence) is now DECIDED** (permissive OSS). Still open: telemetry (#3), API-runner
  portability (#2), the char-limit anatomy gap.

## Guardrails carried forward
- **Publishing is outward-facing + irreversible** — do the content audit and get the licence right
  BEFORE any `git push` (push is ask-gated regardless).
- Proprietary data (HoI4) stays gitignored; committed notes stay synthetic; never a real string ships.

## Flow
`/wake` → work `docs/release-plan.md` top-to-bottom (legal gate → primer reflection → README) →
commit per-track → **stop before `git push`; confirm with Marcin** (and ideally after his legal check).
Deferred to a later session: next lockit (char-limit hunt / new format) + the Polish-audit track.
