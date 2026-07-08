# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we
> are + proposes the next step.
>
> Context: s000 built the system + mapped Wesnoth (gettext). s001 proved it corpus-wide +
> cross-locale QA. s002 ran the generality test on Veloren (Fluent). **s003 closed the tabular
> anatomy: A Dark Forest (Godot CSV) end-to-end — key column, context column, many-locales,
> CSV quoting, JSON-array cells.** See `vault/dev/sessions/003-a-dark-forest-tabular-csv.md`.

## Where we are
- **Three lockits, three formats.** Wesnoth (gettext) · Veloren (Fluent) · **A Dark Forest
  (Godot CSV)**. Same pipeline, same gates. A Dark Forest: 676 rows × 10 cols, 8 scripts, 31
  tests, skill `lockit-a-dark-forest-toolkit`; found 3 real upstream defects (malformed `es`
  arrays) + a dup key; `ua` = only partial locale.
- **The library keeps paying off** as a recogniser/ruler-out. New assets promoted at s003 retro
  (if approved): convention `csv-tabular`, heuristic `csv-detection`, template
  `csv_parse_template.py`; `construct-origin-labeling`/`outlier-hunting`/`cross-locale-invariants`
  gained `a-dark-forest` in also_seen.

## The remaining gap — the ONE still-untested anatomy: a CHAR-LIMIT / max-length column
Three formats are now mapped, but **no lockit has had a char-limit/max-length column** — the
spec §7 `find_over_limit.py` script has still never had data. Three scouts in s003 failed to
find a clean, verifiable source (Godot CSV lacks it; the one open sheet is 410-gone; LocJAM's
xlsx was board-game maps, not a lockit). This is the deliberate gap to close next.

### Step 0 — source a char-limit candidate (bring 2–3 to GATE 0)
Selection criteria (same discipline):
- **Licence-clean** — open-source or public; verify the **content** licence, not just the repo's
  code licence (s003 lesson: a "MIT" game had CC-BY-NC-SA loc content).
- **Has a real char-limit / max-length column** — this is the whole point. Likely homes: a
  shipped game `.xlsx` loc sheet, a public loc spreadsheet/template with a "max length"/"limit"
  column, or a console-game loc export (char limits matter most on consoles). Binary `.xlsx`
  parsing would also finally get exercised (we have a working unzip→sharedStrings peek recipe).
- **Tractable size** — profileable in a session.

### If no char-limit source can be found
Fallbacks (pick with Marcin):
- **Go wider on tabular:** Polyglot Master Sheet (CC0, ~25 locales incl. RTL Hebrew + a
  self-documenting `LANGUAGE_DIRECTION` row) — stress the CSV toolkit at 25 locales + RTL.
- **Licence decision** (north-star #4) — still open; pick before any public push.
- **Wire telemetry** (north-star #3) — the metering seam is still design-only.

## Watch specifically for (does the library keep paying off?)
1. Does the new **`csv-detection`** recogniser fire (or correctly *not* fire on xlsx)?
2. Does `csv_parse_template.py` speed the reader, or does xlsx need a new template?
3. Does `construct-origin-labeling` handle a **char-limit column** as a new column role?
4. First real exercise of **`find_over_limit.py`** — build it against actual limit data.

Flow: `/intake <file-or-repo>` → GATE 0 → `/profile` → GATE 1 → `/toolkit` → GATE 2, library first.

## Guardrails (unchanged)
Gates 0/1/2; deny-leaning perms; `data/**`+`sources/**` gitignored; never put lockit content in
`library/` or a skill; propose→approve→apply for library/CLAUDE.md/skills; harden memory at
`/retro`; document the *why*; scripts stay dependency-free; surface upstream defects, never edit
third-party data.
