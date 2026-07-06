---
type: session
id: "001"
date: 2026-07-06
lockit: wesnoth
gates_cleared: [post-GATE-2 extension]
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 001 — Wesnoth corpus-wide + multi-language (Option A)

**Goal (Marcin):** finish Wesnoth — run the finished toolkit over the whole corpus, extend
it where the wider net reveals new structure, and get the system "ready for other lockit
ingestion." English-analysis foundation first; localisation is downstream.

## What happened

### Warm-up: `/wake` wasn't registered
The five ritual commands existed in `.claude/commands/` but weren't in the slash registry —
they were created mid-session so the file-watcher never picked them up. Fix: `/reload-skills`
(no restart needed). Also normalised their frontmatter to the documented form. Not a file bug.

### Part 1 — generality across all 32 domains (no re-profiling)
- Ran `report.py` over all 32 `.pot`: **26,312 strings, ids 26,312/26,312 unique, 0
  collisions** — the GATE 1 identity model is lossless at full scale. Anatomy holds.
- The wider corpus revealed structure the 4-domain subset never saw. Extended the toolkit
  (Marcin approved "cover all 3"), all grounded in evidence, single-source-of-truth in
  `po_tokens.py`:
  - **Three markup families**, cleanly domain-separated: Pango (29 game domains), **DocBook**
    (`wesnoth-manual`), **po4a/POD man** (`wesnoth-manpages`). `validate_markup` now
    auto-detects family per string. Discovered the "roff" family is actually po4a POD
    (`B<…> I<…> E<lt>`), not plain roff — corrected the design.
  - **`{brace}`** name-generator grammar (286 occ) and **hex entities** (`&#x`/`&#0x`) added.
  - **Refined `$var`** so a trailing sentence period isn't swallowed (`$version.`→`$version`)
    — this alone killed 6 false cross-locale mismatches.
- Full-corpus markup validation → **1 finding**, a real source defect (`& snow` unescaped in
  a Pango span). 0 false positives.

### Part 2 — multi-language (prepared capability)
- Built `validate_placeholders.py` (cross-locale: named vars / printf / markup / plural
  arity, matched by natural key, compared against post-caret display). de/pl pilot over the 4
  profiled domains found **8 real upstream defects, 0 false positives** (e.g. de `$num`→
  `$number`, pl dropped `$count`, pl `$tag`→`$key`).

### Human-in-the-loop review (`data/wesnoth/session001-review.md`, gitignored)
Marcin filled a tickable dossier. Decisions applied:
- **A1–A4 confirmed** (markup detection, `$var` refinement, `{brace}` reading, `&#0x7B;`=`{`).
- **B1** — unescaped `&`-in-markup downgraded **ERROR → WARN** (engine-tolerated "and").
- **B3** — added `gender/agreement` prefix **family** (12 prefixes) so translators can trace
  all gender/plural mechanics. Resolved T5.
- **B4** — pre-seeded a fuller **DocBook** set; **excluded** names colliding with bare CLI
  slots (`command`, `option`, …) after that collision produced 4 false "unclosed" errors.
- **B2** — de/pl defects are upstream (GPL); we **surface, never fix**. Corpus multi-locale
  sweep **deferred** (English focus).
- **A2 audit** surfaced two rare `$var` constructs (`$(…)` formula, `$x[$i]` index) →
  tracked T7 (safe, imprecise).

## Decisions / gates
No hard gate crossed (GATE 0/1/2 were cleared session 000). This was a **post-GATE-2
extension** of an approved toolkit, reviewed via the dossier before hardening.

## Hardened this session
- Vault notes updated in-session: `profile`, `variables`, `context-prefixes` (regenerated to
  129 prefixes), `open-questions` (T2/T3/T4/T5 resolved; T6/T7 tracked), `toolkit`.
- `STATE.md` refreshed to Phase 6; fixed a stale "awaiting approval" line.
- Tests 10 → **21**, all passing.

## Promotions (proposed in review C1, approved, applied)
- heuristic **`markup-families`** — a lockit string may carry >1 markup system; detect +
  validate per family; beware tag/metasyntax name collisions.
- convention **`cross-locale-invariants`** — what must survive translation, WITH the caveat
  (Marcin) that legitimate add/drop cases exist → flag for review, not auto-"bug".
- script-template **`validate_placeholders.py`** — parameterised cross-locale checker.

## Open threads
- **T6** — corpus multi-locale QA sweep (deferred, post-English).
- **T7** — `$(…)` formula / `$x[$i]` index own token class, only if needed.
- **A3-followup** — name-generator affix order is a localisation-phase concern.
- **Licence** (north-star #4) — still undecided before any public push.
- Next: **Option B** — a second, differently-structured lockit to test library speedup.
