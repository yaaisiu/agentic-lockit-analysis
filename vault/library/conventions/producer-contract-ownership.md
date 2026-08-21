---
type: convention
id: producer-contract-ownership
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "008"
---

# Convention: who owns what, when this system produces for a consumer

Cartographer analyses lockits; sometimes it also **produces** for a downstream project that
never opens a raw lockit file. That relationship needs an ownership rule stated once, because
the natural failure mode is either extreme: silently adopting whatever a consumer's draft says,
or declaring that we own everything and letting two consumers' needs collide.

**Settled with Marcin, 2026-08-21, with two live consumers exercising it:**

## The split

- **This repo owns the PROFILE.** The lockit anatomy, the identity function, and what each
  field *means*. Nothing else can coherently own it: we are the single producer, and every
  consumer keys to it. If two consumers disagreed about what a field means, the producer would
  have to emit two incompatible readings of the same data.
- **Each consumer owns its own BUNDLE CONTRACT.** The field list, the shape, what it needs.
  A consumer asking for spans and a consumer asking for bilingual pairs are not two versions of
  one contract — they are two contracts.
- **Therefore: do not converge contracts.** Two exporters against two contracts is the correct
  design, not duplication to be refactored away. (Veloren: span-oriented, monolingual. Wesnoth:
  token-oriented, bilingual. Merging them would force one consumer to accept a shape it cannot
  use, and both to accept a schema that validates neither strictly.)
- **We never write into a consumer's repository.** Deciding what we emit and editing someone
  else's files are different things, and only the first is ours. When we find a bug on their
  side — and we have, twice — **report it, don't fix it**. Two sessions editing one file is
  worse than a reported bug.
- **Where our field list and a consumer's copy disagree, ours wins and theirs mirrors.** That
  is what "normative" means, and it is only defensible because of the first bullet.

## Publish the contract, in our repo

The producer commits the schema (`contracts/<name>.schema.json`); the consumer's copy becomes a
**validating mirror**. A divergence between them is then *a bug with a named owner*, instead of
two projects each assuming the other is right.

**Scope the schema file explicitly in its own description** — "this file describes the bilingual
gettext profile; the span profile is a different contract" — or the next reader will merge them.

## What a schema cannot say, and therefore must be said in prose

JSON Schema validates *shape*. It cannot express which classification a given construct gets,
what a hash covers, or which of two text fields is normative. So the schema's **descriptions**
must carry the definitions a consumer cannot otherwise reproduce:

- the **exact identity preimage**, character for character (see [[derived-identity-keys]]);
- what each hash covers, and over which bytes;
- which fields are **derived and non-normative** (and which one the offsets anchor to);
- any deliberate exception to `additionalProperties: false`, **and why** (a map whose keys are
  data cannot be listed in advance) — and no second exception;
- the standing operational rules (*whoever rewrites the rows rewrites the manifest*).

This unexpressible half — schemas **plus** a construct-mapping guide — is exactly what a
generated converter would need, which is why it is the seed of the converter-generator idea in
the backlog (G6).

## Ship a compatibility note with every reconciliation

5–10 lines, written to be pasted into the consumer's own repo: which field names match their
draft, which differ, **and why**. Their mirror update is written *from* it. Say plainly what you
deliberately did **not** build and which other profile to use instead.

**Companion:** [[byte-stable-artifact]] · [[derived-identity-keys]] ·
[[boundary-vocabulary-mapping]] · [[refusal-scope-discipline]].
