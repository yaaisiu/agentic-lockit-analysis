---
type: lockit-toolkit
lockit: hoi4
skill: lockit-hoi4-toolkit
updated: 2026-07-09
---

# HoI4 — toolkit index

Skill: **`lockit-hoi4-toolkit`** (`.claude/skills/lockit-hoi4-toolkit/SKILL.md`). Scripts in
`scripts/hoi4/`, dependency-free, import the shared reader `clausewitz_parse.py`. Built + tested
+ packaged at **GATE 2 (session 004, Marcin approved 2026-07-09)**. **35/35 tests pass.** Run from
`scripts/hoi4/`; every script takes a **file or a directory** (dir = all `*.yml`).

> If the structure changed, re-profile (`/profile hoi4`) before trusting these. **Never PyYAML.**

| script | what it does | example invocation | tested |
|---|---|---|---|
| `clausewitz_parse.py` | shared line-regex reader (utf-8-sig, greedy quote, optional version, log-and-skip, key styles) + census | `python3 clausewitz_parse.py ../../data/hoi4/en` | ✅ 2026-07-09 |
| `labels.py` | origin registry (`format`/`project`/`unknown`) + two-tier `--audit` (drift / noted tail) | `python3 labels.py --audit ../../sources/hoi4` | ✅ 2026-07-09 |
| `inventory.py` | construct census + `$VAR\|fmt$` + `[scope.fn]` sub-form breakdown | `python3 inventory.py ../../data/hoi4/en --samples 3` | ✅ 2026-07-09 |
| `keys.py` | key-vocabulary catalogue: country tags, suffixes, event namespaces + part kinds (T-H3) | `python3 keys.py ../../data/hoi4/en` | ✅ 2026-07-09 |
| `report.py` | one-screen "what we know" summary | `python3 report.py ../../sources/hoi4` | ✅ 2026-07-09 |
| `extract.py` | select by file/namespace/tag/style; `--clean` = translatable text only | `python3 extract.py ../../data/hoi4/en --namespace germany --clean` | ✅ 2026-07-09 |
| `validate.py` | structural (warnings, dup keys, colour balance, `\"` tail) + `--length-ref` (soft, E1) | `python3 validate.py ../../sources/hoi4 --dups` | ✅ 2026-07-09 |
| `validate_placeholders.py` | prepared cross-locale token preservation ($var/[scope]/£icon/@flag) | `python3 validate_placeholders.py <en> <other>` | ✅ 2026-07-09 |
| `tests/test_toolkit.py` | dual-mode tests (synthetic semantics + real census; incl. all-206 drift=0) | `python3 tests/test_toolkit.py` | ✅ 35 pass |

## Corpus facts (all 206 base-game English files, via the toolkit)
129,087 entries · 0 duplicate keys · 0 parse warnings · tier-1 drift = 0 · key styles
105,109 underscore / 23,978 dotted-event · version :N ∈ {0..4} · constructs: colour 19,754 ·
icon 1,821 · flag 86 · variable 17,861 · scope-fn 31,068 · `\n` 12,152. NOTED tail: 25 unbalanced
colour spans + 21 escaped `\"` (located by `validate.py`).

## Prepared cross-locale tools
`validate_placeholders.py` and `validate.py --length-ref` need a translation dir (we hold only
English). Verified on synthetic fixtures in the tests; framed as prepared, not yet run on a real
HoI4 translation.
