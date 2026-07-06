---
type: session
id: "002"
date: 2026-07-06
lockit: veloren
gates_cleared: [GATE 0, GATE 1, GATE 2]
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 002 — Veloren (Fluent `.ftl`): the generality test, intake → toolkit

Second lockit, chosen to be **deliberately unlike** Wesnoth (gettext) to test whether the
accumulated `library/` speeds intake. Full pipeline completed in one session: intake → profile
→ toolkit → packaged skill, plus a corpus-wide cross-locale defect report. Written as a living
log (Marcin: *logging is the process record — readable backwards, so a weaker model can rebuild
the ecosystem*). Telemetry null (metering not wired — north-star #3).

## Outcome
- **Veloren mapped & tooled.** Fluent keyed-tree lockit: 48 en files, 4,241 messages (0 id
  collisions), 3,312 attributes, 2 terms. Vault chart confirmed; 9 dependency-free scripts +
  50 tests; skill `lockit-veloren-toolkit` packaged (GATE 2).
- **The library paid off as a recogniser/ruler-out** (not a parser): `gettext-detection` →
  not-gettext; `markup-families` → no markup; `inline-context-prefix`/`po_parse_template`
  don't fit → new Fluent reader; Wesnoth's **gender concept transferred** to `.fem/.masc/.neut`.
- **The generality test passed** and produced new reusable assets (proposed at retro).

## Gate decisions
- **GATE 0** — scope = English source only (48 `.ftl` + `_manifest.ron`); 39 translation
  locales reserved. Mode B sparse+shallow clone; GPL-3.0.
- **GATE 1** — anatomy confirmed via review dossier (Marcin answered inline). Identity = unique
  message id. Attributes are first-class translatable sub-units; selectors inline; `{ $var }`
  new placeholder class; terms; `{""}` empties tracked-not-counted; `.ron` manifest excluded;
  `TAIL()` Veloren-custom; `<>` are ordinary text in Fluent. Key outliers: PascalCase
  `tutorial-*/achievement-*`.
- **GATE 2** — toolkit reviewed. **T-V5 resolved: LABEL every construct with an ORIGIN**
  (fluent/project/unknown) in a documented registry (`labels.py`) with a drift audit. The rule
  immediately caught a **4th attribute role, `enum`** (named-lookup keys) I'd missed.

## What the toolkit does (scripts/veloren/)
`ftl_parse` (core reader) · `report` (honest counts) · `inventory` · `extract` (by role) ·
`gender_pairs` · `validate` (structural) · `validate_placeholders` (cross-locale) ·
`report_all_locales` (all-locale sweep) · `labels` (registry + `--audit` drift) · tests (50).

## Cross-locale sweep (Marcin: "our core thing")
Ran `validate_placeholders` over **all 39 locales** → `data/veloren/technical-defects.md`
(gitignored). **81 real technical defects, 0 false positives** — dominant: `$reason` dropped in
`main-login-banned/kicked` (~16 locales); `$min_combo`/`$min_combo_upg` in it axe descs; version
skew in zh-Hant. **Two false-positive sources caught and fixed** (both legitimate divergence per
[[cross-locale-invariants]]): engine-supplied agreement vars (`*_gender`) a translation may add,
and `.aN` random-pick arrays whose per-index matching across locales is unsound. We surface;
never edit GPL upstream.

## Method distilled (reusable for the next keyed/non-tabular lockit)
Detect family first (library heuristics) → census deterministically → find the minimal lossless
identity key → enumerate placeholder classes with a regex each → **hunt outliers** → write a
review dossier and gate on confirmation → only then document → only then build+test scripts →
**label every construct with origin + keep an unknown/drift bucket**.

## Hardened this session
Vault: `profile.md` (confirmed, 4 attribute roles + labeling), `structure.md`, `variables.md`
(labeling & origin), `open-questions.md` (all T-V* + cross-locale resolved), `toolkit.md`,
STATE. Skill packaged. Scratchpad recon scripts (`recon_ftl.py`, `investigate_ftl.py`) were the
throwaway seeds; the tested versions live in `scripts/veloren/`.

## Promotions PROPOSED at retro (approve → apply; none applied yet)
1. **convention `fluent-ftl`** — Fluent anatomy + detection (the `gettext-po` counterpart).
2. **template `ftl_parse_template.py`** — dependency-free Fluent reader (the `po_parse_template`
   counterpart).
3. **heuristic `construct-origin-labeling`** — label constructs format-native/project-native/
   unknown + drift audit (Marcin's rule; format-general).
4. **heuristic `outlier-hunting`** — actively probe for outliers, never assume uniformity.
5. **UPDATE convention `cross-locale-invariants`** — add two legitimate-divergence cases
   (engine-supplied agreement vars; unsound positional match on random-pick variant arrays);
   `also_seen: veloren`.

## Open threads
- **T-V5 follow-on:** enum-role families (buff/weapon/period/time) catalogued; new keys will
  re-surface as unknown (intended).
- Cross-locale WARNs (896 orphans = version skew; 133 dropped selectors) are review-level.
- Next lockit: a **tabular** `.xlsx`/`.csv` with key + char-limit columns (still the untested
  §5 anatomy) — see kickoff.
