---
type: dev-state
updated: 2026-08-21
phase: 6
active_lockit: wesnoth
---

# STATE — you are here

## s008 — WESNOTH BILINGUAL BUNDLE EXPORTER + we now PUBLISH the contract (DONE, 2026-08-21)
**A second producer role, run as an unattended brief (TASK-I1).** No gates fired; the confirmed
anatomy is unchanged. Cartographer exports a profiled gettext lockit as a normalized **bilingual**
bundle for an MT-benchmarking consumer, and — new — **publishes the schema it emits** at
`contracts/bundle.schema.json`, so a consumer validates against a producer-owned contract instead
of guessing at one. Full detail: `vault/dev/sessions/008-wesnoth-bilingual-bundle-exporter.md`.
- **Ownership settled (Marcin, 2026-08-21) and it is narrower than "we own the schema":** this
  repo owns the **profile** (anatomy, the `segment_id` function, field meanings) because it is the
  single producer both consumers key to; **each consumer owns its own bundle contract**. The
  bilingual profile and the other consumer's span profile are different contracts **by design** —
  do not converge them. We still never write into a consumer's repo.
- **`segment_id` ≠ `internal_id` — the trap this session exists to avoid.**
  `<textdomain>:sha1((msgctxt or "") + "|" + msgid_raw)[:12]`; `internal_id` is the same *shape*,
  10 hex, a different preimage. Reusing it yields a bundle that validates, looks correct, and
  **joins to nothing**. Four externally-computed vectors pinned; a stability test shifts every line
  number and adds a plural and asserts no id moves.
- **Wesnoth pl exported:** 26,312 rows · 0 `segment_id` collisions · 24,477,591 bytes ·
  `content_hash f05b545f…` · `--check` **REPRODUCIBLE**. Tests **22 → 34**. Commit `c73f260`.
- **`pool`:** eval 14,914 · untranslated 11,398 (9,647 empty + 1,751 fuzzy). **Six domains are 0%
  translated** (5,874 rows) — they contribute nothing to an eval pool. 54 plurals, 0 arity
  disagreements; 712 derived `msgctxt`; 1,211 rows where raw ≠ display.
- **A1 advanced as a side effect: 22 real upstream placeholder defects across the full Polish
  locale**, reconciling exactly with the existing validator (its four `wesnoth-lib` *findings* are
  three *rows*). Two clusters are stale translations — English lost a variable, Polish kept it.
  Surface, don't fix. `placeholder_check` exists so the curation step can label them.
- **THE LESSON — a refusal must be keyed to something the output actually depends on.** The first
  structural rule refused all 26,312 rows because two `pl.po` files lack a `Plural-Forms` header —
  both domains have **zero plural entries**. Same defect class the brief had already carved out
  once for cross-locale content findings. **Twice = a rule, not an incident.**
- **Identity-proof hazard hardened.** Four notes said "26,312/26,312 unique, 0 collisions" without
  naming which id. It measures `internal_id`; `segment_id` needed its own measurement (also 0).
  `profile.md` / `toolkit.md` / `open-questions.md` corrected; s001 log annotated with a dated
  forward-pointer. *Good news is a documentation hazard when it doesn't name what it covers.*
- **G6 IS NOW WRITABLE** — the second hand-written exporter was the point. Diff yields **11 shared
  items** (the generator's skeleton) vs **7 that must come from a target package**. Design written
  into the backlog. Most transferable single rule: **vocabulary mapping at the boundary**.
- **Flagged, not fixed:** the bilingual manifest has **no `bundle_version` discriminator** and the
  closed field list forbids adding one — the exact absence that bit the Veloren contract at
  0.2.0→0.3.0. Cheap now, expensive after the consumer's freeze.
- **LIBRARY: all 12 promotions APPLIED at the s008 retro** (s008's 5 + s007's 7, which had been
  pending a session). The library grew by **4 conventions** (`byte-stable-artifact`,
  `producer-contract-ownership`, `derived-identity-keys`, `boundary-vocabulary-mapping`),
  **3 heuristics** (`refusal-scope-discipline`, `identity-proof-scope`,
  `construct-spans-not-tokens`) and **1 template** (`byte_stable_jsonl.py`), plus 4 updates
  (`ftl_parse_template` → spans, `construct-origin-labeling`, `fluent-ftl` sections,
  `outlier-hunting` parser-not-grep) and 8 glossary terms. **Nothing pending.**
- **NEXT — Marcin's call.** The **curated slice** (next brief, gated, with a human) · **G6** (now
  writable, and the byte layer is already a template) · or the parked tracks.

