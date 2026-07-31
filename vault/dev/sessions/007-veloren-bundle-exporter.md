---
type: session
id: 007
date: 2026-07-31
lockit: veloren
gates_cleared: []
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 007 — Veloren bundle exporter (first downstream consumer)

**A new capability, not a new lockit.** Cartographer gained its first *output contract*: it
now produces a normalized bundle for a sibling project — a **downstream consumer** that
annotates localisation strings and consumes bundles rather than raw lockit files. No gates fired (no intake, no re-profile) — but the work changed the
foundation parser, so the migration was proven rather than asserted.

## The shape of the problem

The consumer's `docs/EXPORTER_GUIDE.md` names Cartographer as its first producer and
Veloren as the reference format — and calls out three defects in **our** code that blocked a
conformant export. The guide is worth understanding as a genre: it exists *because JSON
Schema cannot express which `kind` a given construct gets*. Two producers making different
calls would disagree on a classifier feature no metric surfaces. That unexpressible half —
schemas **plus** a construct-mapping guide — is what a converter actually needs, and it is
the seed of backlog **G6** below.

The one requirement that shaped everything: **`source_text` is normative**. Every annotation
ever stored is a character offset into the string *we* emit; the consumer never opens the
`.ftl` again. A bundle is not a dump, it is a promise that the same input produces the same
bytes forever.

## What happened

1. **`placeables()` now returns `(start, end, inner)`** — the change everything else depended
   on. It returned `text[i+1:j-1].strip()`: offsets discarded, and the strip made the value
   differ from the real source slice on **495 of 1267** placeables, so nothing could be
   re-anchored. Changed **in place**, not via a sibling function — a duplicate brace scanner
   is exactly the drift the promoted library template already demonstrates.
   - **Behaviour change:** an unterminated `{` is no longer emitted. The old code appended
     `text[i+1:n-1]` — a token ending nowhere, minus its last character. As a *span* that
     becomes a mask swallowing the rest of the string. 0 occurrences in the corpus.
   - **Migration proof:** after updating the 5 call sites, `inventory` / `report` / `validate`
     / `labels --audit` produce output **byte-identical** to a baseline captured before the
     edit. The only non-mechanical site was `labels.py:156`, where `p[:40]` is a `Counter`
     key — a tuple slice is hashable, so a missed unpack would have silently printed
     `(12, 20, '$x')` instead of raising. Pinned by a test.

2. **Decided `source_text` = the reader's normalisation** (strip + join with LF), not a
   verbatim slice. Permitted by the contract, and the better string: Fluent dedents block
   values anyway, so a raw slice would bake file indentation (130 multiline units), trailing
   whitespace (15 lines) and any future `\r` into the text annotations anchor to. Declared in
   `producer_version` (`0.1.0+norm=strip-join-lf`) and **pinned by a payload sha256 in the
   tests** — the real risk was never nondeterminism, it was a future parser edit silently
   moving 7,131 strings.

3. **`export_bundle.py`** — 13-field rows in fixed key order, `line_id` = sha256 of
   `(kind, id, attr)` truncated (a pure function of `native_ref`, never of `line_no`, and
   deliberately **not** including `source_id`), byte-composed payload hashed before writing,
   `lines.jsonl` written before `manifest.json`, self-checks over the importer's seven
   hard-reject rules, and `--check` that re-exports in memory and byte-compares.

4. **Census — every number reconciled, including one measured independently by the other
   side.** 7,131 rows = 6,359 non-empty + 772 blank (424 container messages with no value at
   all are not units). 48 files, 1,267 placeholders, 0 `origin=unknown`, 0
   `structural_role=other`. Units that are *entirely one placeable*: **772 empty + 24 not
   empty** — and 24 was the consumer's own independent measurement of the same corpus.

5. **Acceptance by the consumer's own importer** (`load_bundle`). It
   accepts the bundle: all seven rules and both schemas pass. 7,131 lines, 772 empty, 796
   fully masked (= 772 + 24), 6,335 annotatable, 0 untrusted placeholders. No network needed —
   their `ml/.venv` already had `jsonschema`; run with `PYTHONDONTWRITEBYTECODE=1` so not even
   a `__pycache__` landed in their tree.

6. **Counted, then checked — and the note was wrong.** The census said `function 1` where
   three vault notes said 2. Marcin insisted on confirming rather than assuming benign. There
   is exactly one `{ TAIL($body) }` (`dialogue.ftl:46`); the two cited "call sites" are `#`
   **comments about** the function. A comment is not a placeable. Corrected in
   `structure.md` / `profile.md` / `variables.md`, along with `771 {""}` → **772** (771 `{""}`
   + 1 spaced `{ "" }` — one spelling had been counted, not the construct).

