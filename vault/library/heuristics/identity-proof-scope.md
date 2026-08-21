---
type: heuristic
id: identity-proof-scope
status: accepted
first_seen: wesnoth
also_seen: []
promoted_session: "008"
---

# Heuristic: a proof of identity is a proof about ONE function

**Rule:** a uniqueness / collision result covers exactly one function over one preimage. Whenever
you write such a number down, **name the function and the preimage in the same sentence**. When a
second id of the same shape appears, **measure it separately** and state plainly that the earlier
result does not transfer.

## What happened

Four Wesnoth vault notes recorded *"26,312 / 26,312 unique, 0 collisions"*. Read at speed, that
is a fact about the corpus. It is not: it is a fact about `po_parse.internal_id` — 10 hex over
`domain ⋮ msgctxt ⋮ msgid ⋮ plural`.

s008 minted a second id for bundle export — `segment_id`, 12 hex over `msgctxt|msgid_raw` — a
different function over a different preimage. Its collision count was **unproven** until measured
(it is also 0 over the same 26,312 rows — a *second* result, not the same one). Reading the
existing proof as covering the new id would have been the cheapest possible route to skipping the
identity vectors and shipping a bundle that validates, looks correct, and joins to nothing.

## Why it is a *documentation* hazard specifically

The note was never false. Nobody has to be careless for this to bite: the sentence is accurate,
confident, and load-bearing, and the only thing wrong with it is what it **omits**. Good news
stated without its scope reads as coverage it does not have, and there is nothing in the note to
flag the gap. The same sentence with four extra characters — the function's name — is safe.

This is the same discipline as [[verify-count-changes]] (confirm the cause when a count moves),
applied to **proofs** rather than to counts: don't inherit a result, re-establish it.

## How to apply

1. Write results as *"`<function>` — N/N unique, 0 collisions, over `<preimage>`"*. Never
   "ids are unique".
2. Introducing a second id of the same shape? Measure it over the whole corpus, in its own
   assertion, and add a line to the older note saying the two are different functions.
3. **Assert uniqueness in the pre-write self-check**, not only in a report — a report is read
   once; the check runs every time.
4. Correct an inherited over-broad claim **in place with a dated in-note annotation**; add a
   dated forward-pointer to historical session logs rather than rewriting them (history is
   preserved, not revised).
5. Generalise: the same trap applies to any scoped proof — "0 false positives" (on which corpus?
   which locale?), "the anatomy holds" (over which domains?), "lossless" (with respect to which
   fields?).

**Companion:** [[derived-identity-keys]] · [[verify-count-changes]] · [[outlier-hunting]].
