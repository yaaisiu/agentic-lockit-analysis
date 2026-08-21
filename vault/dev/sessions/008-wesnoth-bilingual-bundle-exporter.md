---
type: session
id: 008
date: 2026-08-21
lockit: wesnoth
gates_cleared: []
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 008 — Wesnoth bilingual bundle exporter (the second producer)

**Executed as an unattended brief (TASK-I1), not an interactive session.** No gates fired: no
intake, no re-profile, no change to the confirmed anatomy. The output is a **second producer
role** — Cartographer now exports a profiled gettext lockit as a normalized **bilingual** bundle
for an MT-benchmarking consumer, and **publishes the schema it emits** so that consumer validates
against a contract owned by the producer instead of guessing at one.

The result went to a gitignored handoff file (`data/handoff/TASK-I1-result.md`), copied out by
hand. This note is the durable half.

## Why a second hand-written exporter, when the backlog says "write a generator"

Backlog **G6** — read first, as the brief required — says `scripts/veloren/export_bundle.py` is a
one-off and the generalisation is a *converter-generator*, "worth reading before anyone
hand-writes a second exporter." The brief overruled it deliberately, and the reasoning is the
useful part: **a generator that generalises over exporters cannot be designed from a single
instance.** What makes G6 writable is having two hand-written exporters to diff. It is now
writable — see *G6 is now writable* below.

## What happened

1. **Recon first, and it was a stop condition.** Read the foundation reader (`po_parse.py`,
   identity `_internal_id`), `completeness.py` (state vocabulary), `validate_placeholders.py`,
   `validate_markup.py` + `po_tokens.py`, `list_context_prefixes.py` (`family()`), and confirmed
   rather than assumed that **exactly one exporter existed** here (the Veloren one).
2. **Provenance probe — passed, and read without a subprocess.** `upstream` =
   `https://github.com/wesnoth/wesnoth.git` @ `2f99e187a804e6e6003b28df61023af0c37badc9`, branch
   `master`, read from `.git/config` / `.git/HEAD` / `.git/refs`. **No git operation needed a
   permission prompt and nothing was added to the allow list.** The exporter parses `.git` files
   directly rather than shelling out: `git -C` is not an allowed prefix, and a provenance probe
   that needs a prompt is one that fails in an unattended run.
3. **`contracts/bundle.schema.json` published here**, describing the bilingual gettext profile.
   Its descriptions carry the four things a consumer cannot otherwise reproduce: the exact
   `segment_id` preimage, what `extraction_script_hash` covers, what `content_hash` covers, and
   that `_display` is derived and non-normative.
4. **`scripts/wesnoth/export_bundle.py`** (879 lines, stdlib only). Reuses the Veloren exporter's
   *engineering* (byte-stable payload, refuse-to-write-over-problems, `--check` re-export
   byte-compare, rows written before manifest) without reusing its *contract*.
5. **Exported Wesnoth pl:** 26,312 rows, 24,477,591 bytes,
   `content_hash f05b545f…ba8b666f`. `--check` reports **REPRODUCIBLE**. Tests **22 → 34**.

## Decisions

- **Ownership, settled with Marcin and narrower than "this repo owns the schema".** This repo
  owns the **profile** — the lockit anatomy, the `segment_id` function, what each field means —
  because it is the single producer and both consumers key to it. **Each consumer owns its own
  bundle contract**: the bilingual profile here and the span profile the other consumer needs are
  different contracts *by design* and must never be merged. The standing rule that we never write
  into a consumer's repo is unchanged — deciding what we emit and editing someone else's files
  are different things.
