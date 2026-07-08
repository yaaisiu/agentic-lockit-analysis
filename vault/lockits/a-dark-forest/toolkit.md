---
type: lockit-toolkit
lockit: a-dark-forest
skill: lockit-a-dark-forest-toolkit
updated: 2026-07-07
---

# A Dark Forest — toolkit index

Deterministic CSV tools in `scripts/a-dark-forest/`, packaged as skill
`lockit-a-dark-forest-toolkit` (pending GATE 2). All **dependency-free** (stdlib
`csv`/`json`/`re` only), import the shared reader `csv_parse.py`, run from
`scripts/a-dark-forest/`. **31 tests pass.** Read [[profile]] before use; if the file's
structure changed, re-profile first.

| script | what it does | example | tested |
|---|---|---|---|
| `csv_parse.py` | core reader — RFC-4180 quoting, meta/locale split, value-shape (scalar/array/empty), dup-key exposure; census self-check | `python3 csv_parse.py ../../data/a-dark-forest/localization.csv` | ✅ 2026-07-07 |
| `labels.py` | labeling registry (format/project/unknown) + `--audit` drift catcher (columns, desc tags, tokens, key parts) | `python3 labels.py --audit ../../data/a-dark-forest/localization.csv` | ✅ 0 unknown |
| `report.py` | "what we know" — namespaces, value shapes, **completeness (intentional vs untranslated vs active)** | `python3 report.py` | ✅ |
| `inventory.py` | construct inventory — placeholders (`{N}`, `\n`), value shapes, desc tags, key constructs, w/ origin | `python3 inventory.py` | ✅ |
| `extract.py` | slice to csv/tsv/json by namespace / key-substring / shape / untranslated; **excludes `[DEPRECATED]` by default** | `python3 extract.py --namespace credit --locales en,pl --format tsv` | ✅ |
| `arrays.py` | expand JSON-array cells element-by-element + **length-parity** check (order left to human, per-key rule) | `python3 arrays.py --key tab_data_titles:world` | ✅ |
| `validate.py` | single-file structural check — dup keys, malformed arrays, `[EMPTY]` consistency, tag drift; completeness | `python3 validate.py --warn` | ✅ 1 err (dup) |
| `validate_placeholders.py` | cross-locale invariants — `{N}` slot parity + array-length parity (conservative, 0 false-pos) | `python3 validate_placeholders.py --locale es` | ✅ 3 real defects |
| `tests/test_toolkit.py` | dual-mode: synthetic fixtures (quoting/arrays/empties/dups/drift) + real-corpus census pins | `python3 tests/test_toolkit.py` | ✅ 31/31 |

## What the toolkit found (real, upstream — report, don't fix)
- **1 duplicate key** `ui_label:heart` (rows 6 & 645) — identity is not unique.
- **3 malformed array cells** in `es`: `npc_event_options:cat_talk_A{1,2,3}` store `["?"],`
  (stray trailing comma) where `en` has `["?"]` — a data-entry defect. (My GATE-1 manual scan
  missed these; the toolkit's stricter parse caught them.)
- **`ua` is the only genuinely partial locale** — 256 *active* untranslated strings; every
  other locale is fully translated once `[DEPRECATED]` rows are excluded.

## Notes
- **Labeling is the drift guardrail** ([[construct-origin-labeling]]): `labels.py --audit`
  surfaces any construct unknown to our system (columns, description tags, control tokens). It
  re-verifies on every run that no hidden markup crept in (Marcin's D2 ask). Currently 0 unknown.
- **No `find_over_limit.py`** — this lockit has no char-limit column (deferred, [[open-questions]]
  Q0.3). That spec §7 script still awaits a dataset that has the column.
- Reusable, format-general pieces (a `csv-tabular` convention, a `csv-detection` recogniser, a
  dependency-free CSV reader template) are **proposed for `library/` at /retro** (approve→apply).
