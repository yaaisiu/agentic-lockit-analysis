---
name: lockit-hoi4-toolkit
description: Use to parse, inventory, extract, validate, or QA the Hearts of Iron IV (Paradox Clausewitz pseudo-YAML) lockit — the loose `*_l_english.yml` localisation files — e.g. "parse the HoI4 .yml", "list placeholders / §colour / £icon / @flag / $VAR|fmt$ / [scope.fn] tokens", "catalogue the key vocabulary (country tags, suffixes, event namespaces/parts)", "extract an event namespace or clean translatable text", "validate structure (dup keys, colour balance, escaped-quote tail)", "audit for unknown constructs / dialect drift", "cross-locale check a translation preserves $vars/[scope]/icons", "report what we know". Wraps tested deterministic scripts in scripts/hoi4/; prefer these over ad-hoc parsing and NEVER use PyYAML on Clausewitz files.
---

# HoI4 Clausewitz pseudo-YAML lockit toolkit

Deterministic, dependency-free tools for the Hearts of Iron IV localisation `.yml` files
(Paradox **Clausewitz pseudo-YAML**, old-style dialect). **Read the chart first:**
`vault/lockits/hoi4/profile.md` (confirmed anatomy), `variables.md` (constructs + labeling),
`structure.md`. All scripts live in `scripts/hoi4/` and import the shared reader
`clausewitz_parse.py`. Run from `scripts/hoi4/`. Point any script at a **file or a directory**
(a dir = all `*.yml` in it — used for the whole 206-file corpus).

> **This is NOT YAML — never use PyYAML/ruamel.** It's a line format; the shared reader is a
> line-regex parser. **If the structure changed, re-profile before trusting these**
> (`/profile hoi4`). `labels.py --audit` tells you if new/unknown constructs appeared.

## Anatomy in one line
UTF-8-**BOM** files, each starting `l_english:`, then entries `KEY:[VERSION] "VALUE"`. Identity =
`KEY` (globally unique here). **Version integer** = optional deprecated revision counter ({0..4}),
never identity. **Two key styles:** underscore `<TAG>_<...>_<SUFFIX>` (country names `GER_fascism`
/ `_DEF` definite / `_ADJ` adjective) and dotted event `namespace.id.part` (`t`/`desc`/options/
tooltip/named-variant). **Old-style dialect:** `§X…§!` colour · `£icon` (whitespace-terminated,
**no closing £**) · `@TAG` flag · `$VAR$` / `$VAR|fmt$` (fmt = colour **and/or** number format) ·
`[scope.fn]` (dotted / bare / `?`optional / `|fmt`) · literal `\n` (and rare `\t`). Values may
contain **unescaped inner `"`** → extract greedy first→last quote. No char-limit column.

## Scripts
| Script | Use | Invocation |
|---|---|---|
| `clausewitz_parse.py` | core line-regex reader / census self-check | `python3 clausewitz_parse.py <file\|dir>` |
| `report.py` | one-screen summary + **source-side completeness/integrity node** (event coverage, reference resolution) | `python3 report.py [dir]` |
| `inventory.py` | construct census + `$VAR\|fmt$` / `[scope.fn]` sub-forms | `python3 inventory.py [dir] --samples 3` |
| `keys.py` | **key-vocabulary catalogue** (tags, suffixes, event namespaces + part kinds) | `python3 keys.py [dir]` |
| `extract.py` | select by `--file`/`--namespace`/`--tag`/`--style`; `--clean` = translatable text only | `python3 extract.py [dir] --namespace germany --clean` |
| `validate.py` | structural (warnings, dup keys, colour balance, `\"` tail) | `python3 validate.py [dir] --dups` |
| `validate.py --refs` | **reference integrity** — `$OTHER_KEY$` resolved vs **dangling** (defect list) | `python3 validate.py <full_dir> --refs` |
| `validate.py --length-ref` | **soft** localised-vs-source length reference (no hard limit exists) | `python3 validate.py --length-ref <en_dir> <other_dir> [--ratio 1.6]` |
| `validate_placeholders.py` | **cross-locale** token preservation ($var/[scope]/£icon/@flag) | `python3 validate_placeholders.py <en_dir> <other_dir>` |
| `labels.py` | **labeling registry + drift audit** | `python3 labels.py` · `python3 labels.py --audit <file\|dir>` |
| `tests/test_toolkit.py` | dual-mode tests (synthetic + real census) — 35 pass | `python3 tests/test_toolkit.py` |

## Labeling & drift (project rule)
`labels.py` is the single source of truth: every construct is tagged `format` (Clausewitz dialect,
portable) / `project` (HoI4-specific) / `unknown` (flagged). The audit is **two-tier**: **tier-1
drift** (foreign syntax — an unknown `§` letter, an escape beyond `\n`/`\t`, a CK3-style `#…#!`
span, a `{brace}`) must be **0**; **tier-2 noted** (expected tail — `\"`, cross-string colour
spans) is reported, not failed. Run `labels.py --audit <dir>` whenever the data changes.
**Coverage note:** the vault profile was built on a 5-file slice; the registry is verified against
all 206 files (tier-1 drift = 0 over 129,087 entries) — always audit the full set, not a slice.

## Prepared (cross-locale) tools
We hold only English source, so `validate_placeholders.py` and `validate.py --length-ref` are
**prepared**: point them at a source dir and a translation dir and they run. Length-ref is a
**soft reference** (HoI4 has no char limit); long/short ratios only *hint* at UI overflow.

## Completeness / integrity (source-side — no translation needed)
HoI4 English is source-only, so there is no *translation* completeness to measure. `report.py`
instead reports what the source alone can tell: **event structural coverage** (events missing a
title/body) and **reference integrity** (`$OTHER_KEY$` resolving to a real key vs **dangling**).
**Run reference checks on the FULL corpus** — a `$key$` ref may target a key in another file, so a
partial set reports false danglers (`validate.py` warns when the set looks partial).

## Known corpus facts (surface, don't fix)
Across all 206 base-game English files: 129,087 entries, **0 duplicate keys, 0 parse warnings,
tier-1 drift = 0**. NOTED tail: **25** colour spans unbalanced within one string (a known
cross-string `$VAR$`-concatenation pattern, not necessarily a defect) + **21** escaped `\"`.
**40 dangling `$VAR$` reference candidates** (real defects to review — e.g. the double-L typo
`$sasebo_naval_arsenall$`, `$Australia$`, `$Scavenger$`); **245 events with no title, 130 with no
body/desc** (some intentional — news/tooltip-only — some likely defects).

## Trust boundary
Generated by this project; trusted after GATE 2 (session 004). Scripts read/write local files
only, no network. **Proprietary Paradox content** (non-commercial User Agreement): data is
gitignored (`data/hoi4/**`, `sources/hoi4/**`); we **surface** aggregate facts/defects, never
edit the data, and **never** copy its strings into `library/`, this skill, or any committed note.
