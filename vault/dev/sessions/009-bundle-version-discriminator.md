---
type: session
id: 009
date: 2026-08-21
lockit: wesnoth
gates_cleared: []
telemetry: { model_calls: null, input_tokens: null, output_tokens: null, est_cost_usd: null }
---

# Session 009 — the contract gets a version, and the version gets a pin

**Executed as an unattended brief (TASK-I3), not an interactive session.** No gates fired: no
intake, no re-profile, no change to the confirmed anatomy, no change to the row builder. One
field, one schema edit, one re-export. The Result went to a gitignored handoff file
(`data/handoff/TASK-I3-result.md`), copied out by hand; this note is the durable half.

This closes the loudest open thread s008 left: *"the bilingual manifest has no `bundle_version`
discriminator and the closed field list forbids adding one — cheap now, expensive after the
consumer's freeze."* It was flagged, not fixed, because that brief's field list won. This brief
existed to fix it, and the timing was the point — the **next** brief commits a curated-slice file
into this public repo that pins the manifest's hash, and adding a manifest field after that file
exists forces a re-pin of a committed public artifact.

## What happened

1. **Recon first, as a stop condition.** HEAD, the manifest object's exact shape, whether any
   version-like field already existed (a **kill signal** — do not add a second one, do not pick a
   winner), the manifest on disk with its three hashes, and where the manifest is assembled.
2. **`contracts/bundle.schema.json`** — `bundle_version` added as a **required** property, pinned
   `"const": "1.0.0"`. The object stays `additionalProperties: false`; no second exception was
   added (the one documented exception is still `upstream.po_revision_dates`).
3. **`scripts/wesnoth/export_bundle.py`** — `BUNDLE_VERSION = '1.0.0'` beside
   `CARTOGRAPHER_VERSION`, `'bundle_version'` first in `MANIFEST_KEYS` (so key order and the
   extra-key check carry it with no special case), emitted first in the manifest literal, and
   `verify_manifest()` now **refuses to write** a manifest carrying any other value.
4. **Re-exported Wesnoth pl.** `content_hash` **unchanged** at `f05b545f…ba8b666f` over 26,312
   rows and 24,477,591 bytes; `extraction_script_hash` moved `08f5cd2a…` → `3c46b350…`;
   `--check` **REPRODUCIBLE**. Tests **34 → 37**.
5. **Committed `3dc4230`** — schema, exporter, tests. Nothing under `data/`.

## Decisions

- **`const`, not `"type": "string"` — the entire point of the task.** A version *field* that
  accepts any string is decoration: two bundles that mean different things by the same token
  still validate identically, and a consumer learns nothing at validation time. With `const`, a
  consumer holding a mirror of `1.0.0` **rejects** a `2.0.0` bundle loudly. This is not
  hypothetical here — `scripts/veloren/export_bundle.py` carries its own comment recording that
  its `0.2.0` and `0.3.0` bundles validated against the same schema while a `selector` span meant
  opposite things, "and this string is the ONLY discriminator a consumer has."
- **Three versions, three owners, and the description says so.** `bundle_version` versions **the
  contract** (the bilingual gettext profile). `cartographer_version` versions **the producer** —
  one producer version can ship two contracts as easily as one contract ships from two producer
  versions. The Veloren `0.2.0`/`0.3.0` series belongs to a **different consumer's contract** and
  this one deliberately does not continue it. A future reader who assumes a single numbering
  across this repo is the next person to be bitten, so the schema says it in the field itself.
- **Bump rule, written into the description:** a change a conforming consumer can ignore is a
  **minor** bump; any change to the field list, to a field's type, or to a field's **meaning** is
  a **major** bump.
- **`cartographer_version` deliberately NOT bumped.** The schema's own rule is to bump it when a
  change would move `content_hash` for unchanged input. This one does not — and bumping it would
  have made a fourth manifest field differ, breaking the proof below.
- **`bundle_version` placed first** in the manifest, matching the Veloren exporter's key order. A
  discriminator is what a consumer reads before deciding how to read the rest.

## The proof, and why it is a proof and not an assertion

The brief allowed **exactly three** manifest fields to differ from the shipped bundle:
`bundle_version`, `extraction_script_hash`, `generated_at`. The re-export overwrites the shipped
manifest, so "compare the two files" was not available.

Instead: rebuild the shipped manifest **from the new one** — drop `bundle_version`, revert the
other two to their recorded values — re-serialise with the exporter's own write settings, and
check the bytes hash back to `53b1a334…d22852`, the sha256 recorded for the shipped file **before**
the task. They do. A fourth moved field, anywhere in the object, breaks that digest.

*The generalisable half:* when an artifact is overwritten, a recorded digest of the old bytes is
still a complete comparison — reconstruct the old artifact from the new one under your stated
diff and hash it back. Cheaper than keeping a copy, and it fails closed. This is the same
instinct as [[verify-count-changes]]' byte-identical baseline diff, applied where no baseline
file survives.

**A second, load-bearing check: the negative test was shown to fail.** A test that a wrong
`bundle_version` fails validation proves nothing unless it *stops passing* when the guard goes. I
loosened `const` → `"type": "string"` **in memory** and re-ran: a `2.0.0` manifest then validates
with zero problems. With the pin: `manifest.bundle_version: const '1.0.0' != '2.0.0'`. The test
fails exactly when the pin is removed, which is what makes it worth having.

## Tests — 34 → 37, and one of them is the fix

