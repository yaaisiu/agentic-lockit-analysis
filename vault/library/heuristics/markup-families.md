---
type: heuristic
id: markup-families
status: accepted
first_seen: wesnoth
also_seen: []
promoted_session: "001"
---

# Heuristic: a lockit string may carry MORE THAN ONE markup system

**Recognise → validate per family.** Don't assume one markup syntax across a whole lockit.
A single localisation set often mixes markup systems that are **cleanly separated by
sub-file / string-type** (in Wesnoth: by textdomain). Detect the family **per string** and
apply that family's balance rule — a validator hard-wired to one syntax will raise false
errors on the others.

**Families seen in the wild (extend as new ones appear):**
- **Pango / HTML-ish** — `<b>…</b>`, `<i>`, `<span attr='…'>…</span>`; balanced open/close,
  self-closing `/>` ignored. (Game/UI text.)
- **DocBook XML** — `<emphasis>…</emphasis>`, `<link>`, `<guimenuitem>`, empty
  `<imagedata …/>`; same open/close balance model as Pango, just a different tag set. (Manuals.)
- **POD / po4a man markup** — `B<bold>`, `I<italic>`, `E<lt>`/`E<gt>` for literal `< > &`;
  an uppercase letter immediately before `<` opens a span that closes at the matching `>`.
  (Man pages.) Balance rule: `#[A-Z]< == #'>'`, no bare `<`.
- **Bare CLI metasyntax** — single `<slot>` tokens (`<file>`, `<side>`): argument
  placeholders, NOT markup — never balance-check them (they never close).

**Discriminators (cheap, per string):**
- POD/po4a iff a `[A-Z]<` opener is present AND there is **no** real close tag `</name>`
  (a path like `B</var/run/socket>` is content, not a close tag).
- Otherwise treat as balanced-tag (Pango ∪ DocBook): walk `<…>`, push opens, pop closes,
  skip self-closing and known-empty elements.
- A `<word>` that is neither a known tag nor part of a POD span is **metasyntax** — count
  it, don't balance it.

**Beware name collisions:** a DocBook tag name (`command`, `option`, `filename`, `parameter`)
can also be a bare CLI metasyntax slot in another sub-file. When pre-seeding a known-tag set,
**exclude names that appear as bare `<slot>` tokens** or you'll get false "unclosed" errors.

**Severity:** structural breakage (unbalanced/unclosed, bad POD, bare `<`, stray `\`) = hard
error; an unescaped `&` inside a markup string is often engine-tolerated (used as "and") →
prefer **WARN** unless the target engine is known strict.

**Then reach for** the per-family check in a `validate_markup`-style script; keep the family
detector and tag sets in one shared token module so a fix propagates.
