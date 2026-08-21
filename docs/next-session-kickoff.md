# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 HoI4 (Clausewitz) — first proprietary lockit. s005 public-release
> prep. s006 went PUBLIC + doc reconciliation. s007 the first bundle exporter. s008 the second
> exporter, and the first contract we publish ourselves. **s009 — that contract now carries a
> version, pinned with `const`.**

## Where we are
- **Four lockits, four formats, all gated + tooled — and now TWO producer roles.**
  `scripts/veloren/export_bundle.py` emits a span-oriented **monolingual** bundle for one
  consumer; `scripts/wesnoth/export_bundle.py` (new in s008) emits a token-oriented **bilingual**
  bundle for a different one. **They deliberately do not converge**, and that is the design.
- **We now publish a contract.** `contracts/bundle.schema.json` is normative for the bilingual
  gettext profile; the consumer's copy is a validating mirror. Ownership, settled with Marcin:
  **this repo owns the *profile*** (anatomy, the `segment_id` function, field meanings) because it
  is the single producer both consumers key to; **each consumer owns its own *bundle contract*.**
  We still never write into a consumer's repo.
- **The contract is VERSIONED, and the version is PINNED (s009).** The bilingual manifest now
  requires `bundle_version: "1.0.0"`, declared in the schema with **`const`** — not
  `"type": "string"`. That distinction is the whole mechanism: an unconstrained version token lets
  two bundles that mean different things by the same token validate identically (which is what bit
  the Veloren contract at 0.2.0→0.3.0). Three versions, three owners: `bundle_version` = the
  contract · `cartographer_version` = the producer · Veloren's `0.2.x` = a **different consumer's**
  contract, deliberately not continued here.
- **Wesnoth pl is exported and reproducible:** 26,312 rows, 0 `segment_id` collisions, `--check`
  REPRODUCIBLE. Bundle + census live in gitignored `data/bundles/` — CC-BY-SA content, public repo.
  Wesnoth tests 22 → 34 → **37**. Commits `c73f260`, `3dc4230`. Re-exported at s009 with
  `content_hash` **unchanged** (`f05b545f…`) — the proof that only the manifest moved.
- **Repo is PUBLIC** (`github.com/yaaisiu/agentic-lockit-analysis`). Treat every commit as
  outward-facing. Nothing is pushed from s007 or s008 — `git push` is `ask`-gated.

## The library grew this retro — consult it BEFORE re-deriving
All twelve pending promotions were applied at the s008 retro (s008's five, plus s007's seven,
which had been pending a session). **Recognise before re-inferring** — if you are about to write
an exporter, an identity function, or a refusal, these already exist:

- **`conventions/byte-stable-artifact`** — the eleven rules two exporters agreed on. Start here
  for anything another system will store and join against.
- **`conventions/producer-contract-ownership`** — we own the *profile*, each consumer owns its
  *bundle contract*, contracts don't converge, we never write into a consumer's repo.
- **`conventions/derived-identity-keys`** — the export's join key is **not** the toolkit's
  internal id; publish the preimage; pin external vectors; state the separator's precondition.
- **`conventions/boundary-vocabulary-mapping`** — map our labels onto a consumer's enum *in the
  exporter*; never rename the registry; pass `unknown` through.
- **`heuristics/refusal-scope-discipline`** — name the output field a refusal protects, or it
  isn't a refusal.
- **`heuristics/identity-proof-scope`** — a collision proof covers one function; say which.
- **`heuristics/construct-spans-not-tokens`** — return `(start, end, text)`; a span used as a
  mask must never contain translatable text.
- **`script-templates/byte_stable_jsonl.py`** — the byte layer as working code. A third exporter
  should not hand-write `serialize()` again.

**s009 added three more** (approved + applied at its retro):
- **`heuristics/pinned-version-discriminator`** — a version token that is not pinned (`const`) is
  decoration; a mirror validates the wrong contract and reads it as though nothing changed.
- **`heuristics/negative-test-mutation-proof`** — mutate the guard, watch the negative test fail,
  restore. A guard test that has never failed is a passing test, not a proof.
