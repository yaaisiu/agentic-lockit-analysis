---
type: heuristic
id: pinned-version-discriminator
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "009"
---

# Heuristic: a version token that is not PINNED is decoration

An artifact that another system stores and joins against should say **which version of the
contract it conforms to**. Almost everyone gets that far. The half that gets skipped is the
pin: declaring the field `"type": "string"` instead of `"const": "<version>"`.

**Rule:** in the schema, a contract-version field is declared **`const`**. Not `type: string`,
not a `pattern`, not an `enum` of every version ever shipped. If a consumer holding a mirror of
version *N* can validate a bundle written against version *N+1* **without error**, the field is
decoration — it records history for a human reading the file, and does nothing at the moment
that matters.

## What goes wrong without the pin, in one sentence

Two revisions of a contract can validate against the same schema while meaning **opposite things
by the same token** — and an unpinned version field lets the newer bundle through the older
consumer's validator, which then reads it as though nothing had changed.

## The two instances

- **Veloren (s007, the bite).** `0.2.0` → `0.3.0` changed what a `selector` **span** covers: from
  the whole construct *including its translatable variant bodies* to one piece of selector
  syntax with the bodies outside it. A span is used downstream as a **mask**. Under the old
  reading the mask swallows translatable text; under the new one it does not. **Both bundles
  validate against the same schema.** The exporter's own comment records that the version string
  "is the ONLY discriminator a consumer has. Never reuse a version."
- **Wesnoth (s008 → s009, the fix).** The bilingual manifest shipped with **no** contract-version
  field at all, and `additionalProperties: false` meant a consumer could not add one either.
  s008 flagged it and did not fix it; s009 added `bundle_version`, required, `const "1.0.0"`,
  in the window before a downstream file pinned the manifest.

## Three versions, three owners — say which one you mean

The word "version" attaches to at least three different things in a producer repo, and a reader
who assumes one numbering across the repo is the next person to be bitten:

| field | versions | moves when |
|---|---|---|
| `bundle_version` / contract version | **the contract** — the field list and what each field *means* | the contract changes |
| `cartographer_version` / producer version | **the producing code** | a change would move the payload hash for unchanged input |
| another consumer's series | **a different contract entirely** | that consumer's contract changes — unrelated, and never to be continued here |

One producer version can ship two contracts as easily as one contract can ship from two producer
versions. **Write this distinction into the field's own `description`**, not only into a session
note: the person who needs it is transcribing your schema into a mirror, months later, and the
schema is the only file they are reading.

## The bump rule, stated in the schema

- **Minor** — a change a conforming consumer can **ignore**.
- **Major** — any change to the **field list**, to a field's **type**, or to a field's
  **meaning**. The third is the one that has no other detector.

## How to apply

1. Declare the field `"const"` in the schema, `required`, inside the closed field list.
2. Emit it from the **same key-order mechanism** that drives every other field — no special case
   outside it — and put it **first**, since it is what a consumer reads before deciding how to
   read the rest.
3. Have the producer's own self-check **refuse to write** any other value, so a wrong version
   cannot be produced, only rejected.
4. Write the negative test, and prove it fails when the pin is loosened
   ([[negative-test-mutation-proof]]).
5. Pin the value in a test as well, so a bump is a deliberate edit to a test rather than silent
   drift.
6. **Tell the mirror-holder the caveat:** a mirror only helps if they validate with something
   that honours `const`. A hand-rolled "required keys present, types match" checker reproduces
   this exact defect while appearing to validate.

**Companion:** [[byte-stable-artifact]] rule 11 · [[producer-contract-ownership]] ·
[[negative-test-mutation-proof]] · [[schema_check]].