- **`segment_id` is a new function and `internal_id` was NOT reused.**
  `<textdomain>:sha1((msgctxt or "") + "|" + msgid_raw)[:12]`. `internal_id` is the **same shape,
  10 hex, a different preimage** (domain and plural hashed in behind `0x1f`). Reusing it produces
  a bundle that validates, looks correct, and joins to nothing. Four vectors computed outside this
  repo are pinned in the tests; a stability test shifts every line number and adds a
  `msgid_plural` and asserts no id moves; `verify_rows` recomputes the id from each row's own
  normative fields before anything is written.
  - **Hazard recorded, not fixed:** the separator is a literal `|`, which occurs in Wesnoth text
    as the `$var|` terminator. The preimage is injective here **only** because `msgctxt` is empty
    on every Wesnoth entry. Written into the schema description for the next lockit that uses it.
- **Two text forms, one normative.** `source_en`/`target_pl` are raw PO strings, escapes intact —
  the id is computed over the raw msgid and any future offset anchors there. `*_display` are
  unescaped, derived, non-normative. **Detection runs on the raw form** (that is what the
  `po_tokens` regexes are written against); display is derived afterwards and is never an input.
  Cost measured: only **1,211 of 26,312 rows** actually differ between the two forms.
- **`pool` is owned by the export** (`eval` / `untranslated`; never `reference`). Fuzzy collapses
  into `untranslated` — gettext skips fuzzy at runtime — while `fuzzy` survives as its own
  boolean so the distinction is not lost.
- **`placeholders` are plain tokens, not spans.** Spans are strictly more informative and are what
  the *other* consumer wants; this profile's schema is closed and would reject them. Said in the
  compatibility note; not built.
- **`last_changed` is null throughout, and says why.** The checkout is shallow, so `git log` would
  return the same grafted-commit date for all 32 files — a different question than the one asked.
  A fabricated-looking constant is worse than null.

## The refusal that was wrong — the session's real lesson

The first structural rule refused the **entire 26,312-row export** because two `pl.po` files
(`wesnoth-editor`, `wesnoth-tutorial`) carry no `Plural-Forms` header. Both domains have **zero
plural entries**: nothing in the bundle depended on the header. Narrowed to fire only when a
domain actually has a plural entry.

This is **the same defect class the brief had already pre-empted once** — it carved out an
explicit exception so cross-locale *content* findings (a target that dropped a `$var`) could never
block, precisely because "conflating them makes this task produce nothing on its first run." The
rule was right about content findings and I reintroduced it for header metadata. **Twice in
consecutive passes makes it a rule, not an incident:** *a refusal must be keyed to something the
output actually depends on, not to well-formed metadata.* If you cannot name the field that
becomes unreliable, it is a reported number or a per-row verdict — not a refusal.
Proposed as heuristic `refusal-scope-discipline` below; L1 memory written.

## The identity-proof hazard — hardened in the vault this session

Four notes said "26,312/26,312 unique, 0 collisions" **without naming which id it measured**. It
measures `internal_id`. `segment_id`'s collision count was *unproven* until this session measured
it (also 0 over the same 26,312 — a second result, not the same one). Reading the old proof as
covering the new id is the cheapest way to skip the vectors and ship an unjoinable bundle.
**Applied, not merely proposed:** `profile.md`, `toolkit.md` and `open-questions.md` now name the
function; the s001 session log got a dated forward-pointer (history preserved, s006 precedent).
*Good news is a documentation hazard when it is stated without naming what it covers.*

## The numbers (each consumed by the next brief)

- **26,312 rows · 0 `segment_id` collisions · all four id vectors green.**
- **32 textdomains in `.pot`, 32 with a `pl.po` — none missing.**
- **`pool`:** `eval` 14,914 · `untranslated` 11,398 (= 9,647 empty + 1,751 fuzzy).
  **Six domains are 0% translated** (5,874 rows) and contribute nothing to an eval pool.
- **54 plural entries**, `nplurals=3` on 30 of 32 domains, **0 arity disagreements**.
  `wesnoth-editor` / `wesnoth-tutorial` have no `Plural-Forms` header *and* no plurals.
- **712 rows carry a derived `msgctxt`** (129 distinct caret prefixes) — Wesnoth sets a real
  `msgctxt` on **zero** entries, which is exactly what makes the preimage injective.
