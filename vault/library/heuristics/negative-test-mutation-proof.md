---
type: heuristic
id: negative-test-mutation-proof
status: accepted
first_seen: wesnoth
promoted_session: "009"
---

# Heuristic: a guard test proves nothing until it has been shown to FAIL

A test that asserts *"a bad input is rejected"* is only evidence if it would **stop passing**
when the rejection goes away. Otherwise it is a test that has never been observed doing anything
— it may be asserting on a message that is produced for an unrelated reason, on a code path the
guard does not sit in, or on nothing at all.

**Rule:** after writing a negative test, **remove or loosen the guard it protects**, watch the
test fail, then put the guard back. Do the mutation in memory if you can, so nothing is edited
on disk. Record the observation next to the test.

## The instance

s009 pinned a manifest's contract version with `"const": "1.0.0"` and wrote the test that a
`2.0.0` manifest fails validation. The suite went green — which by itself demonstrates nothing,
because a wrong version could also have been caught by an unrelated `required`-keys check.

The mutation: loosen `const` → `"type": "string"` **in memory** and re-validate the same
`2.0.0` manifest. Result: **zero problems** — it validates cleanly. With the pin:
`manifest.bundle_version: const '1.0.0' != '2.0.0'`. The test fails exactly when the pin is
removed, so the test is measuring the pin and nothing else. *That* is what made it worth
committing, and it is the sentence that belongs in the session note.

## Why this is worth a ritual, not just good intentions

A guard and its test are usually written in the same ten minutes by the same person holding the
same assumption. Nothing in "write the check, write the test, both pass" ever tests the *link*
between them. The mutation is the only cheap step that does — and it is cheap: one edit, one
re-run, one revert, usually under a minute.

It generalises past schemas. The same move applies to a **refusal** (delete the condition — does
the fixture still refuse?), a **verifier** (return `[]` unconditionally — do the self-check
tests still pass?), and an **identity pin** (change one character of the preimage — do the
vectors move?). Any of those passing after the mutation is a test asserting something other
than what its name claims.

## How to apply

1. Write the guard and its negative test.
2. Mutate the guard — loosen, delete, or short-circuit it — **in memory**, never as a committed
   edit.
3. Re-run the negative test. **It must fail.** If it still passes, the test is not measuring the
   guard: find what it *is* measuring before trusting it.
4. Restore, re-run, confirm green.
5. Put the observation in the session note in one sentence, so the next reader knows the pair was
   verified rather than merely written.
6. Keep the negative test **adjacent to the positive one**. Someone reading the suite in six
   months should see the pair together and understand instantly what the guard buys.

**Companion:** [[refusal-scope-discipline]] (scope the guard first) ·
[[pinned-version-discriminator]] (the instance) · [[identity-proof-scope]] · [[byte-stable-artifact]].