Kept adjacent so the pair reads as one idea, per the brief:

- `test_manifest_validates_against_published_schema` — the emitted manifest validates against
  `contracts/bundle.schema.json`, **read from the file**.
- `test_wrong_bundle_version_fails_validation` — `2.0.0`, `1.0.1`, `0.3.0` and `""` each fail with
  a `const` message naming the field; a manifest with the field removed fails as missing-required;
  and each is also refused by the exporter's own `verify_manifest`, so a wrong version cannot be
  *written*, only detected afterwards.
- `test_bundle_version_is_pinned_to_1_0_0` — pins the constant, the schema's `const`, its presence
  in `required`, and that it is the first key emitted. A bump is now a deliberate edit to a test.

**Validating against the *published file*, with no dependency.** `jsonschema` is not installed
here and installing it needs network, so the suite carries a ~40-line reader covering the keywords
the manifest object actually uses (`required`, `additionalProperties: false`, `type`, `const`,
`enum`, `pattern`). The point is not the reader — it is that the tests read
`contracts/bundle.schema.json` rather than a second copy of its rules. A mirror of the rules
inside the test file is exactly the drift these tests exist to catch.

## Push-back recorded rather than acted on

- **The brief's Context was wrong on one fact:** it said the working copy was still *one* commit
  ahead of the public remote. It is **four** (`c73f260` → `f08a24b` → `d93572b`, then this
  session's `3dc4230` makes five). Neither intervening commit touches the exporter, the schema or
  the bundle, so the premises held — reported, not reconciled quietly.
- **`source_ref`'s definition was already published.** AC 3 asked to write it into the schema
  description *if missing*; it was already there from s008. Nothing to do, case reported.
- **One decision refused: whether `--check` should read the schema *file* at runtime.** It
  validates against `verify_manifest()`, the exporter's hand-written mirror of the schema, which
  now also checks `bundle_version`. Making the producer read its own JSON Schema at export time
  needs either a `jsonschema` dependency on the write path (network, and a dependency the
  stdlib-only rule doesn't want) or the reader promoted out of the tests. That is an
  architectural decision the brief did not settle, so the schema-file reading lives in the tests,
  where the ACs actually demanded it — and the *written* manifest was separately confirmed valid
  against the published file. **Open thread, small.**
- **`scripts/wesnoth/export_bundle.py` line 3 still reads `# source: TASK-I1`.** Accurate
  provenance for the file's creation; TASK-I1 is not superseded by this task. Left alone. If the
  convention is "a file names the last task that changed it", that needs a decision.

## Promotions — five proposed, **all five approved by Marcin and APPLIED** at this retro

1. **NEW `heuristics/pinned-version-discriminator`** — *a version token that is not pinned is
   decoration.* Declare it `const`, never `type: string`. Carries both instances (Veloren's bite,
   Wesnoth's fix), the three-versions-three-owners table, the bump rule, and the caveat for the
   mirror-holder: a mirror only helps if they validate with something that honours `const`.
2. **NEW `heuristics/negative-test-mutation-proof`** — *a guard test proves nothing until it has
   been shown to fail.* Mutate the guard in memory, watch the test fail, restore. Generalises past
   schemas to refusals, verifiers and identity pins.
3. **UPDATE `conventions/byte-stable-artifact`** — rule 11 now says *pin* the discriminator (and
   the Wesnoth counter-case it recorded is marked closed); **new rule 12**, pin the payload not the
   manifest; **new rule 13**, a field's meaning is part of the contract — publish the description
   in the session that chose it, since it cannot move the payload hash.
4. **UPDATE `conventions/producer-contract-ownership`** — each contract owns its **own version
   series**, and the series do not converge any more than the contracts do; say it in the field's
   `description`, where the mirror-transcriber reads. Compatibility notes now ship the schema diff
   as text plus the `const` caveat.
5. **NEW `script-templates/schema_check.py`** — validate an emitted artifact against the
   **published schema file** with no dependency. `const` is the first keyword it implements, since
   a checker that ignores `const` reproduces the very defect it is there to catch. Verified against
   the real manifest (VALID), a wrong version (rejected), and a real row against `$defs.line`.

**`library/glossary.md`** gained three terms: *contract version vs producer version* · *pinned
(`const`)* · *mutation proof*. Nothing pending.

## Open threads

- **The curated slice** is the next brief and is a gated session with a human. It pins the
  manifest's sha256: **`f3724964b2ab73e7f3a78192150bd4261777b144420b3ffd51f406633d88eece`** — and
  that number moves on every re-export, because `generated_at` is inside the manifest. Pin the
  payload (`content_hash f05b545f…`) for identity; the manifest digest pins **one write**.
- **The consumer's mirror update** is a separate brief in the consumer's own repo: transcription,
  not derivation. The exact schema diff is in the Result. A mirror only helps if the consumer
  validates with something that honours `const` — a hand-rolled "required keys present, types
  match" checker reproduces the exact defect this session closed while appearing to validate.
- `--check` validates against the code mirror, not the schema file (above).
- Unchanged from s008: **G6** is writable (**F6** gates its output) · `source_ref`'s intent is
  chosen, not confirmed · char-limit hunt (F4) · Polish-audit track · F5/F6 security · G1/G2
  generators · F7 doc-freshness.

## Commits

- `3dc4230` — feat(contract): pin `bundle_version` in the bilingual manifest (TASK-I3).
- (this retro) — s009 retro: vault + session note + STATE + kickoff.