- **1,211 rows** where raw ≠ display (4.6%) — how much the escaping decision actually touches.
- **`markup_flags`:** pango 1193 · newline 905 · po4a 216 · entity 63 · docbook 51 · metasyntax 23.
- **`string_class`** (30 of 82 enum values occur; `unknown` 0): `campaign/plain` 19,743 ·
  `ui/plain` 1,518 · `core/plain` 1,381 · `help/plain` 1,088 · `units/plain` 788 · … ·
  `campaign/gender_agreement` 116 · `units/gender_agreement` 64 · `help/gender_agreement` 62.
- **`placeholder_check`:** `not_applicable` 25,891 · `ok` 399 · `target_only` 15 · `source_only` 6
  · `mismatch` 1. Only 538 of 26,312 source strings carry a placeholder at all.

## A1 advanced as a side effect — 22 real upstream defects, full Polish locale

The backlog's **A1** ("run the prepared cross-locale tools on a real translation — the first *our
tool caught a real bug in a delivery* report") has effectively been run at corpus scale. **22 rows
across 32 domains carry genuine upstream placeholder defects**, and they reconcile exactly with
the existing validator: the four findings it reports for `wesnoth-lib` are three rows (one entry
both invents `$key` **and** drops `$tag` → classified `mismatch`), and my row counts for that
domain are those three. Two clusters are **stale translations** — the English lost a variable in
a rewrite and the Polish still carries the old one: eight `wesnoth-ei` rows and six `wesnoth`
rows (`$friends`, `$enemies`, `$cost`, `$remaining_turns`, `$herbs_needed`, and a
`{AMOUNT}`/`{RACE}` WML-macro pair). Excellent known-bad reference cases; terrible eval rows.
*Surface, don't fix — upstream CC-BY-SA data.*

**Recorded limitation:** for plurals the target token set is the **union** over all forms
(mirroring `validate_placeholders`' rule that a singular form legitimately omits the count
variable). Cost: a token dropped from exactly one form of a plural reads as `ok`. In the
docstring, not fixed — fixing it would report the whole plural family as broken.

## G6 is now writable — and wasn't before

