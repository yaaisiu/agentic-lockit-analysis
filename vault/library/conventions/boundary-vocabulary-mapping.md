---
type: convention
id: boundary-vocabulary-mapping
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "008"
---

# Convention: map vocabularies at the boundary — never rename the registry to chase a consumer

Our toolkit names things for its own reasons: the names come from the format, from the profile,
and from what a human called them at GATE 1. A consumer names things for *its* reasons. The two
vocabularies will not match, and the pressure — every time — is to rename ours so the export can
pass the value straight through.

**Don't.** Map at the boundary instead: keep the registry as the single source of truth, and
translate to the consumer's enum **inside the exporter**, in one visible place.

> Two independent instances, and it is the single most transferable rule between them.
> Veloren: `ORIGIN_MAP = {'fluent': 'spec', 'project': 'project', 'unknown': 'unknown'}` — our
> registry says `fluent` for spec-defined constructs; the contract's enum says `spec`.
> Wesnoth: `CARET_SLUG = {'gender/agreement': 'gender_agreement', 'SI number units': 'si_units',
> …}` — the `^`-prefix registry returns human labels; the contract needs slugs.

## Why

- **The registry serves every tool, not just the exporter.** Renaming `gender/agreement` to
  `gender_agreement` to please one consumer degrades the label in the inventory report, the
  vault note, and the GATE-1 dossier — where a human reads it.
- **The next consumer will want a third spelling.** Renaming does not scale; a second map does.
  Chasing consumers through the registry means the registry ends up owned by whoever asked last.
- **A rename is invisible in a diff of meaning.** A boundary map is one dict, greppable, sitting
  next to a comment explaining which side is which. Someone auditing "why does the bundle say
  `spec` when our note says `fluent`?" finds the answer in one line.
- **It keeps the ownership split honest.** We own the profile; they own their contract
  ([[producer-contract-ownership]]). A boundary map is that split expressed in code.

## The rules

1. One `dict` per vocabulary, at module level in the exporter, with a comment naming both sides
   and why they differ.
2. **Map at the boundary, once** — never scatter `if fam == 'x': 'y'` through the row builder.
3. **Pass drift signals through UNCHANGED.** `unknown` must survive the map. It is the value
   telling the consumer not to trust the classification and to escalate to a reviewer; a map
   that helpfully collapses it to a plausible neighbour destroys the only signal that a lockit
   changed. Default an unmapped input to `unknown`, never to the nearest known value.
4. **Assert the mapped value is in the contract's enum before writing** (a module-level
   `frozenset`, checked in `verify_rows`). If our registry grows a value the contract has no
   home for, the export must **fail**, not quietly emit something out of contract. That failure
   is the prompt to talk to the consumer.
5. **Do not invent a value to fill a gap.** If a domain, construct, or class does not resolve,
   emit the explicit unknown and report the count. (Wesnoth `string_class` returns `unknown` for
   any textdomain the profile has not classified — 0 today, and it is the drift detector for
   domain 33.)

**Companion:** [[construct-origin-labeling]] (the registry this maps *from*) ·
[[producer-contract-ownership]] · [[byte-stable-artifact]].