- **`script-templates/schema_check.py`** — validate an emitted artifact against the **published
  schema file**, no dependency. Use it rather than growing a second copy of the contract's rules.

Updated too: `byte-stable-artifact` (rule 11 now *pins* the discriminator; new rules 12–13),
`producer-contract-ownership` (each contract owns its own version series), and 3 glossary terms.

Updated too: `ftl_parse_template.py` (`placeables()` → spans), `construct-origin-labeling`,
`fluent-ftl` (section markers), `outlier-hunting` (count from the parser, not grep), and the
glossary (8 new terms).

## THEN — Marcin's call (no gate mid-flight)
1. **The curated slice** — the next brief, and it *is* a gated session with a human: strata, the
   reference pool, the self-consistency subset. `placeholder_check` was built so it can either
   exclude the **22 known-bad rows** or include them deliberately labelled. Note that **six
   domains are 0% translated** (5,874 rows) and contribute nothing to an eval pool.
   **s009 was the window before this one** — the slice commits a file that pins the manifest, and a
   manifest field added afterwards forces a re-pin of a committed public artifact. Two numbers it
   needs: manifest sha256 `f3724964b2ab73e7f3a78192150bd4261777b144420b3ffd51f406633d88eece`
   (**which moves on every re-export** — `generated_at` lives inside the manifest) and
   `content_hash f05b545f…ba8b666f`, which does not. **Pin the payload for identity; a manifest
   digest pins one write.**
2. **G6 — the converter-GENERATOR skill, now actually writable.** s008 was the second instance the
   design needed. `vault/dev/backlog.md` now records the real input: **11 items the two exporters
   share** (the generator's fixed skeleton) vs **7 that must come from a target package** (the part
   a JSON Schema cannot state). A generator emits the 11, takes the 7 as declaration, and leaves
   only the row builder per (format, contract) pair. **F6** still gates its output.
3. **The consumer's mirror update** — *done here, not there.* `bundle_version` landed at s009, so
   the consumer's validating mirror of `contracts/bundle.schema.json` is now one field behind. That
   is a brief in **their** repo and it is transcription, not derivation: the exact schema diff is in
   the s009 Result. **The caveat worth passing on:** a mirror only helps if they validate with
   something that honours `const` — a hand-rolled "required keys present, types match" checker
   reproduces the exact defect this closed, while appearing to validate.
4. **Resume lockit work.** A1 is largely done (s008 found 22 real defects across the full Polish
   locale — the "our tool caught real bugs in a delivery" report now has evidence at corpus scale);
   remaining: the char-limit hunt (**F4**, the one untested §5 anatomy) · a new format
   (JSON/`.arb`/`.strings`/xliff) · the Polish-audit track.
5. **Security F5/F6** — input hardening (injection-aware profiling) and/or the generated-script
   safety gate. Neither built; **F6 is a prerequisite for G6**.
6. **QA-generators G1/G2** (translator brief, pseudo-loc) or **F7** (doc-freshness check).

## Three habits worth keeping (all earned the hard way)
- **A refusal must name the field it protects.** If you cannot say which output field becomes
  unreliable when the defect stands, it is a *reported number* or a *per-row verdict*, not a
  refusal. s008 refused 26,312 rows over a header two domains didn't need.
- **A proof of identity is a proof about ONE function.** Quote a collision count and name the
  function and preimage it covers, in the same sentence. Good news without its scope reads as
  coverage it does not have.
- **A guard test proves nothing until it has been shown to fail.** s009's negative test says a
  wrong `bundle_version` fails validation — worth having only because loosening `const` to
  `"type": "string"` *in memory* was watched to make it pass. Mutate the guard, watch the test go
  green, put it back. A test that has never failed is a passing test, not a proof.
- **When an artifact is overwritten, its recorded digest is still a complete comparison.**
  Reconstruct the old bytes from the new ones under your stated diff and hash them back. s009
  proved "exactly three manifest fields moved" that way, with the old file already gone.
