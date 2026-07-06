# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we
> are + proposes the next step. (Pasting is only a fallback for a fresh clone / API runner.)
>
> Context: Session 000 built the system + mapped the Wesnoth lockit (4-domain subset).
> Session 001 confirmed the anatomy **corpus-wide (32 domains)**, extended the toolkit
> (3 markup families, `{brace}`/hex classes, refined `$var`, gender/agreement prefixes), and
> built the cross-locale `validate_placeholders.py` (de/pl pilot). See
> `vault/dev/sessions/001-wesnoth-corpus-wide-multilang.md`.

## Where we are
- **Wesnoth is done as the English-analysis foundation.** Toolkit runs over all 32 domains,
  0 identity collisions; 21 tests pass; markup validates 0-error/1-warn; vault fully updated.
- **Library now carries 3 cross-file assets from this work** (recognise before re-inferring):
  heuristic `markup-families`, convention `cross-locale-invariants`, template
  `validate_placeholders.py` — plus session 000's `gettext-po`, `inline-context-prefix`,
  `list-grammar-cldr`, `gettext-detection`, `review-dossier`, `po_parse_template`.
- Multi-language is a **prepared capability**, intentionally not the current focus.

## The point of next session — prove the library pays off (spec Phase 6, Option B)
**Intake a second, differently-structured (non-gettext) lockit** and measure whether the
accumulated library made intake faster. Good candidates: a `.xlsx`/`.csv` UI lockit (has the
key/limit columns Wesnoth lacked), or `.ftl`/`.json`/`.resx`.

### Step 0 — first, find a good example lockit (like we did with Wesnoth)
Before profiling, source a suitable candidate together (Marcin, s001). Selection criteria:
- **Licence-clean** — an open-source / permissively-licensed game or a public dataset, so we
  can work with real data (Wesnoth was GPL). No NDA data for this generality test.
- **Genuinely different structure** — ideally *tabular with columns* (a real `.xlsx`/`.csv`
  UI lockit with key + char-limit + locale columns) so it stresses the §5 anatomy parts
  gettext never exercised. Avoid another gettext game (that wouldn't test generality).
- **Tractable size** — enough structure to be interesting, small enough to profile in a session.
- Intake **Mode B** (point at a repo/folder, locate loc files) is fair game, as with Wesnoth.
Bring 2–3 options to GATE 0; confirm scope before profiling.

Watch specifically for:
1. Does **`gettext-detection`** correctly say *"not gettext"* and stop us re-inferring?
2. Does the **`review-dossier`** heuristic make GATE 1 faster to confirm?
3. Does **`markup-families`** correctly recognise the new file's markup (or absence)?
4. Does the new format **seed new library assets** (a new convention/heuristic/template)?
5. Does `po_parse_template` NOT fit (as expected) → what's the new reader shape?

Flow: `/intake <file-or-repo>` → GATE 0 → `/profile` → GATE 1 → `/toolkit` → GATE 2, using
the library first at every step. This is the real generality test the whole system was built
to pass.

## Alternatively (if Marcin prefers)
- **T6** — run `validate_placeholders` as a corpus multi-locale QA sweep (more locales / all
  32 domains) and save a report. (We surface upstream defects, never fix GPL data.)
- **Licence decision** (north-star #4) — pick before any public push (Apache-2.0 + CC-BY-4.0,
  or MIT, or source-available). Still open.

## Guardrails (unchanged)
Gates 0/1/2; deny-leaning perms; `data/**`+`sources/**` gitignored; never put lockit content
in `library/` or a skill; propose→approve→apply for library/CLAUDE.md/skills; harden memory
at `/retro`; document the *why*; scripts stay dependency-free where possible.
