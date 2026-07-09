---
type: dev-state
updated: 2026-07-08
phase: 6
active_lockit: hoi4
---

# STATE — you are here

## Active — HoI4 (Clausewitz pseudo-YAML) — GATE 0 + GATE 1 CLEARED, 2026-07-09 (session 004)
- **First proprietary/NDA-class lockit.** Files pre-staged in `sources/hoi4/` (gitignored; 206
  loose English `.yml`, 129,087 entries, all `l_english`, UTF-8-BOM). Gitignore discipline
  verified load-bearing via `git check-ignore`. **Vault notes are committed → synthetic examples
  only, no real strings; real content lives in the gitignored `data/hoi4/gate1-review.md`.**
- **GATE 0 (Marcin confirmed): 5-file slice** in `data/hoi4/en/`, chosen from **measured construct
  density** (not guessed): `focus` (version-int 97%), `events` ([scope]+\n densest), `decisions`
  (£icon), `game_rules` (@TAG carrier), `countries` (plain baseline). **12,867 entries ≈10%.**
- **GATE 1 CLEARED — structure confirmed, vault written** (`profile.md` confirmed, `structure.md`,
  `variables.md`, `open-questions.md`). Anatomy: line-regex `KEY:[VER] "VALUE"` (field-guide regex
  matched **100%**, 0 malformed/multi-line/dup); **two key styles** (underscore `<TAG>_<ideology>_DEF`
  + dotted event `namespace.id.part`); OLD-style dialect `§X…§!` / `£icon` (no closing £!) / `@TAG`
  / `$VAR|fmt$` / `[scope.fn]` (4 sub-forms) / `\n`; **unescaped inner `"`** (greedy first→last
  extraction, lossless); identity = key.
- **Two GATE-1 "look closer" items resolved empirically (all 206):** `$VAR|fmt$` `|` is a **format
  spec (colour AND number-format)**, not colour-only; `KEY:N` is a **version counter** (values
  {0..4}, no key has two Ns), not a selector. Marcin idea E1: **length-ref** (localised vs source
  length) for limit-less lockits → build into validate, propose at /retro.
- **Library payoff:** ✅ `gettext-detection`→not gettext · ✅ `csv-detection`→not csv · reader
  templates (po/ftl/csv) don't fit → **new line-regex reader needed**. Gap: no `clausewitz-detection`
  recogniser, no clausewitz convention/template → propose at /retro (kickoff plan).
- **GATE 2 CLEARED — toolkit built, tested, packaged (Marcin approved 2026-07-09).** 8
  dependency-free scripts in `scripts/hoi4/` (clausewitz_parse, labels, inventory, keys, report,
  extract, validate[+`--length-ref`], validate_placeholders) + dual-mode tests; **35 tests pass.**
  Skill `lockit-hoi4-toolkit` packaged; `toolkit.md` indexes it. **Scaled to all 206** (129,087
  entries): 0 dup keys (T-H2), 0 parse warnings, **tier-1 drift = 0** (registry recognises the
  whole corpus, T-H1); NOTED tail = 25 unbalanced colour spans + 21 escaped `\"`. Key catalogue
  (T-H3): 374 country tags, suffix vocab (`_DEF`/`_ADJ`/`_desc`…), 41 event namespaces, part kinds.
  Design: two-tier audit (drift vs noted); event parts = semi-open vocab (never drift); prepared
  cross-locale tools (`validate_placeholders`, `--length-ref`) run when given a translation.
- **NOW — using the skill to answer Marcin's question:** how does HoI4 handle plurals + gender/
  case inflection? (likely via engine `[scope.Get*]` functions + `_DEF`/`_ADJ` variant keys, not
  in-string selectors — investigating with inventory/keys.)
