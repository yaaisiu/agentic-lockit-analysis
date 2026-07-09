---
type: session
id: "004"
date: 2026-07-09
lockit: hoi4
gates_cleared: [GATE 0, GATE 1, GATE 2]
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 004 — HoI4 (Paradox Clausewitz pseudo-YAML): the first proprietary lockit

## Goal
Intake + profile + tool the biggest, most construct-heavy lockit yet (206 files, 129,087 entries)
and the **first proprietary/NDA-class** one — testing whether the library sped it up and whether
gitignore + vault-commit discipline hold under real NDA data.

## What happened

### GATE 0 — intake (files pre-staged)
Files already in `sources/hoi4/` (gitignored). Rather than take the kickoff's guessed slice, I
**measured construct density across all 206 files** and picked a 5-file slice for coverage:
`focus` (version-int, 97% of all version tags), `events` ([scope]+\n densest), `decisions`
(£icon), `game_rules` (@TAG carrier), `countries` (plain baseline). Marcin confirmed **5 files**
(+countries). Copied to `data/hoi4/en/` (12,867 entries ≈10%). Corrected two kickoff guesses from
real data: countries has **0** @TAG (game_rules is the carrier); version-int is 97% in focus.
`git check-ignore` verified both `data/hoi4/**` and `sources/hoi4/**` are ignored.

### GATE 1 — structure (dossier, all confirmed)
Library-first: `gettext-detection`/`csv-detection` correctly ruled out; no reader template fit →
new line-regex reader. Field-guide regex matched **100%** (0 malformed, 0 multi-line, 0 dup).
Anatomy: `KEY:[VER] "VALUE"`, UTF-8-BOM, **two key styles** (underscore `<TAG>_..._DEF` + dotted
event `namespace.id.part`); old-style dialect `§X…§!`/`£icon` (no closing £)/`@TAG`/`$VAR|fmt$`/
`[scope.fn]` (4 sub-forms)/`\n`; **unescaped inner `"`** → greedy first→last extraction.
**Two "look closer" items resolved empirically (all 206):** `$VAR|fmt$` `|` = **format spec
(colour AND number)**, not colour-only; `KEY:N` = **version counter** (values {0..4}, no key has
two Ns), not a selector. Marcin idea **E1**: length-ref for limit-less lockits.

**Discipline established:** vault notes are committed → wrote them with **synthetic examples only**;
real `file:line` content went to the gitignored `data/hoi4/gate1-review.md`. (Hardened to memory.)

### GATE 2 — toolkit (8 scripts, 35 tests, packaged)
`clausewitz_parse` (shared reader: utf-8-sig, greedy quote, optional version, log-and-skip, key
styles) · `labels` (origin registry + **two-tier** `--audit`) · `inventory` · `keys` (vocabulary
catalogue, T-H3) · `report` · `extract` (+`--clean` translatable text) · `validate` (structural +
`--length-ref`, E1) · `validate_placeholders` (prepared cross-locale). Dual-mode tests **35/35**.
Skill `lockit-hoi4-toolkit` packaged; `toolkit.md` indexes it. **Scaled to all 206:** 0 dup keys
(T-H2), 0 parse warnings, **tier-1 drift = 0** over 129,087 entries (T-H1); NOTED tail = 25
unbalanced colour spans + 21 escaped `\"`. Key catalogue: 374 tags, suffix vocab, 41 namespaces.

### Marcin's question — plural / gender / case inflection (answered via the toolkit)
HoI4 **delegates morphology to the engine**, not in-string selectors: case/definite/adjective via
`GetNameDef`/`GetAdjective` (~25k) + `_DEF`/`_ADJ` keys; gender via `GetSheHe`/`GetHerHis` (~230,
character-scoped); **plurals: none** (no count selection; `_plural` = fixed labels). Opposite of
gettext/Fluent. Real downstream limit for Polish (no in-loc case/number agreement). Recorded as
Q-INFL; generalised into the new `morphology-location` heuristic.

## Real findings surfaced (report, don't fix — proprietary data)
0 structural defects across 206. Only anomalies: 25 cross-string colour spans (known
`$VAR$`-concatenation pattern) + 21 escaped `\"` — both expected, both located by `validate.py`.

## Library payoff (recognise-before-infer)
✅ `gettext-detection` → not gettext · ✅ `csv-detection` → not CSV · reader templates didn't fit →
new line-regex reader · ✅ `construct-origin-labeling` generalised (added the two-tier drift idea) ·
✅ `outlier-hunting` (slice under-samples; audit the whole corpus) · ✅ `cross-locale-invariants`
(token preservation is the invariant when morphology is engine-delegated).

## Promotions proposed → **Marcin approved all 9 → applied (s004)**
1. heuristic `clausewitz-detection` (new)
2. convention `clausewitz-pdx-yaml` (new; per-game profile-as-data, HoI4 = first row)
3. script-template `clausewitz_parse_template.py` (new; verified on all 206)
4. heuristic `morphology-location` (new; wesnoth/veloren/hoi4 contrast)
5. heuristic `length-reference` (new; E1 — soft length for limit-less lockits)
6. update `construct-origin-labeling` (+two-tier drift, +semi-open-vocab, +also_seen hoi4)
7. update `cross-locale-invariants` (+token-preservation invariant, +also_seen hoi4)
8. update `outlier-hunting` (+also_seen hoi4 — slice under-sampling, tail, semi-open vocab)
9. memory hardened: [[proprietary-vault-discipline]] (synthetic in committed notes; real in dossier)

## Open threads
- **Char-limit column still untested** — the one §5 anatomy no lockit has exercised; `length-ref`
  is the soft workaround, not a substitute. Needs a dedicated source hunt (deferred).
- Prepared cross-locale tools (`validate_placeholders`, `--length-ref`) not yet run on a real HoI4
  translation — would need a `_l_polish.yml` set.
- North-star still open: licence choice (#4), telemetry wiring (#3).
