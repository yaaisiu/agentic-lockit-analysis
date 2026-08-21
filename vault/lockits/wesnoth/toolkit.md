---
type: lockit-toolkit
lockit: wesnoth
skill: lockit-wesnoth-toolkit
updated: 2026-08-21
---

# Wesnoth — toolkit index (how & why)

The deterministic tools for this lockit, packaged as the `lockit-wesnoth-toolkit` skill
(`.claude/skills/lockit-wesnoth-toolkit/SKILL.md`). Scripts live in `scripts/wesnoth/`.
Built + tested at GATE 2 (session 000); **extended corpus-wide in session 001** — DocBook +
po4a markup families, `{brace}` + hex-entity classes, refined `$var`, and the cross-locale
`validate_placeholders.py`. Companion chart: [[profile]], [[variables]], [[structure]],
[[context-prefixes]].

## Design principles (the *why*, for whoever runs this next — incl. a cheaper model)
- **Discover once, extract forever.** The LLM inferred structure at GATE 1; these scripts
  now do the repeatable work with no model calls — reproducible, free, testable.
- **One parser, one token source.** Everything imports `po_parse` (records) and
  `po_tokens` (patterns), so a fix propagates and code never drifts from [[variables]].
- **Lossless + non-ambiguous identity.** Every field preserved separately; identity is
  `(domain, msgctxt, msgid[,plural])` + a reorder-proof `sha1` internal id (line = locator).
- **Rationale-first.** Each script opens with a plain-language *why* header.
- **Dependency-free.** No polib/pandas/pytest required — runs in a minimal env and under
  cheaper models (supports the API-runner goal). Tests run under plain `python3` too.

## Scripts

| script | what it does | example | tested |
|---|---|---|---|
| `po_parse.py` | **foundation** reader → uniform records (+ internal id); `--summary/--jsonl/--check` | `python3 scripts/wesnoth/po_parse.py sources/wesnoth/po/wesnoth-lib/wesnoth-lib.pot --check` | ✅ unit + real |
| `po_tokens.py` | shared token regexes + markup families (pango/docbook/po4a) + `brace_var` | (imported) | ✅ via token/family tests |
| `list_placeholders.py` | inventory `$vars`/markup/entities/escapes/printf/`{brace}` | `… list_placeholders.py sources/wesnoth/po/*/*.pot` | ✅ matches recon |
| `list_context_prefixes.py` | `^`-prefix registry (families, counts, first-seen) | `… list_context_prefixes.py sources/wesnoth/po/*/*.pot --family gender` | ✅ 129 prefixes |
| `extract_by_type.py` | slice by domain / prefix / substring / token class | `… extract_by_type.py sources/wesnoth/po/wesnoth-units/wesnoth-units.pot --prefix female` | ✅ female forms |
| `validate_markup.py` | **per-family** balance (Pango/DocBook/po4a) + stray `\`; **ERROR** (structural) vs **WARN** (unescaped `&`-in-markup) | `… validate_markup.py sources/wesnoth/po/*/*.pot` | ✅ 0 error, 1 warn, 0 FP |
| `validate_placeholders.py` | **cross-locale** consistency: `$var`/`{brace}`/printf/markup/plural-arity, source vs a translation `.po` | `… validate_placeholders.py …/wesnoth-lib.pot …/wesnoth-lib/de.po` | ✅ 8 real defects on de/pl |
| `report.py` | coverage snapshot ("what we know / don't") | `… report.py sources/wesnoth/po/*/*.pot` | ✅ |
| `completeness.py` | **translation completeness** per domain/language (translated / fuzzy / untranslated; plural = done only if all forms filled) | `… completeness.py data/wesnoth/po/pl` | ✅ synthetic + real de/pl |
| `export_bundle.py` | **export a normalized BILINGUAL bundle** (manifest.json + lines.jsonl) for a downstream MT-benchmarking consumer; `--check` re-verifies + byte-compares | `… export_bundle.py wesnoth pl` · `… --check data/bundles/wesnoth-pl sources/wesnoth/po` | ✅ synthetic + real pl (26,312 rows) |
| `test_toolkit.py` | dual-mode tests (pytest or plain python) | `python3 scripts/wesnoth/test_toolkit.py` | ✅ **34 passed** |

## Translation completeness (added s004 — the report Wesnoth was missing)
The English `.pot` profiling never measured *translation* completeness (needs the `.po`). Added
`completeness.py`; ran it on **de + pl** for the 4 profiled domains (copied from the s000 sparse
clone into gitignored `data/wesnoth/po/<lang>/`). Result:
- **German: 100%** across all 4 domains (5,258 strings) — a fully-maintained locale.
- **Polish: 89.2%** overall — but real gaps: `wesnoth` + `wesnoth-httt` = 100%, **`wesnoth-lib`
  80.2%** (160 fuzzy + 173 untranslated), **`wesnoth-units` 73.2%** (153 fuzzy + 82 untranslated).
  **313 fuzzy** strings a naive count would wrongly call "done" — hence the fuzzy split matters.
Surface, don't fix (upstream GPL). Confirms the "completeness node" value: it turns "is this
language done?" into per-domain numbers with the fuzzy trap made explicit.

## Validated facts — corpus-wide (`report.py`, all 32 domains, session 001)
- **26,312 strings; `internal_id` 26,312/26,312 unique; 0 collisions** — the GATE 1 identity
  model is lossless at full scale. 54 pluralizable; **129 `^`-prefixes** (712 entries).
  *(s008: this measures `internal_id` only. The bundle's `segment_id` is a different function
  and was measured separately — also 0 collisions. See [[profile]] § Shape.)*
- Token coverage: wml_var 686, markup_tag 4064, text_attr 47, entity 90, escape 3206,
  printf 17, **brace_var 286**.
- **20,206 strings (77%) have neither `^`-prefix nor `#. id`** → identity rests on the msgid
  text; confirms the GATE 1 key decision at corpus scale.