- **Q-INFL answered (Marcin's question):** HoI4 **delegates morphology to engine functions +
  variant keys**, NOT in-string selectors — `GetNameDef`/`GetAdjective` (~25k), `GetSheHe`/
  `GetHerHis` (~230), `_DEF`/`_ADJ`/`_plural` keys; **no plural system**. Opposite of gettext/
  Fluent. Real downstream limit for Polish. → generalised into heuristic `morphology-location`.
- **`/retro` DONE (2026-07-09). All 9 promotions approved by Marcin + applied:** NEW heuristics
  `clausewitz-detection`, `morphology-location`, `length-reference`; NEW convention
  `clausewitz-pdx-yaml` (per-game profile-as-data, HoI4 = first row); NEW template
  `clausewitz_parse_template.py` (verified on all 206); updated `construct-origin-labeling`
  (+two-tier drift audit, +semi-open-vocab), `cross-locale-invariants` (+token-preservation
  invariant), `outlier-hunting` (+slice-under-sampling) — all +also_seen hoi4. Memory hardened:
  [[proprietary-vault-discipline]]. Session note `004-hoi4-clausewitz-proprietary.md` + kickoff written.
- **NEXT SESSION — Marcin's call.** Options in kickoff: (a) the deferred **char-limit hunt** (the
  one untested §5 anatomy); (b) a new differently-structured lockit (JSON/`.arb`/`.strings`/xliff)
  to keep testing library speed-up; (c) run the prepared HoI4 cross-locale tools on a real
  translation locale; (d) start the downstream **Polish audit** track (morphology-location makes
  HoI4 a sharp test case). No gate is mid-flight.

## Active — A Dark Forest (Godot CSV, TABULAR) — GATE 0 + GATE 1 cleared, 2026-07-07 (session 003)
- **The deliberate gap:** first genuinely **tabular** lockit — explicit key column, context
  column, many-locales-as-columns, CSV quoting/escaping. Closes most of the one untested §5
  anatomy (char-limit column **deferred** — no clean source found; see below).
- **Intake done (Mode B):** sparse+shallow clone of `github.com/TinyTakinTeller/GodotProjectZero`
  → `sources/a-dark-forest/` (gitignored). Scope = `assets/i18n/localization.csv`, copied to
  `data/a-dark-forest/` (+ `.csv.import` metadata + `UPSTREAM-LICENSE.txt`).
- **GATE 0 facts:** header `key,description,en,zh,fr,pt,pl,ua,th,es`; **675 data rows**;
  key + `description` context col + 8 locales (en/zh/fr/pt/pl/ua/th/es); comma-delimited.
- **Licence — CC-BY-NC-SA 4.0 (loc content), NOT MIT.** Only `*.gd` code is MIT; all locales
  (incl. Polish) + English narrative are CC-BY-NC-SA. Usable as gitignored, non-commercial,
  test-only data (never ships, never enters `library/`). Marcin confirmed (open-questions Q0.2).
- **Dropped at intake:** LocJAM 3 xlsx — turned out to be the board-game's printable maps
  (sheets MAP 1/MAP 2/COUNTERS, 50 strings, no key/locale/char-limit columns), not a lockit.
  Clone left at `sources/locjam3/` (gitignored; rm was denied — harmless).
- **Char-limit column STILL UNTESTED** (deferred, Q0.3) — no verifiable clean source found by
  three scouts. Revisit in a future dedicated hunt.
- **GATE 1 cleared — vault written:** `structure.md`, `profile.md` (confirmed), `variables.md`,
  `open-questions.md`. Anatomy: flat CSV 676×10; identity = `key` (`namespace:name`, ~24 ns,
  **1 dup** `ui_label:heart`); `description` = context col + closed 4-tag DSL
  (`[EMPTY]`/`[noun]`/`[verb]`/`[DEPRECATED]`), NOT a locale; 8 locales (`en` src, **`ua` ~half
  untranslated**); **JSON-array cells** (30 keys/207 cells, length = cross-locale invariant);
  placeholders `{0}`–`{3}` + literal `\n`; **no markup** (drift sweep clean); CSV quoting
  exercised (631 comma / 287 quote cells, 0 embedded newlines).
- **Library payoff:** ✅ `gettext-detection` (not gettext) · ✅ `markup-families` (none) · ✅
  `cross-locale-invariants` ({N} + array-length) · ✅ `outlier-hunting` (dup key, variants, arrays)
  · **gap:** no `csv-detection` recogniser + no CSV reader template → propose at `/retro`.
- **GATE 2 cleared — toolkit built, tested, packaged (Marcin approved 2026-07-08).** 8
  dependency-free scripts in `scripts/a-dark-forest/` (csv_parse, labels, report, inventory,
  extract, arrays, validate, validate_placeholders) + tests; **31 tests pass**. Skill
  `lockit-a-dark-forest-toolkit` packaged; `toolkit.md` indexes it.