## s007 — BUNDLE EXPORTER: Cartographer's first downstream consumer (DONE, 2026-07-31)
**A new capability, not a new lockit.** We now produce a **normalized bundle** (manifest.json +
lines.jsonl) for the sibling **downstream consumer**, against its DRAFT v0.2
contracts. No gates fired, but the foundation parser changed, so the migration was *proven*.
- **`placeables()` now returns `(start, end, inner)`** — offsets were discarded, and `.strip()`
  made the value differ from the real slice on **495 of 1267** placeables, so nothing could be
  re-anchored. Unterminated `{` is no longer emitted (it used to invent a token ending nowhere;
  as a *span* that becomes a mask over the rest of the string). **Migration proof: inventory /
  report / validate / labels --audit are byte-identical to a pre-change baseline.**
- **`source_text` = the reader's documented normalisation**, not a verbatim slice — declared in
  `producer_version` and **pinned by a payload sha256 in the tests**, because the risk was never
  nondeterminism but a future parser edit silently moving 7,131 strings.
- **Census reconciled with the consumer's own numbers:** 7,131 rows = 6,359 non-empty + 772 blank
  (424 valueless container messages are not units); 48 files; 1,267 placeholders; 0 drift. Units
  that are entirely one placeable: **772 empty + 24 not empty** — the 24 matched the consumer's
  independent measurement exactly. **Their importer (`load_bundle`) accepts the bundle.**
- **Counted, then checked:** the census said `function 1` where the vault said 2 — the two cited
  "call sites" are `#` COMMENTS about `TAIL()`. Notes corrected (also `771 {""}` → **772**: one
  spelling had been counted, not the construct). *A comment is not a placeable.*
- **`##`/`###` section markers captured** as `context.section`: **3,979 of 7,131 rows** gain one
  (vs 11 with a `#` comment). Consecutive marker lines join — keeping only the last had made
  "Feel free to ignore them." the corpus's most common section, on 564 entries.
- **Sibling repo treated as READ-ONLY.** Found a real bug in their fixture (`regenerate.py`
  hashes `source_id` into `line_id`, contradicting their own schema) — **reported, not fixed**;
  Marcin fixes it there. Other contract gaps flagged rather than approximated (see session note).
- Tests **50 → 93**. Commits `a5d9a76`, `b11fba4`, `da8796c`, `53738ca`.
- **Backlog G6 added (direction, not scheduled):** a **converter-GENERATOR skill** — the consumer
  publishes an information package (schemas + construct-mapping guide) and Cartographer *generates*
  the converter. `export_bundle.py` is the first instance, hand-written; G6 is the generalisation.
- **NEXT — Marcin's call.** 7 library promotions await approval (see the session note); then the
  parked tracks: A1 cross-locale on a real translation · char-limit hunt (F4) · Polish-audit ·
  F5/F6 security · G1/G2 generators · F7 doc-freshness · or build **G6**.

## s006 — WENT PUBLIC + doc reconciliation (DONE + PUSHED), 2026-07-10
**Not a lockit session — the release close-out.** Marcin's legal check cleared; flipped the repo
to **PUBLIC**. No gate mid-flight; next session is his call (lockit / security / QA-generators).
- **Repo is PUBLIC:** `github.com/yaaisiu/agentic-lockit-analysis`. Flip preceded by a clean final
  pre-flight (no client data tracked or in history — only `.gitkeep`; no PII/paths; all release
  artifacts present). Added description-consistent + **10 discoverability topics** (localization,
  game-localization, claude-code, ai-agents, …). Marcin handles the LinkedIn post in another tool.
