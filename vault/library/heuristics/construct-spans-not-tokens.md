---
type: heuristic
id: construct-spans-not-tokens
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "008"
proposed_session: "007"
---

# Heuristic: return SPANS, not just token text — and know when a span is a mask

**Rule:** when a reader extracts an in-string construct (a placeholder, a tag, a variable), have
it return **`(start, end, text)`** against the string it came from, not the text alone. Offsets
are cheap to keep and impossible to recover later.

## Why

- **Re-anchoring.** Any consumer that stores an annotation, a highlight, or a QA finding stores
  it as an offset. If the reader threw the offsets away, nothing can be re-anchored — and the
  loss is not obvious until someone needs it.
- **The stripped value is not the source slice.** Veloren's `placeables()` returned
  `text[i+1:j-1].strip()`. That made the returned value differ from the real slice on
  **495 of 1267** placeables (every `{ $x }` with inner spacing). Both facts — no offsets, and
  a value that doesn't match the source — came from the same one-line convenience.
- **It costs nothing to keep both.** Return the span *and* the stripped inner text; downstream
  classifiers keep working unchanged, and `text[start:end]` is always the exact slice.
- **It makes an integrity check possible.** With both, the exporter can assert
  `source_text[start:end] == token` at build time — the assertion that fires if the offsets and
  the text ever come from different strings.

## The second half: a span used as a MASK must never contain translatable text

A span is *descriptive* when it says "a placeholder is here". It becomes **normative** the moment
a consumer subtracts it — "everything outside the spans is the prose to translate/annotate". Then
a span that is too wide **hides real words**, and nothing complains.

- **State the rule in its operational form.** Not "a span must not contain translatable text"
  (a prohibition you have to remember) but **"the complement of the spans is exactly the
  translatable text"** (a subtraction you can *run*). Veloren implements `complement()` and
  `complement_syntax()` and checks every row before writing.
- **Flatten composite constructs.** A Fluent selector as one span masks its variant bodies —
  real prose, sometimes mid-sentence. Emit the head, each variant key, and the closer as
  separate spans and leave the bodies exposed.
- **Refuse rather than emit a suspect mask.** If the flattener hits its fallback and returns a
  whole construct as one token, that is a refusal ([[refusal-scope-discipline]]: the output field
  really would be wrong).
- **Never invent a span that ends nowhere.** An unterminated `{` used to be emitted as
  `text[i+1:n-1]` — as a *span* that becomes a mask swallowing the rest of the string. Don't
  emit it; the structural validator is the channel a human hears about it.

## When plain tokens are the right answer

Not every contract wants spans. Wesnoth's bilingual bundle emits placeholders as **plain string
tokens**, because that consumer scores translation pairs and its schema is closed. Spans are
strictly more informative, but "more informative" is not the same as "what this contract
accepts" — see [[producer-contract-ownership]]. **Decide per contract, and say in the
compatibility note which one you emitted and why.** What is *not* negotiable is that the
**reader** keeps the offsets; whether the **exporter** ships them is the contract's call.

## Changing a foundation reader safely
This rule usually arrives as a change to the one reader every script imports. Change it **in
place** — a sibling function is exactly the drift the library templates exist to prevent — and
**prove** the migration: capture a baseline of every downstream tool's output before the edit and
diff for byte-identity after. Watch for call sites where a missed unpack fails *silently*
(Veloren's `labels.py` used the result as a `Counter` key; a tuple is hashable, so it would have
printed `(12, 20, '$x')` instead of raising). Pin those with a test. See [[verify-count-changes]].

**Companion:** [[construct-origin-labeling]] · [[byte-stable-artifact]] · [[fluent-ftl]].