7. **Section markers captured (`context.section`).** `parse_text` discarded all 163 `##`/`###`
   markers. They are the finest-grained structural signal Fluent offers, and the consumer's
   pre-pass uses file **and** section as class hints — for Fluent the file is coarse (48 files
   over 7,131 units). **3,979 of 7,131 rows** now carry a section, versus 11 with a `#`
   comment. Consecutive marker lines join into one section: Veloren writes two-line blocks,
   and keeping only the last line had made *"Feel free to ignore them."* the corpus's most
   common section, on 564 entries — a real signal turned into a fragment.

## Decisions

- **`source_text` = documented normalisation**, not verbatim slice (Marcin).
- **`{""}` empties keep their verbatim text** plus a `literal` placeholder, rather than
  collapsing to `""` — lossless, and consistent with our own 773-literal inventory. Stated
  cost, accepted knowingly: 772 rows (10.8%) carry 4 characters of pseudo-text that enter
  char-level statistics. The contract contradicts itself here; flagged upstream.
- **`origin: unknown` passes through unchanged** — it is the drift signal telling the
  consumer not to trust a mask and to escalate. Never normalised, collapsed, or "fixed".
- **Refuse to export over `validate.py` ERRORs** (`--force` overrides, loudly, and records it
  in `manifest.notes`). Demonstrated: `m1 = hello { $x` yields `placeholders: []` — a false
  "no placeholder here" over a live substitution point, in a field the contract defines as a
  *positive assertion*.
- **The consumer's repo is read-only for us.** We found a real bug in their
  `fixtures/openttd-mini/regenerate.py` and did **not** fix it (below) — two sessions editing
  one file is worse than a reported bug.

## Reported to the sibling repo (not fixed by us)

- **Their fixture contradicts their own schema.** `regenerate.py:237` computes
  `sha256(source_id + "\x1f" + key)`, while `bundle.schema.json` says `source_id` is "no
  longer a component of `line_id` … so changing it does not invalidate stored annotations."
  Rename `openttd-mini` and all 50 ids change. Marcin is fixing it on that side; our exporter
  hashes `native_ref` only, pinned by a test that shifts every line number and asserts no
  `line_id` moves.
- **Contract gaps flagged rather than approximated:** no machine-readable field to declare a
  normalisation (`additionalProperties:false`); the `empty` clause is self-contradictory
  (`source_text: ""` *and* "the literal belongs in placeholders" cannot both hold); their
  `line_count` sentence read literally gives 7,555 vs our 7,131; **772 blanks, not 771** (three
  places in the contracts say 771); `msg-ref` and `NUMBER`/`DATETIME → spec` ship unexercised
  (0 occurrences); `key` is non-unique by design; `targets` withheld per v0.2; contracts are
  DRAFT and un-frozen, so `bundle_version` is hardcoded `0.2.0`.

## Hardened

- Bundle export + its rules → `vault/lockits/veloren/toolkit.md` (incl. the "normative output,
  handle differently" note) and the skill's `SKILL.md`.
- The corrected counts → `structure.md`, `profile.md`, `variables.md`, each with a dated
  in-note correction rather than a silent edit.
- Marcin's direction for a general converter-generator → **backlog G6**, cross-referenced from
  the Veloren toolkit note so a future session finds it *before* hand-writing a second
  exporter.
- Memory: [[verify-count-changes]] (confirm the cause of a changed count before calling it
  benign).

## Promotions proposed (awaiting approval — NOT applied)

1. `library/script-templates/ftl_parse_template.py` — sync `placeables()` to spans.
2. NEW heuristic `construct-spans-not-tokens`.
3. NEW convention `byte-stable-artifact`.
4. NEW template `byte_stable_jsonl.py`.
5. Update `construct-origin-labeling` — map vocabularies at the boundary; pass `unknown` through.
6. Update `fluent-ftl` — section markers as structural context.
7. Update `outlier-hunting` — count from the parser, not from grep.

## Open threads

- The seven promotions above.
- **G6** recorded, not scheduled.
- Contracts are DRAFT v0.2 — re-export and re-pin the payload hash at ratification.
- Per-attribute `line_no` still reports the parent entry's line (blessed by the schema's own
  example, but an approximation; `_build_entry` already iterates `block[1:]`, so the fix is ~4
  lines whenever it matters).
- Untouched from before: char-limit hunt (F4), A1 cross-locale on a real translation, the
  Polish-audit track, F5/F6 security, G1/G2 generators, F7 doc-freshness.

## Commits

- `a5d9a76` — feat(veloren): export normalized bundles for a downstream consumer (v0.2 contracts).
- `b11fba4` — docs(veloren): correct the TAIL() call count (2 → 1) and the blank count (771 → 772).
- `da8796c` — feat(veloren): capture `##`/`###` section markers as `context.section`.
- `53738ca` — backlog: add G6 — a converter-GENERATOR skill (the method one level up).
- (this retro) — STATE s007 + session note + kickoff.