Diffing the two exporters yields **eleven items shared** (the generator's fixed skeleton) against
**seven that must come from a target package** (the part a JSON Schema cannot state). Written in
full into `vault/dev/backlog.md` under G6. The headline: a G6 generator emits the eleven as
scaffolding, takes the seven as the package's declaration, and leaves **only the row builder** to
be written per (format, contract) pair. Of the eleven, the most transferable single rule is
**vocabulary mapping at the boundary** — map our labels onto the consumer's enum *in the exporter*
(`ORIGIN_MAP` in Veloren, `CARET_SLUG` here), never rename the registry to chase a consumer. That
now has two independent instances.

## Push-back recorded rather than acted on

**The bilingual manifest has no contract-version discriminator, and the closed field list forbids
adding one.** This repo has already been bitten by exactly that absence: the Veloren exporter's
own comment records that 0.2.0 and 0.3.0 bundles **validate against the same schema while meaning
opposite things by the same token**, and that the version string is the *only* discriminator a
consumer has. `cartographer_version` is the producer's version, not the contract's. No field was
added — the brief says its field list wins — but it is cheap now and expensive after the
consumer's freeze. Flagged to the consumer in the compatibility note.

Two smaller ones: **`source_ref` was undefined by the brief** and was chosen (the gettext `#:`
refs, as provenance into the *game's* source), named explicitly as the one field to challenge; and
**a ninth `string_class` domain group, `tools`**, was added beyond the eight the brief listed,
because folding a build-tooling domain into `core` or `ui` would put a false label on 96 rows —
the exact failure the "not the bare textdomain" rule exists to prevent.

## Corrections to the brief's own Context, reported not reconciled quietly

1. **There is no `contracts/` directory in this working copy** — the brief implied there was. If a
   consumer was told this repo already published a contract, it was not published from here.
2. **This copy is ahead of the public remote by exactly one commit, and that commit *is* the
   0.3.0 one** (`407f5bf`). The Veloren exporter here hardcodes `0.3.0`, not `0.2.0` — one
   unpushed local commit, not a divergent branch.
3. **"Roughly four in wesnoth-lib" is four *findings* over three *rows*** — a units mismatch, not
   a missing row.
4. **Two `pl.po` files ship with no `Plural-Forms` header** — an upstream metadata defect worth
   knowing about, and the trigger for the refusal lesson above.

## Hardened (applied this session)

- Bundle export + all its rules → `vault/lockits/wesnoth/toolkit.md` (new § *Bundle export — a
  NORMATIVE output*), and the exporter + `--check` added to the skill's `SKILL.md` command listing
  (authorized by the brief; tests 22 → 34 recorded there).
- Identity-proof scope named in `profile.md`, `toolkit.md`, `open-questions.md`; dated
  forward-pointer added to the s001 log.
- G6's actual design (11 shared / 7 from the package) → `vault/dev/backlog.md`.
- Memory (L1): [[refusal-scope-discipline]], [[identity-proof-names-its-function]].

## Promotions proposed (awaiting approval — NOT applied)

s008's five, plus the **seven from s007 that are still unapplied** (see that note; none of them
landed). Where the two overlap, s008 supplies a second instance, which is the evidence s007's
proposals were missing.

1. **NEW heuristic `refusal-scope-discipline`** — a refusal must be keyed to something the output
   actually depends on, never to well-formed metadata; if you cannot name the field that becomes
   unreliable, it is a reported number or a per-row verdict field. Two instances, consecutive
   sessions. *(This is the strongest of the five.)*
2. **NEW convention `producer-contract-ownership`** — when this repo produces for a consumer: we
   own the **profile** (anatomy, identity function, field meanings), each consumer owns its
   **bundle contract**, contracts for different consumers must not be converged, and we never
   write into a consumer's repo. Settled with Marcin 2026-08-21; two consumers now exercise it.
3. **NEW convention `derived-identity-keys`** — a bundle's join key is a pure function of a named
   tuple of source fields, never of a locator; the toolkit's internal id and an export's id are
   **different functions** and must not be conflated; pin vectors computed outside the repo; state
   the preimage's injectivity precondition. (Absorbs the `|`-separator hazard as the worked
   example.) Also fixes the documentation hazard by rule rather than by note.
4. **STRENGTHEN s007's proposed convention `byte-stable-artifact`** (still unapplied) — s008 is the
   second independent instance, and `serialize()` + `verify_payload_bytes()` are now provably
   format-independent. Promote with the accompanying `byte_stable_jsonl.py` template s007 also
   proposed.
5. **STRENGTHEN s007's proposed update to `construct-origin-labeling`** — but promote **vocabulary
   mapping at the boundary** to its own convention rather than a clause inside an origin-labelling
   note. It now has two instances (`ORIGIN_MAP`, `CARET_SLUG`) and is broader than origin labels:
   *map at the boundary, never rename the registry to chase a consumer.*

## Open threads

- **The five above + s007's seven.** Twelve pending promotions is the largest debt in the repo.
- **G6** is now writable (design in the backlog); **F6** still gates its output.
- **`bundle_version`** absent from the bilingual manifest — flagged, not fixed; cheapest to fix
  before the consumer's schema freeze.
- **`source_ref`'s intent** — chosen, not confirmed. The one field for the consumer to challenge.
- **The curated slice** (strata, reference pool, self-consistency subset) is the next brief and is
  a gated session with a human. `placeholder_check` exists so it can label the 22 known-bad rows.
- Untouched from before: char-limit hunt (F4) · Polish-audit track · F5/F6 security · G1/G2
  generators · F7 doc-freshness.

## Commits

- `c73f260` — feat(wesnoth): bilingual bundle exporter + publish the bundle contract (TASK-I1).
- (this retro) — vault hardening + STATE s008 + session note + kickoff.
