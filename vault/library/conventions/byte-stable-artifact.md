---
type: convention
id: byte-stable-artifact
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "008"
updated_session: "009"
proposed_session: "007"
---

# Convention: a byte-stable artifact (when our output is someone else's input)

Most of what this system emits is a *report* — read once by a human, then discarded. Sometimes
it emits an **artifact**: a file another system reads, stores, and joins against later. The two
need different disciplines, and the difference is not cosmetic. **A report describes; an
artifact promises.** The promise is: *the same input produces the same bytes, forever.*

Break it and the failure is silent. A consumer that stored character offsets into our text now
points at the wrong characters; a consumer that joined on our ids now matches nothing. Nothing
crashes, no schema complains, and the corruption is discovered — if at all — long after the run
that caused it.

> **Two instances, two formats, two contracts.** Veloren/Fluent (s007, span-oriented,
> monolingual) and Wesnoth/gettext (s008, token-oriented, bilingual). The rules below are the
> part that came out **identical** in both — `serialize()` is character-for-character the same
> function — which is what makes them a convention rather than one project's habit.

## The rules

1. **Compose the payload in memory, as bytes, and write once.** UTF-8, **no BOM**, **LF only**,
   one JSON object per line, **exactly one** trailing newline, single binary write
   (`open(path,'wb')` / `write_bytes`). Never a text-mode write — it will silently give you
   CRLF on some platform, and the hash will move for no reason anyone can see.
2. **Fixed key order, and never `sort_keys`.** Key order is insertion order, which is why every
   row is built from **one dict literal in schema order**. Reordering keys changes the hash
   without changing meaning — the worst kind of diff. Drive both the key order and the
   "no keys outside the schema" check from **one** `ROW_KEYS` tuple.
3. **Hash the bytes you wrote, not a re-serialisation.** `content_hash = {algorithm, value,
   covers}` over the payload exactly as written. Re-serialising to verify would hide precisely
   the defects worth catching (text-mode write, BOM, CRLF).
4. **Write the rows before the manifest.** A torn run then leaves a bundle with *no manifest*
   (rejected on sight) rather than a manifest asserting a hash for bytes that are not there.
   **Standing rule to state in the schema: whoever rewrites the rows rewrites the manifest.**
   A row file that has moved while the manifest has not is the one corruption nothing else in
   the chain can detect.
5. **Verify the bytes as bytes.** A `verify_payload_bytes(payload)` that checks BOM / CR / NUL /
   trailing newline / no blank lines. This function is **format-independent** — it was written
   for Fluent and reused unchanged for gettext.
6. **Ship a `--check <artifact-dir> [<source-dir>]`.** Re-read from disk, re-validate, verify
   the hash against the bytes on disk, and — given the source — **re-export in memory and
   byte-compare**, reporting `REPRODUCIBLE` or the first differing line. This is what turns
   "byte-stable" from a claim into a test. It catches a text-mode write, a locale-dependent
   sort, or a parser change that moved a string; a schema can see none of those.
7. **Pin the payload hash in the tests.** Two pins are better than one: a **synthetic** corpus
   pin that runs on a fresh clone (licence-clean, no client data), and a **real-corpus** pin
   that skips when the gitignored data is absent. The real risk was never nondeterminism — it
   is a future parser edit silently moving every string.
8. **Declare anything that is not a verbatim slice.** If the text is normalised, name the
   normalisation in a producer/version field so a consumer diffing a moved hash can find out
   *why*. (Veloren: `producer_version = 0.1.0+norm=strip-join-lf`. Wesnoth: verbatim-raw, and
   the schema says so.)
9. **Sort deterministically, and say so.** **Byte-sorted, never locale-sorted** — a locale-aware
   sort makes the artifact depend on the machine's environment.
10. **Accumulate problems, then refuse once.** Three verifiers (`verify_rows`,
    `verify_manifest`, `verify_payload_bytes`), each returning `list[str]`, all collected, then
    a single refuse-to-write. Print the first ~25. A warning nobody reads is not a check.
    Scope every refusal per [[refusal-scope-discipline]].
11. **Keep a version discriminator on the artifact — and PIN it in the schema.** Two revisions
    of a contract can validate against the same schema while meaning **opposite things by the
    same token** (Veloren 0.2.0 → 0.3.0: a `selector` span went from covering a whole construct
    to covering one piece of syntax). The version string is then the *only* discriminator a
    consumer has. **Never reuse a version** — and declare it `"const": "<version>"`, never
    `"type": "string"`, or the discriminator is decoration: a consumer's mirror validates a
    bundle from another contract version and reads it as though nothing changed. See
    [[pinned-version-discriminator]] for the full rule and the two instances.
    *(The Wesnoth bilingual manifest was the recorded counter-case — a closed field list with
    no such field. Closed at s009: `bundle_version`, required, `const "1.0.0"`.)*
12. **Pin the payload, not the manifest.** The manifest's own digest moves on every run, because
    `generated_at` lives inside it. `content_hash` over the payload is the artifact's stable
    identity; a sha256 of `manifest.json` pins **one write** of one manifest. A downstream file
    that records "the manifest's hash" as though it identified the bundle will re-pin on every
    export and read as drift when nothing drifted. Say which one you mean, in the note that
    records it.
13. **A field's meaning is part of the contract — publish it where the transcriber reads.** A
    field whose meaning was chosen by the exporter but never written into the schema's
    `description` is a field the mirror-holder will guess at. Writing a description costs
    nothing (it cannot move the payload hash), so there is no reason to defer it past the
    session that made the choice.

## How to apply
Start from [[byte_stable_jsonl]] — it is items 1–7 and 10 as working code. Add the row builder
and the contract's field list; leave the byte layer alone. Then see
[[producer-contract-ownership]] for who owns the schema you are emitting against, and
[[derived-identity-keys]] for the id.

**Companion:** [[refusal-scope-discipline]] · [[derived-identity-keys]] ·
[[producer-contract-ownership]] · [[boundary-vocabulary-mapping]] ·
[[pinned-version-discriminator]] · [[negative-test-mutation-proof]] · [[schema_check]].
