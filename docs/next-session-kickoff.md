# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext) built the system. s001 corpus-wide + cross-locale QA. s002
> Veloren (Fluent). s003 A Dark Forest (Godot CSV) — closed the tabular anatomy. **s004 HoI4
> (Paradox Clausewitz pseudo-YAML) — the first proprietary lockit; biggest yet. All gates cleared,
> toolkit packaged, retro applied.**

## Where we are
- **Four lockits, four formats, all gated + tooled.** Wesnoth · Veloren · A Dark Forest · **HoI4**.
  The library now has **three recognisers** (`gettext-detection`, `csv-detection`,
  **`clausewitz-detection`**), four format conventions, reader templates for each, the
  origin-labeling + two-tier-drift machinery, `outlier-hunting`, `cross-locale-invariants`, and
  two new cross-lockit heuristics from s004: **`morphology-location`** and **`length-reference`**.
- **HoI4 is done:** skill `lockit-hoi4-toolkit` (8 scripts, 35 tests, drift = 0 across all 206
  files / 129,087 entries). Proprietary discipline held: committed vault notes use synthetic
  examples; real content stays in the gitignored dossier ([[proprietary-vault-discipline]]).
- **No gate is mid-flight.** Next target is Marcin's call.

## Options for the next target (pick one at wake)
1. **Char-limit hunt (the last untested §5 anatomy).** Still no lockit with a real
   `max_length`/`char_limit` column — `find_over_limit.py` was never built; `length-reference` is
   only the soft workaround. Needs a dedicated source hunt (a UI/mobile lockit — `.arb`, an Unreal/
   Unity CSV with a length column, an xliff with `maxwidth`). This closes the anatomy matrix.
2. **A new differently-structured lockit** (`.json`/`.arb`/`.strings`/`.resx`/`.xliff`) — keep
   testing whether the library makes intake faster (does a recogniser rule in/out; does a template
   fit; what new asset falls out). xliff would also likely bring the char-limit column (folds into 1).
3. **Run the prepared HoI4 cross-locale tools on a real translation** — pull a
   `_l_polish.yml` (or other) locale into `data/hoi4/<lang>/` (gitignored) and run
   `validate_placeholders.py` + `validate.py --length-ref` in earnest. First real cross-locale
   defect report on Clausewitz.
4. **Start the downstream Polish-audit track.** `morphology-location` makes HoI4 a sharp case:
   an engine-delegated format gives a Polish translator little in-loc control over case/number/
   gender agreement — a real, documentable limitation to audit. (This is closer to the project's
   ultimate purpose; the four mapped lockits are the foundation for it.)

**Recommendation:** if the goal is to *complete the anatomy coverage*, do **1** (ideally via an
xliff/`.arb` that also carries a char-limit column, satisfying 1+2 together). If the goal is to
move toward *purpose*, do **3** then **4** on HoI4 (we already own the toolkit).

## Guardrails carried forward
- **Proprietary data (HoI4):** `data/hoi4/**` + `sources/hoi4/**` gitignored; committed notes get
  synthetic examples only; never a real string into `library/`/skills/committed notes.
- **Library-first:** at any new intake, check the three recognisers before inferring.
- North-stars still open: licence choice (#4), telemetry wiring (#3).

## Flow
`/wake` → pick a target → `/intake <x>` → GATE 0 → `/profile` → GATE 1 → `/toolkit` → GATE 2 →
`/retro`. (For option 3, no intake gate — just add the locale dir and run the prepared tools.)
