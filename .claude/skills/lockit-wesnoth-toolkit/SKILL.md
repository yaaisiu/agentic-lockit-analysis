---
name: lockit-wesnoth-toolkit
description: >
  Use to parse, inventory, extract, validate, or EXPORT the Wesnoth gettext lockit
  (.pot / .po) — e.g. "parse a Wesnoth .pot", "list all placeholders/variables/{brace}
  tokens", "extract gender (female^) forms", "pull one textdomain or ^-context prefix",
  "validate markup is balanced (Pango / DocBook / po4a man)", "check a translation preserves
  $vars/plurals (cross-locale)", "report completeness per domain", "export a normalized
  BILINGUAL bundle (manifest.json + lines.jsonl) for a downstream consumer", "check a bundle
  / verify it is byte-reproducible", "report what we know about the lockit". Wraps tested
  deterministic scripts in scripts/wesnoth/; prefer these over ad-hoc parsing for any
  Wesnoth localisation file.
allowed-tools: Bash(python3:*) Read Glob
---

# Wesnoth lockit toolkit

Deterministic tools for the Wesnoth gettext lockit. **Structure is documented in
`vault/lockits/wesnoth/profile.md`** (+ `structure.md`, `variables.md`, `context-prefixes.md`).
Read the profile first if unsure what a field means. Real files live in gitignored
`data/wesnoth/` (client/GPL data — never copy their content into this skill or the library).

## Core model (why these tools exist)
Wesnoth localisation is **GNU gettext**, not a spreadsheet: no key/limit columns; identity
is `(textdomain, msgctxt, msgid[, msgid_plural])` (msgctxt empty in Wesnoth, so
`(domain, msgid)` is unique). Discover with the model **once**; after that, run these
scripts — reproducible, free, testable. Each script has a plain-language *why* header.

## Foundation (import these; don't re-parse by hand)
- `scripts/wesnoth/po_parse.py` — PO/POT reader → uniform records (msgid, plural, msgctxt,
  `^`-context split, all comments/refs/flags, **sha1 internal_id**). Lossless.
- `scripts/wesnoth/po_tokens.py` — the single source of truth for token regexes + known tags.

## Commands (lockit path is `data/wesnoth/pot/<domain>.pot`; accepts many files)
- `python3 scripts/wesnoth/po_parse.py <file> [--summary|--jsonl|--check]` — parse / self-check.
- `python3 scripts/wesnoth/list_placeholders.py <file...>` — inventory `$vars`, markup,
  entities, escapes, printf, **`{brace}`**: counts + which entries.
- `python3 scripts/wesnoth/list_context_prefixes.py <file...> [--family FAM]` — the `^`-prefix
  registry (regenerates `context-prefixes.md`'s data). Families incl. **`gender/agreement`**.
- `python3 scripts/wesnoth/extract_by_type.py <file...> [--prefix P] [--contains S] [--has CLASS] [--jsonl]`
  — slice by textdomain / `^`-context / substring / token class. (Prints source text — local use only.)
- `python3 scripts/wesnoth/validate_markup.py <file...> [--show-unknown]` — **per-family** tag
  balance (Pango / DocBook / po4a man, auto-detected), stray backslash, unescaped `&`; prints
  **ERROR** (structural) vs **WARN** (unescaped `&`); exits non-zero only on ERROR.
- `python3 scripts/wesnoth/validate_placeholders.py <source.pot> <translation.po> [--json]` —
  **cross-locale** check: a translation must preserve `$var`/`{brace}` names, not add printf,
  keep markup balanced, and supply the locale's `nplurals` forms. (Prints strings — local use.)
- `python3 scripts/wesnoth/report.py <file...> [--json]` — coverage snapshot ("what we know /
  what we don't") to read against `profile.md`.
- `python3 scripts/wesnoth/completeness.py <po-file-or-dir>` — **translation completeness** per
  domain/language: translated / fuzzy / untranslated (fuzzy ≠ done; a plural is done only when
  every form is filled). Needs `.po` translations, not `.pot`.
- `python3 scripts/wesnoth/export_bundle.py <lockit> <locale> [<out-dir>] [--dry-run] [--force]`
  — **export a normalized BILINGUAL bundle** (`manifest.json` + `lines.jsonl`) for a downstream
  MT-benchmarking consumer. Contract: **`contracts/bundle.schema.json`**, which this repo owns
  and publishes; a consumer's copy is a validating mirror. Reads `sources/<lockit>/po/<domain>/`
  (`<domain>.pot` + `<locale>.po`), writes gitignored `data/bundles/<lockit>-<locale>/`.
  Identity is **`segment_id` = `<textdomain>:sha1(msgctxt|msgid_raw)[:12]`** — a *different*
  function from `po_parse.internal_id` (10 chars, different preimage); **never join on the
  wrong one**. Refuses on **structural** errors (`--force` overrides); **never** refuses on
  cross-locale content findings — those are per-row `placeholder_check` verdicts, because the
  Polish locale legitimately contains years-old upstream placeholder bugs.
  *(Prints counts only, never strings — but the bundle it writes is full lockit content and
  stays under gitignored `data/`.)*
- `python3 scripts/wesnoth/export_bundle.py --check <bundle-dir> [<source-po-root>]` — re-read a
  written bundle, validate it, verify `content_hash` against the bytes on disk; with the source
  root it **re-exports in memory and byte-compares** (REPRODUCIBLE or the first differing line).
  *Standing rule: whoever rewrites `lines.jsonl` rewrites `manifest.json`.*

## Tests
`python3 scripts/wesnoth/test_toolkit.py` (or `pytest scripts/wesnoth/`) — **34 tests**
(incl. the four pinned `segment_id` vectors, id stability, the byte-stable payload pin, and the
self-checks' refusals).
Synthetic fixtures (no lockit content) + an optional real-`.pot` integration check that skips
if data is absent.

## Trust & change
Generated by this project; GATE 2 passed 2026-07-02, **extended corpus-wide + reviewed
session 001 (2026-07-06)** — 3 markup families, `{brace}`/hex classes, refined `$var`,
`gender/agreement` prefixes, cross-locale validator. **If the lockit's structure has changed,
re-profile and update `profile.md` before trusting these**, and propose any convention change
to `vault/library/`. General patterns from this toolkit live in `vault/library/`
(`markup-families`, `cross-locale-invariants`, `validate_placeholders` template).
