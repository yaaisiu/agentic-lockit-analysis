# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we
> are + proposes the next step. (Pasting is only a fallback for a fresh clone / API runner.)
>
> Context: Session 000 built the system + mapped Wesnoth (gettext). Session 001 proved it
> corpus-wide + built cross-locale QA. **Session 002 ran the generality test: intook a second,
> differently-structured lockit — Veloren (Fluent `.ftl`) — end-to-end (intake→profile→toolkit),
> and swept all 39 locales for technical defects.** See `vault/dev/sessions/002-veloren-fluent-intake.md`.

## Where we are
- **Two lockits done, two formats.** Wesnoth (gettext) + Veloren (Fluent). Same pipeline, same
  gates. Veloren: 4,241 messages, 9 scripts, 50 tests, skill `lockit-veloren-toolkit`, and a
  cross-locale report (`data/veloren/technical-defects.md`, 81 real defects / 0 false positives).
- **The library paid off** as a recogniser/ruler-out; Wesnoth's gender concept transferred to
  Fluent's `.fem/.masc/.neut`. New reusable assets were **proposed at retro** (see below).
- **New capability this session:** origin-labeling (`fluent`/`project`/`unknown`) + a drift
  audit that catches constructs unknown to our system (it found the `enum` attribute role).

## Retro promotions — pending Marcin's approval (propose→approve→apply)
If not yet applied, decide these first (they make the NEXT file faster):
1. convention `fluent-ftl` · 2. template `ftl_parse_template.py` · 3. heuristic
`construct-origin-labeling` · 4. heuristic `outlier-hunting` · 5. update `cross-locale-invariants`
(engine-supplied agreement vars; unsound positional match on random-pick arrays).

## The point of next session — the ONE untested anatomy: TABULAR with columns
Both lockits so far are **keyed** (one string per key, one file per locale). Neither exercised
the §5 anatomy a real UI lockit has: an explicit **key column**, **char-limit / max-length
columns**, **metadata columns** (context/screen/notes), **many locales as columns in one file**,
and **CSV/XLSX quoting/escaping** failure modes. That's the deliberate gap to close next.

### Step 0 — source a good tabular candidate (bring 2–3 to GATE 0)
Selection criteria (same discipline as before):
- **Licence-clean** — open-source game or public dataset (no NDA data for a generality test).
- **Genuinely tabular** — a real `.xlsx`/`.csv` with a key column + locale columns; **bonus** if
  it has char-limit/context columns (the part still untested). Session-002 sourcing already
  surfaced **With Flying Colors** (MIT, Godot CSV, key + 7 locale cols, ~37 rows) as a small
  clean example — Marcin wanted *"a bit more data than Flying Colors"*, so scout for a larger one
  (Godot CSVs, a public loc spreadsheet, or a game shipping an `.xlsx`).
- **Tractable size** — enough rows/columns to be interesting, profileable in a session.

### Watch specifically for (does the library keep paying off?)
1. `gettext-detection` says *not gettext*; is there a **`fluent-detection`/`csv-detection`** gap?
2. Does `review-dossier` speed GATE 1 again?
3. Does the new `outlier-hunting` rule catch key/column outliers?
4. Does `construct-origin-labeling` generalise to a tabular format (columns as constructs)?
5. New format → new library assets (a `csv-tabular`/`xlsx` convention, a tabular reader template)?
6. This is the first file that should exercise **`find_over_limit.py`** (char-limit column) — the
   spec §7 script we've never had data for.

Flow: `/intake <file-or-repo>` → GATE 0 → `/profile` → GATE 1 → `/toolkit` → GATE 2, library first.

## Alternatively (if Marcin prefers)
- **Licence decision** (north-star #4) — still open; pick before any public push (Apache-2.0 +
  CC-BY-4.0, or MIT, or source-available).
- **Wire telemetry** (north-star #3) — the metering seam is still design-only.

## Guardrails (unchanged)
Gates 0/1/2; deny-leaning perms; `data/**`+`sources/**` gitignored; never put lockit content in
`library/` or a skill; propose→approve→apply for library/CLAUDE.md/skills; harden memory at
`/retro`; document the *why*; scripts stay dependency-free where possible; surface upstream
defects, never edit third-party data.