- **Markup families:** tag = 26,096, po4a = 216. `validate_markup` → 1 real source defect
  (unescaped `&` in a Pango span), 0 false positives.
- **Multi-language (de/pl pilot, 4 domains):** `validate_placeholders` found 8 real defects
  (misspelled/dropped/wrong `$vars`), 0 false positives.

## Bundle export — a NORMATIVE output (added s008, 2026-08-21)
`export_bundle.py` is the toolkit's first **producer** role, and it is handled differently from
every other script here: the other tools *report*, this one *promises*. A consumer joins on the
ids we emit forever, so the rules below are contract, not style.

- **The contract is published by us, at `contracts/bundle.schema.json`** (repo root, committed).
  It is **normative**; a consumer's copy is a validating mirror. Ownership split settled with
  Marcin: **this repo owns the *profile*** (the lockit anatomy, the `segment_id` function, what
  each field means) because it is the single producer both consumers key to; **each consumer
  owns its own *bundle contract*.** We never write into a consumer's repo — deciding what we
  emit and editing someone else's files are different things.
- **`segment_id` ≠ `internal_id`, and this is the trap.** `segment_id` =
  `<textdomain>:sha1((msgctxt or "") + "|" + msgid_raw)[:12]` — 12 hex, a pure function of
  `(textdomain, msgctxt, msgid_raw)`. `po_parse.internal_id` is the **same shape, 10 hex, a
  different preimage**. Reusing the wrong one produces a bundle that validates, looks correct,
  and joins to nothing. Four independently-computed vectors are pinned in the tests.
  *Hazard recorded for the next lockit:* the separator is a literal `|`, which occurs in Wesnoth
  text as the `$var|` terminator. The preimage is injective here **only** because `msgctxt` is
  empty on every Wesnoth entry. A lockit that actually uses `msgctxt` must revisit it.
- **Two kinds of error, two reactions — never conflate them.** A **structural** error (a `.po`
  that will not parse, a broken plural block) means the rows are untrustworthy → refuse
  (`--force` overrides loudly). A **cross-locale content finding** (the target dropped a `$var`)
  is a real upstream translation bug that has been in the locale for years → **never refuse**;
  record it per row in `placeholder_check`. Refusing on those would decline to export a corpus
  that legitimately contains them. See [[refusal-scope-discipline]] (proposed s008).
- **Byte-stable payload**, composed in memory, `lines.jsonl` written **before** `manifest.json`,
  `content_hash` over the bytes as written. *Standing rule: whoever rewrites the rows rewrites
  the manifest.* `--check <bundle-dir> <source-po-root>` re-exports in memory and byte-compares.
- **Provenance is a stop condition.** No `upstream {remote, commit, branch}` → no bundle. Read
  from `.git/config` / `.git/HEAD` / `.git/refs` with the file reader, **no git subprocess** —
  the deny-leaning permissions don't allow `git -C`, and a probe that needs a prompt fails in an
  unattended run.
- **Real-corpus result (Wesnoth pl, 2026-08-21):** 26,312 rows, 0 `segment_id` collisions, 54
  plurals, 712 derived `msgctxt`, 22 rows with real placeholder defects, `--check` REPRODUCIBLE.
  The bundle itself is gitignored (`data/bundles/wesnoth-pl/`) — CC-BY-SA content, public repo.

## Deferred / candidate extensions (see [[open-questions]])
- **DONE (B3):** `family()` now has a `gender/agreement` family (was misfiled under other/UI).
- **T6 (deferred, post-English):** run `validate_placeholders` across more locales / all 32
  domains (corpus QA sweep).
- **T7:** give `$(…)` WML formula / `$x[$i]` index their own handling only if needed.
