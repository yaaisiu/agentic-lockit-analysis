# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 Wesnoth (gettext). s001 corpus-wide + cross-locale QA. s002 Veloren (Fluent). s003
> A Dark Forest (Godot CSV). s004 HoI4 (Clausewitz) — first proprietary lockit. s005 public-release
> prep. s006 went PUBLIC + doc reconciliation. s007 the first bundle exporter. **s008 — the second
> exporter, and the first contract we publish ourselves.**

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
- **Wesnoth pl is exported and reproducible:** 26,312 rows, 0 `segment_id` collisions, `--check`
  REPRODUCIBLE. Bundle + census live in gitignored `data/bundles/` — CC-BY-SA content, public repo.
  Wesnoth tests 22 → 34. Commit `c73f260`.
- **Repo is PUBLIC** (`github.com/yaaisiu/agentic-lockit-analysis`). Treat every commit as
  outward-facing. Nothing is pushed from s007 or s008 — `git push` is `ask`-gated.

## FIRST — 12 library promotions await approval (the repo's largest standing debt)
**s007 proposed seven; none were applied.** s008 proposes five more, and where they overlap s008
supplies the *second instance* that s007's proposals were missing. Both lists are in their session
notes (`007-veloren-bundle-exporter.md`, `008-wesnoth-bilingual-bundle-exporter.md`).

s008's five, strongest first:
1. **NEW heuristic `refusal-scope-discipline`** — a refusal must be keyed to something the output
   *actually depends on*, never to well-formed metadata. Bitten twice in consecutive passes.
2. **NEW convention `producer-contract-ownership`** — we own the profile, each consumer owns its
   bundle contract, don't converge contracts, never write into a consumer's repo.
3. **NEW convention `derived-identity-keys`** — an export's join key is a different function from
   the toolkit's internal id; pin externally-computed vectors; state the preimage's injectivity
   precondition.
4. **STRENGTHEN s007's `byte-stable-artifact`** (+ its `byte_stable_jsonl.py` template) — now
   provably format-independent across two exporters.
5. **PROMOTE "vocabulary mapping at the boundary" to its own convention** (s007 had it as a clause
   inside `construct-origin-labeling`) — two instances now: `ORIGIN_MAP`, `CARET_SLUG`.

Approve/reject each, then apply and commit citing the session that produced it.

## THEN — Marcin's call (no gate mid-flight)
1. **The curated slice** — the next brief, and it *is* a gated session with a human: strata, the
   reference pool, the self-consistency subset. `placeholder_check` was built so it can either
   exclude the **22 known-bad rows** or include them deliberately labelled. Note that **six
   domains are 0% translated** (5,874 rows) and contribute nothing to an eval pool.
2. **G6 — the converter-GENERATOR skill, now actually writable.** s008 was the second instance the
   design needed. `vault/dev/backlog.md` now records the real input: **11 items the two exporters
   share** (the generator's fixed skeleton) vs **7 that must come from a target package** (the part
   a JSON Schema cannot state). A generator emits the 11, takes the 7 as declaration, and leaves
   only the row builder per (format, contract) pair. **F6** still gates its output.
3. **Fix `bundle_version` before the consumer freezes its schema.** The bilingual manifest has no
   contract-version discriminator and its closed field list forbids one — the exact absence that
   bit the Veloren contract at 0.2.0→0.3.0, where two incompatible meanings validated identically.
   Cheap now, expensive later. Needs a word with the consumer, not a code change here.
4. **Resume lockit work.** A1 is largely done (s008 found 22 real defects across the full Polish
   locale — the "our tool caught real bugs in a delivery" report now has evidence at corpus scale);
   remaining: the char-limit hunt (**F4**, the one untested §5 anatomy) · a new format
   (JSON/`.arb`/`.strings`/xliff) · the Polish-audit track.
5. **Security F5/F6** — input hardening (injection-aware profiling) and/or the generated-script
   safety gate. Neither built; **F6 is a prerequisite for G6**.
6. **QA-generators G1/G2** (translator brief, pseudo-loc) or **F7** (doc-freshness check).

## Two habits worth keeping (both earned the hard way)
- **A refusal must name the field it protects.** If you cannot say which output field becomes
  unreliable when the defect stands, it is a *reported number* or a *per-row verdict*, not a
  refusal. s008 refused 26,312 rows over a header two domains didn't need.
- **A proof of identity is a proof about ONE function.** Quote a collision count and name the
  function and preimage it covers, in the same sentence. Good news without its scope reads as
  coverage it does not have.