- **Real defects surfaced (report, don't fix):** 1 dup key (`ui_label:heart`); **3 malformed
  `es` array cells** (`npc_event_options:cat_talk_A{1,2,3}` = `["?"],` stray comma — caught by
  the toolkit, missed by manual GATE-1 scan); `ua` = only genuinely partial locale (256 active
  untranslated; fr/pt/pl "untranslated" were all `[DEPRECATED]`).
- **`/retro` DONE (2026-07-08).** Library promotions applied (Marcin approved all six):
  new convention `csv-tabular`, heuristic `csv-detection`, template `csv_parse_template.py`;
  updated `construct-origin-labeling` (origin `format` generalises `fluent`/`gettext`; +also_seen),
  `outlier-hunting` (+also_seen), `cross-locale-invariants` (+array-length invariant, +also_seen).
  Memory hardened: [[content-vs-code-licence]]. Session note `003-a-dark-forest-tabular-csv.md`
  + kickoff written.
- **NEXT SESSION — HoI4 (Paradox Clausewitz pseudo-YAML), the biggest lockit yet.** Marcin
  deferred the char-limit hunt and pivoted to HoI4. Files staged + research validated at end of
  s003 (see below). Char-limit column remains the deferred §5 gap / fallback.

## Staged — HoI4 (Clausewitz pseudo-YAML) — FIRST PROPRIETARY LOCKIT, researched not yet intaken
- **In `sources/hoi4/` (gitignored):** 206 loose **English** `.yml` (14 MB) + `research.md`
  (Marcin's Clausewitz field guide — content-free, cross-game).
- **Proprietary Paradox content** — first NDA-class lockit; gitignore discipline now load-bearing.
  Never a string into `library/`/skills/committed notes; non-commercial, no dumps.
- **Research validated against the real files (s003 scan):** 206 files all `l_english` +
  **UTF-8-BOM**; **129,087 entries**; format `l_english:` header + `key:VERSION "value"` (version
  optional, ~2%); **not real YAML → line-regex parser, not PyYAML**; the doc's regex matched 100%
  of non-blank/comment lines. Old-style dialect: `§Y…§!` colours (39.5k), `[scope/fn]` (17.9k),
  `$VAR$` (12.7k), `\n` (6.2k), `£icon£` (1.4k), `@TAG` (200), escaped `\"` (21).
- **Plan (in kickoff):** GATE 0 = scope a ~3–5 file **representative slice** (focus + events +
  countries + an icon-rich file) → profile → toolkit on the slice → **scale to all 206** (Wesnoth
  pattern). Later: propose `library/conventions/clausewitz-pdx-yaml` (per-game profile-as-data),
  a `clausewitz-detection` heuristic, a reader template — through the gates.
- **NEXT — `/intake hoi4`** (files staged) → GATE 0 confirm the slice.

---

**Phase 6. Session 002 DONE — the generality test PASSED.** Two lockits now fully mapped +
tooled: Wesnoth (gettext, 32 domains) and **Veloren (Fluent `.ftl`)** — different formats,
same pipeline, GATE 0/1/2 all cleared, 50 tests, skill packaged, all-locale defect report.
The library sped intake (recogniser/ruler-out) and gained new assets. **Next session: intake
a third, still-untested-structure lockit — a TABULAR `.xlsx`/`.csv`** (key + char-limit
columns are the one §5 part neither gettext nor Fluent exercised). Retro promotions pending
Marcin's approval (see below). See `docs/next-session-kickoff.md`.

## Active — Veloren (Fluent `.ftl`) — GATE 0 + GATE 1 cleared, 2026-07-06
- **Intake done (Mode B):** sparse+shallow clone of `gitlab.com/veloren/dev/veloren`
  `assets/voxygen/i18n/` into gitignored `sources/veloren/`. GPL-3.0, licence-clean.
- **GATE 0 scope:** English source = 48 `en/**/*.ftl` + `en/_manifest.ron` in
  `data/veloren/en/` (gitignored). 4,241 messages (0 id collisions), 3,312 attrs, 2 terms.
- **GATE 1 cleared** (dossier `data/veloren/gate1-review.md`, gitignored; Marcin answered
  inline). Vault written: `profile.md` (confirmed), `structure.md`, `variables.md`,
  `open-questions.md`. Anatomy: Fluent keyed tree; identity = unique message id; **3
  attribute roles** (metadata `.desc/.stat` · variant-arrays `.aN` · **gender
  `.fem/.masc/.neut`** ← echoes Wesnoth gender/agreement); inline selectors; `{ $var }`;
  terms; `{""}` empties; Veloren-custom `TAIL()`; no markup family.
- **Library payoff:** ✅ `gettext-detection` (not gettext) · ✅ `markup-families` (no markup)
  · ⚠️ `inline-context-prefix`/`po_parse_template` don't fit → **new Fluent reader** needed.
- **GATE 2 cleared — toolkit built, tested, packaged.** 9 dependency-free scripts in
  `scripts/veloren/` (parser, report, inventory, extract, gender_pairs, validate,
  validate_placeholders, report_all_locales, labels) + tests; **50 tests pass**. Skill
  `lockit-veloren-toolkit` packaged; `toolkit.md` indexes it.
- **T-V5 resolved — LABELING system built (Marcin's rule):** every construct tagged origin
  `fluent`/`project`/`unknown` in documented registry `labels.py`; `--audit` drift catcher
  found a 4th attribute role (`enum`). 4 attribute roles total (metadata/variant/gender/enum).
- **Cross-locale sweep done (all 39 locales):** `data/veloren/technical-defects.md` (gitignored)
  — **81 real technical defects, 0 false positives** (dominant: `$reason` dropped in
  `main-login-banned/kicked` across ~16 locales; `$min_combo` in it axe descs; version skew
  in zh-Hant). FP fixes: engine `*_gender` vars + `.aN` index mismatch excluded.
- **Standing rule captured (→ harden at /retro):** targeted outlier/consistency checks are a
  project rule when analysing any lockit (found PascalCase key outliers, gender attrs, enum role).
- **NEXT — `/retro`:** propose library promotions (approve→apply): `fluent-ftl` convention,
  `ftl_parse_template`, and the **origin-labeling + drift-audit** idea (format-general); write
  session 002 note (already drafted as living log) + next-session kickoff.

## Done
- Repo scaffolded per spec §6; `git init` done (first commit: scaffold only).
- `.claude/settings.json` — deny-leaning permissions (spec §9 / App. D), verified
  against current Claude Code docs. Note: spec's `Write(/**)`/`Edit(/**)` deny rules
  were **omitted** — with current path semantics a single leading slash is
  project-root-relative, so those would deny *all* in-repo writes; Claude Code already
  confines writes to the project dir.
- Commands: `/intake`, `/profile`, `/toolkit`, `/wake`, `/retro`.
- `vault/02_SYSTEM/schema.md` — note frontmatter contracts, incl. the telemetry seam.
- `vault/library/` seeded empty (conventions/ heuristics/ script-templates/ + glossary).

## In progress — Wesnoth (GATE 0 + GATE 1 cleared)
- **Intake done (Mode B):** sparse/shallow clone of `wesnoth/wesnoth` `po/` in gitignored
  `sources/wesnoth/`; 32 gettext textdomains, ~26.3k English strings, 60+ langs.
- **GATE 0:** scope = 4 `.pot` (English source): `wesnoth-lib`, `wesnoth`, `wesnoth-units`,
  `wesnoth-httt`, copied to `data/wesnoth/pot/`.
- **GATE 1 cleared:** structure confirmed via review dossier (`data/wesnoth/gate1-review.md`,
  gitignored). Identity = `(domain, msgctxt, msgid[,plural])` + sha1 internal id, lossless.
- **Phase 3 done — vault notes written:** `profile.md` (confirmed), `structure.md`,
  `variables.md`, `context-prefixes.md` (105-prefix registry, script-generated),
  `open-questions.md` (decisions + tracked T1–T4).
- **Phase 4/5 DONE — toolkit built, tested, packaged.** 8 scripts in `scripts/wesnoth/`
  (parser, tokens, list_placeholders, list_context_prefixes, extract_by_type,
  validate_markup, report, tests); **10 tests pass** (dual-mode). Skill
  `lockit-wesnoth-toolkit` packaged; `toolkit.md` indexes it. GATE 2 cleared.
- **Library seeded (applied at /retro):** conventions `gettext-po`, `inline-context-prefix`,
  `list-grammar-cldr`; heuristics `gettext-detection`, `review-dossier`; script-template
  `po_parse_template.py` (verified on real files).
## Session 001 DONE — Option A (corpus-wide + multi-language), 2026-07-06
- **Generality confirmed:** toolkit ran across **all 32 domains**, no re-profiling —
  26,312 strings, **ids 26,312/26,312 unique, 0 collisions**. Anatomy holds.
- **Toolkit extended (Marcin-approved):** 3 markup families (Pango/DocBook/po4a) with
  per-family + ERROR/WARN validation; `{brace}` + hex-entity classes; refined `$var`
  tokenizer; `gender/agreement` prefix family (129-prefix registry regenerated).
- **Multi-language capability built:** `validate_placeholders.py` (cross-locale) — de/pl
  pilot found **8 real upstream defects, 0 false positives**. Framed as a *prepared* tool;
  focus stays on English analysis.
- **Tests 10 → 21, all pass.** Vault notes (profile/variables/structure/context-prefixes/
  open-questions/toolkit) updated in-session.
- **Human-in-the-loop review** (`data/wesnoth/session001-review.md`): A1–A4 confirmed;
  B1 (`&`→WARN), B3 (gender/agreement family) applied; B4 (DocBook pre-seed, CLI-collision
  names excluded); T5 resolved; T6/T7 tracked.
- **Library promotions applied (Marcin approved in review C1):** heuristic `markup-families`,
  convention `cross-locale-invariants`, template `validate_placeholders.py`.

- **NEXT — Phase 6 (Option B):** intake a **second, differently-structured (non-gettext)
  lockit** (`.xlsx`/`.csv`/`.ftl`/`.json`) to test whether the library made intake faster —
  does `gettext-detection` correctly say "not gettext", does `review-dossier` speed GATE 1,
  do new formats seed new library assets? See `docs/next-session-kickoff.md`.

## Policy added this session (from Marcin's guidance)
- **Memory is two-layer + hardened.** `vault/02_SYSTEM/memory-policy.md`: volatile
  Claude memory is staging only; the ritual (`/retro`) hardens durable facts into
  git-tracked SOPs/library/CLAUDE.md. `/wake` now surfaces un-hardened memory.
- **Document the *why* + harden working code.** Scripts carry plain-language rationale
  for less-capable agents; validated, broadly useful code is promoted to
  `vault/library/` principles. Folded into `/toolkit`, `/retro`, `schema.md`.
- **CLAUDE.md pointer to memory-policy + why-docs — APPLIED** (session 000 retro). No
  cornerstone changes pending.

## Backlog (bigger-picture direction)
See `vault/dev/backlog.md` — Marcin's product vision parked durably: translator/loc-specialist QA
(Theme A, near-term), knowledge graph (B), embeddings/semantic search+clustering (C), NL Q&A (D),
UI/explorer (E), foundations incl. telemetry (F). Principle: deterministic core stays source of
truth; graph/embeddings/NL are a semantic LAYER on top. Suggested first: A1 (run the prepared
cross-locale tools on a real translation) → A2/A3 → B1/B2 → F1 before C/D.

## North-star goals (design toward; raise at decision points)
1. **Cheaper models can do the job.** Profiles, conventions, and library must be
   explicit, deterministic, model-agnostic — the scripts carry the load, the model
   reads the chart. Bias every artifact toward being followable by a small model.
2. **Portable to an API runner.** Keep steps, prompts, and contracts clean enough to
   lift out of interactive Claude Code into code orchestrating LLMs via API.
3. **Telemetry & token/cost awareness.** Metering seam reserved in `schema.md` (design
   only so far). Wire it so each pipeline step can report calls/tokens/cost, enabling
   deliberate cheap-vs-expensive routing.
4. **Public release.** Intended to be shared publicly under a licence that invites
   others to pick up the idea. **Open decision — licence not yet chosen** (candidates:
   Apache-2.0 for code + CC-BY-4.0 for docs; or MIT; or a source-available/ethical
   licence). Decide before first public push. No client data ever ships (`data/**`,
   `sources/**` gitignored).

## Hard gates (never pass without Marcin's confirmation)
- **GATE 0** — confirm which located files are the lockit (Mode B intake).
- **GATE 1** — confirm/correct inferred structure before documenting.
- **GATE 2** — review generated toolkit before packaging as a skill.
