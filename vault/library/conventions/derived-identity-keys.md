---
type: convention
id: derived-identity-keys
status: accepted
first_seen: wesnoth
also_seen: [veloren]
promoted_session: "008"
---

# Convention: derived identity keys (the id a consumer joins on)

A toolkit mints an id so *its own* scripts can refer to a record. An export mints an id so
*someone else's* system can join to it, forever. These look identical and are not the same
object, and conflating them is the most expensive mistake in this whole area — because it
**fails silently**: the bundle validates, the ids look right, and nothing matches downstream.

## The rules

1. **An id is a pure function of a named tuple of SOURCE fields — never of a locator.**
   Not the line number (entries move when strings are added), not the file (a message keeps its
   identity when it moves between files), not the sequence number, and not the *display* form of
   the text. State the tuple in the schema and hold to it.
2. **The export's id and the toolkit's internal id are DIFFERENT FUNCTIONS. Say so, loudly.**
   Wesnoth's reader mints `internal_id` = `<domain>:sha1(domain ⋮ msgctxt ⋮ msgid ⋮ plural)[:10]`;
   the bundle emits `segment_id` = `<domain>:sha1(msgctxt|msgid_raw)[:12]`. **Same shape,
   different value.** An export that reuses the internal one validates, looks correct, and
   produces a bundle nothing downstream can join. Assert the emitted shape in code
   (`^[^:]+:[0-9a-f]{12}$`) so the wrong id cannot ship.
3. **Publish the preimage character-for-character, in the schema description.** Separator,
   encoding, hash, truncation length, case. A consumer that cannot reproduce your id exactly
   cannot verify anything you send. "sha1 of the key" is not a specification.
4. **Pin vectors computed OUTSIDE the repo.** A handful of `(inputs → expected id)` rows in the
   tests. A test that recomputes the id with the same function it is testing proves nothing;
   external vectors are what catch a "harmless" refactor of the preimage.
5. **Test the id against everything it must NOT depend on.** Shift every entry's line number,
   add a plural, move the entry between files — and assert no id moves. This is a different
   test from uniqueness and catches a different bug.
6. **Measure collisions for THIS function, over the whole corpus, every time.** See
   [[identity-proof-scope]] — a proof about one id is not a proof about another. Assert
   uniqueness in the pre-write self-check, not merely in a report.
7. **State the injectivity precondition of your separator, especially when it holds by luck.**
   Wesnoth's preimage joins `msgctxt` and `msgid` with a literal `|` — and `|` occurs *inside*
   Wesnoth source text as the documented `$var|` terminator. It is injective **only because
   `msgctxt` is empty on every Wesnoth entry**, so nothing can straddle the separator. That is a
   property of this corpus, not of the construction. Recorded in the schema as a hazard for the
   next lockit that actually uses `msgctxt`. **Prefer a separator that cannot occur in the
   text** (the reader uses `0x1f` for exactly this reason); when you cannot, write down why it
   is safe *here*.
8. **Recompute the id from the row's own fields in the self-check.** One line, and it catches a
   builder that hashed the display form, the context prefix, or the plural.
9. **Never hash the artifact's own name into the id.** Renaming a bundle must not orphan stored
   annotations. (A consumer's fixture generator got this wrong, contradicting its own schema;
   reported, not fixed — see [[producer-contract-ownership]].)

## Why the truncation length is a decision, not a default
12 hex = 48 bits. Over ~26k entries the birthday probability is negligible, but "negligible" is
an argument, not a measurement — so measure. And keep the length **stable**: changing it later
is a new id function, which means a new contract version, not a patch.

**Companion:** [[byte-stable-artifact]] · [[producer-contract-ownership]] ·
[[identity-proof-scope]] · [[gettext-po]] (the natural gettext key this derives from).