- **"Unknown licence" badge explained (cosmetic).** GitHub's `licensee` reads any root `LICENSE*`
  file; `LICENSE-docs.md` *describes* CC-BY-4.0 in prose instead of pasting its verbatim legal text,
  so the scanner can't fingerprint it → "Apache-2.0, Unknown licenses found." Harmless; nothing
  mislicensed. Optional clean-up (deferred, Marcin's call): rename `LICENSE-docs.md` out of the
  `LICENSE*` glob (option 1) — not done.
- **Doc-reality drift caught + fixed.** Reviewer (who cloned the now-public repo) found STATE /
  kickoff / backlog / s005-note still claiming *private*. Corrected the **live-state** files;
  **annotated** the s005 session log with a dated forward-pointer (history preserved, not rewritten).
- **Backlog F7 added:** doc-freshness / repo-truth consistency check (grep stale-claim patterns +
  diff asserted facts against `gh`/`git`; run at `/wake` + `/retro`; distinguish live-state files
  from historical logs). No library promotion — parked until built. Commits `8ab8ebe` (+ push).
- **NEXT — Marcin's call** (all prepared, no gate mid-flight): (a) resume **lockit work** — char-limit
  hunt / a new format (JSON/`.arb`/`.strings`/xliff) / cross-locale tools on a real translation (A1) /
  Polish-audit track; (b) **security** F5 (input/injection) &/or F6 (generated-script safety gate);
  (c) **QA-generators** G1 (translator brief) / G2 (pseudo-loc).

## s005 — PUBLIC RELEASE PREP (DONE + PUSHED to the PRIVATE repo), 2026-07-10
**Not a lockit session — polish-and-publish.** Worked `docs/release-plan.md` top-to-bottom; all
three tracks done, committed, and **pushed to the private GitHub repo
`git@github.com:yaaisiu/agentic-lockit-analysis`** (Marcin authorized the push). Tag
`seed-v1-original` pushed too. **Repo was flipped PUBLIC on 2026-07-10 (s006)** after Marcin's
go-ahead + a clean final pre-flight (see north-star #4). *(At end of s005 it was still private, pending
his legal check.)*
- **Track 1 — legal/safety gate.** Pre-flight re-verified (history clean, no PII/paths, client data
  gitignored). Content-licence audit: the one real CC-BY-NC-SA fragment (`"Writing & Narrative"` in
  a-dark-forest `profile.md`) scrubbed to synthetic; HoI4 notes confirmed synthetic. Added `LICENSE`
  (Apache-2.0), `LICENSE-docs.md` (CC-BY-4.0), `ATTRIBUTION.md` (four upstreams + licences).
  Copyright holder = "Lockit Cartographer contributors" (Marcin's choice, not his legal name).
- **Track 2 — seed reflective/universalisation pass.** Originals pinned at git tag
  **`seed-v1-original`** (referenced from each revised file). Spec §3 reframed "Claude Code" → **any
  agentic coding harness** (six requirements + a Claude-Code binding table). Foregrounded the
  **cheap/local-model** rationale (proprietary/pre-release data → may need a local model). Added a
  **"toolkit shape — what good looks like"** section, mined from all 4 toolkits (parse→record→tools,
  stdlib-only, deterministic + stable identity, BOM, origin-labeling + two-tier drift, report-vs-
  validate, prepared cross-locale checker, dual-mode tests, dense "why" docstrings, command vocab).
  Folded in day-one **proprietary-vault** + **prompt-injection** disciplines, "a slice under-samples,"
  honest char-limit gap, QA outcomes. Fixed the `@docs/initial-spec.md` path bug (CLAUDE.md + prompt).
- **Track 3 — README rewrite + field guide.** Full README led by Marcin's **why** (13-yr loc
  specialist; help the process, don't replace translators). Added **"how it remembers & improves"**
  (wake/retro rhythm + two learning loops — from a review question). Published the content-free
  **Clausewitz field guide** → `docs/clausewitz-loc-field-guide.md` (provenance header). **Marcin
  reviewed → 5 `[C:]` comments addressed:** scope = all formats not just tabular / not just studios
  (mods + OSS too); translators warned of limits early; dropped "yet" (supportive tool, never a
  translator by design); field-guide provenance (drafted by Claude research mode, our pipeline caught
  wrong bits — the case for deterministic verification); hire-me offer in the courtesy note.
- **New backlog (security foundation):** **F5** prompt-injection awareness+defence (input hardening);
  **F6** generated-script safety gate — verify the LLM-generated toolkit (AST linter + sandbox +
  determinism, via the script-reviewer subagent the spec already anticipates; output verification).
  F5 ↔ F6 = the two halves (harden input / verify output).
- **Memory hardened:** `about-marcin` (user memory — 13-yr loc specialist, philosophy, MobyGames +
  LinkedIn links).
- **NEXT — Marcin's call.** (a) After his ~30-min legal sanity check, **flip the repo to public**
  (outward + irreversible); (b) resume deferred lockit work — char-limit hunt / a new format
  (JSON/`.arb`/`.strings`/xliff) / run the prepared cross-locale tools on a real translation
  (backlog A1) / start the Polish-audit track; (c) begin **F5/F6** security hardening. No gate mid-flight.

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
- **Post-retro (2026-07-09): source-side completeness/integrity node added** (Marcin: "add a
  completeness node"). `report.py` now reports event structural coverage + reference resolution;
  `validate.py --refs` lists **dangling `$OTHER_KEY$` refs** (all 206: **40** real candidates incl.
  typo `$sasebo_naval_arsenall$`; **245** events missing a title). Run `--refs` on the FULL corpus
  (cross-file refs). Tests **41/41** (+6). Recorded in open-questions + toolkit.md.
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

## Completeness node added (2026-07-09, Marcin: "add a completeness node / missing reports")
- **HoI4 (source-side):** `report.py` completeness node + `validate.py --refs` — 40 dangling
  `$OTHER_KEY$` refs, 245 events missing a title (all 206). See the HoI4 section above.
- **Wesnoth (the missing translation-completeness report):** the s000 sparse clone was still on
  disk (1,922 `.po`, no re-clone needed) → copied **de + pl** for the 4 domains into gitignored
  `data/wesnoth/po/<lang>/`; added `scripts/wesnoth/completeness.py` (translated/fuzzy/untranslated,
  plural-aware). **German 100%; Polish 89.2%** (lib 80.2%, units 73.2%; 313 fuzzy). Wesnoth tests
  21→22. Indexed in wesnoth `toolkit.md` + SKILL. (Veloren + A Dark Forest already had completeness.)

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
4. **Public release — DONE (2026-07-10): repo is now PUBLIC.** Flipped
   `yaaisiu/agentic-lockit-analysis` to public after Marcin's go-ahead + a clean final pre-flight
   (no client data tracked or in history — only `.gitkeep`; no PII/paths; all release artifacts
   present). Added 10 discoverability topics (localization, game-localization, claude-code,
   ai-agents, …). Next: Marcin posts to LinkedIn for traction. Licence — permissive open source:
   Apache-2.0
   (code) + CC-BY-4.0 (docs) + a README **courtesy note** (commercial use free; a request,
   not a term, to hear about commercial products). Marcin's reasoning: the seed is
   reproducible from the prompts, so a restrictive licence adds friction + false security.
   **Next session executes the release** — see `docs/release-plan.md` + kickoff. No client
   data ever ships (`data/**`, `sources/**` gitignored). Legal sanity-check advised pre-push.

## Hard gates (never pass without Marcin's confirmation)
- **GATE 0** — confirm which located files are the lockit (Mode B intake).
- **GATE 1** — confirm/correct inferred structure before documenting.
- **GATE 2** — review generated toolkit before packaging as a skill.
