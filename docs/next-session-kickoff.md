# Next-session kickoff

> **You don't need to paste this.** Just run `/wake` at the start of the next session —
> it reads this file automatically (along with CLAUDE.md, STATE.md, the active lockit's
> notes, and the library) and will summarise where we are + propose the next step.
> (Pasting is only a fallback for environments without the `/wake` command, e.g. a fresh
> clone or an API runner.)
>
> Context: Session 000 built the system and mapped the **Wesnoth** lockit (English source,
> 4-domain subset) end-to-end. See `vault/dev/sessions/000-wesnoth-first-lockit.md`.

## Where we are
- Toolkit is built, tested (10 passing), packaged, documented. GATE 0/1/2 cleared.
- Library seeded: conventions `gettext-po`, `inline-context-prefix`, `list-grammar-cldr`;
  heuristics `gettext-detection`, `review-dossier`; template `po_parse_template.py`.
- One item awaiting approval: a small **CLAUDE.md addition** (pointer to memory-policy +
  why-docs). Apply if Marcin approves.

## The point of next session — prove the loop pays off (spec Phase 6)
Pick with Marcin:

**Option A — widen Wesnoth (generality within one lockit).**
1. Run the *finished* toolkit across **all 32 textdomains** with no re-profiling
   (`python3 scripts/wesnoth/report.py sources/wesnoth/po/*/*.pot` — or copy the rest into
   `data/`). Confirm the anatomy holds; watch for new `^` prefixes (T4), new markup, new
   metasyntax (T2/T3).
2. Pull **2–3 pilot `.po` languages** (e.g. `de`, `pl`) for the 4 domains and build+test the
   deferred **`validate_placeholders.py`** (cross-locale `$var`/`^`/`%d`/plural consistency,
   markup balance on translations). This starts the multi-language goal.

**Option B — second, differently-structured lockit (the real generality test).**
Intake a non-gettext lockit (e.g. a `.xlsx`/`.csv`/`.ftl`/`.json` game loc file) and measure
whether the library made it faster — does `gettext-detection` correctly say "not gettext",
does `review-dossier` speed GATE 1, does a new format seed new library assets?

**Recommendation:** A first (cheap, proves corpus-scale + starts multi-language), then B.

## Guardrails (unchanged)
Gates 0/1/2; deny-leaning perms; `data/**`+`sources/**` gitignored; never put lockit content
in `library/` or a skill; propose→approve→apply for library/CLAUDE.md/skills; harden memory
at `/retro`; document the *why*; scripts stay dependency-free where possible.
