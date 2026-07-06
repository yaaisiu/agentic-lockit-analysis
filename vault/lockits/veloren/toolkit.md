---
type: lockit-toolkit
lockit: veloren
skill: lockit-veloren-toolkit
updated: 2026-07-06
---

# Veloren — toolkit index

Deterministic Fluent tools in `scripts/veloren/`, packaged as skill `lockit-veloren-toolkit`
(GATE 2 cleared, session 002). All dependency-free, import the shared reader `ftl_parse.py`,
run from `scripts/veloren/`. **50 tests pass.** Read [[profile]] before use; if structure
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
| `tests/test_toolkit.py` | synthetic fixtures + real-corpus census pins | `python3 tests/test_toolkit.py` | ✅ 50/50 |

## Notes
- **Labeling is the drift guardrail** ([[open-questions]] T-V5): `labels.py --audit` surfaces any
  construct unknown to our system. It already found the `enum` attribute role at GATE 2.
- **Cross-locale sweep** produced `data/veloren/technical-defects.md` (gitignored): 81 real
  technical defects across 39 locales (dominant: `$reason` dropped in login ban/kick messages).
- Reusable, format-general pieces (`fluent-ftl` convention, a Fluent reader template, the
  origin-labeling + drift-audit idea) are **proposed for `library/` at /retro** (approve→apply).
