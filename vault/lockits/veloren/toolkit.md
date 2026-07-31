---
type: lockit-toolkit
lockit: veloren
skill: lockit-veloren-toolkit
updated: 2026-07-31
---

# Veloren — toolkit index

Deterministic Fluent tools in `scripts/veloren/`, packaged as skill `lockit-veloren-toolkit`
(GATE 2 cleared, session 002). All dependency-free, import the shared reader `ftl_parse.py`,
run from `scripts/veloren/`. **83 tests pass.** Read [[profile]] before use; if structure
changed, re-profile first.

| script | what it does | example | tested |
|---|---|---|---|
| `ftl_parse.py` | core reader (messages/terms/attributes/selectors/placeables); census self-check | `python3 ftl_parse.py ../../data/veloren/en` | ✅ 2026-07-06 |
| `report.py` | "what we know" — honest total vs translatable counts | `python3 report.py ../../data/veloren/en` | ✅ |
| `inventory.py` | placeholder inventory (5 classes, charset, origin) | `python3 inventory.py ../../data/veloren/en` | ✅ |
| `extract.py` | extract units by file / prefix / **role** / has-selector | `python3 extract.py ../../data/veloren/en --role gender` | ✅ |
| `gender_pairs.py` | gender forms side-by-side + incomplete-set report | `python3 gender_pairs.py ../../data/veloren/en` | ✅ |
| `validate.py` | single-locale structural check (braces, selector defaults, BOM) | `python3 validate.py ../../data/veloren/en --warn` | ✅ 0 err/0 warn |
| `validate_placeholders.py` | cross-locale invariants (source vs translation) | `python3 validate_placeholders.py ../../data/veloren/en ../../sources/…/pl --warn` | ✅ 0 false-pos |
| `report_all_locales.py` | technical-defect sweep over all locales → markdown | `python3 report_all_locales.py ../../data/veloren/en ../../sources/veloren/assets/voxygen/i18n out.md` | ✅ 39 locales |
| `labels.py` | labeling registry (fluent/project/unknown) + drift audit | `python3 labels.py --audit ../../data/veloren/en` | ✅ 0 unknown |
| `export_bundle.py` | emit a **normalized bundle** (manifest.json + lines.jsonl) for a downstream consumer; `--check` re-verifies + proves byte-stability | `python3 export_bundle.py ../../data/veloren/en` | ✅ 7131 rows, 0 problems |
| `tests/test_toolkit.py` | synthetic fixtures + real-corpus census pins | `python3 tests/test_toolkit.py` | ✅ 83/83 |

## Notes
- **Bundle export (session 007)** — `export_bundle.py` produces the input format a sibling
  **downstream consumer** consumes (DRAFT v0.2 contracts). Two things make it different from every
  other script here: its output is **normative** (annotations are stored as character offsets
  into the `source_text` *we* emit, so re-export must be byte-identical forever), and its
  identity is a sha256 of `(kind, id, attr)` — never a line number. `source_text` uses the
  reader's documented normalisation (strip + join with LF), declared in `producer_version`;
  the payload hash is pinned in the tests so a parser change fails loudly instead of silently
  re-anchoring stored annotations. It **refuses to export** a corpus with `validate.py`
  ERRORs, because unbalanced braces make the scanner drop a placeable and the row would then
  assert "no placeholder here" over a live substitution point. Output → gitignored
  `data/veloren/bundle/`. Verified by the consumer's own importer (`load_bundle`): 7,131
  lines, 772 empty, 796 fully masked, 6,335 annotatable, 0 untrusted placeholders.
  **This script is a one-off, written by hand against one consumer's schemas — the
  generalisation is parked as backlog G6** ("prepare a converter": the consumer publishes an
  information package — schemas + construct-mapping guide — and Cartographer *generates* the
  converter). Read that entry before hand-writing a second exporter. See [[backlog]].
- **`context` (session 007)** — `##`/`###` section markers are captured as `context.section`;
  3,979 of 7,131 rows carry one, versus 11 with a `#` comment. Consecutive marker lines join
  into one section (Veloren writes two-line blocks; keeping only the last line turned the
  corpus's most common section into the fragment "Feel free to ignore them.").
- **Labeling is the drift guardrail** ([[open-questions]] T-V5): `labels.py --audit` surfaces any
  construct unknown to our system. It already found the `enum` attribute role at GATE 2.
- **Cross-locale sweep** produced `data/veloren/technical-defects.md` (gitignored): 81 real
  technical defects across 39 locales (dominant: `$reason` dropped in login ban/kick messages).
- Reusable, format-general pieces (`fluent-ftl` convention, a Fluent reader template, the
  origin-labeling + drift-audit idea) are **proposed for `library/` at /retro** (approve→apply).
