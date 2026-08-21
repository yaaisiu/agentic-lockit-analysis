---
type: convention
id: fluent-ftl
status: accepted
first_seen: veloren
also_seen: []
promoted_session: "002"
---

# Project Fluent (`.ftl`) — standard conventions (reusable for ANY Fluent lockit)

Client-free reference distilled at session 002 (source: Project Fluent spec). **Recognise
these before re-inferring** on any `.ftl` lockit; only the *project-specific* semantics (which
attribute names mean what, custom functions) need fresh inference. The gettext counterpart is
[[gettext-po]]; reader template [[ftl_parse_template]]; labeling [[construct-origin-labeling]].

## Files & identity
- One file (or a tree) per **locale**; a locale's files load into ONE **bundle** = a single
  flat **namespace**. So a **message id is globally unique** within a locale → identity = the
  message id alone (no domain/context tuple like gettext). Verify with a cross-file collision
  check (0 collisions ⇒ id is a lossless key).
- Encoding: **UTF-8, no BOM** (the spec mandates no-BOM; flag a BOM as an error).

## Entry kinds
- **Message** `ident = value` (ident `[A-Za-z][A-Za-z0-9_-]*`).
- **Term** `-ident = value` — a shared, reusable snippet referenced via `{ -ident }`; not shown
  standalone but is translatable.
- **Attribute** `.name = value` (indented, under a message/term) — a named sub-string. Fluent
  defines the MECHANISM only; the *meaning* of an attribute name (description, gender form,
  variant list, enum key…) is a PROJECT convention → infer + label per lockit
  ([[construct-origin-labeling]]).
- **Comment** `#` / `##` / `###` = standalone / group / resource.
- **Junk** = anything that doesn't parse — a reader should REPORT it, not crash (0 junk on a
  clean source is a good parser-correctness signal).

## Values
- May be **inline** (after `=`) or **block/multiline** (indented continuation). A block value
  may contain **internal blank lines** (kept), and in the wild the continuation is sometimes
  flush at **column 0** — so an entry-boundary rule keyed only on indentation is wrong: end an
  entry at the next column-0 definition or comment, absorbing everything else ([[ftl_parse_template]]).
- A truly-empty value is illegal; the idiom is `{""}` → treat as an intentional blank: **track
  but exclude** from translatable counts (a naive count over-counts by the number of blanks).

## Placeables `{ … }` (everything between braces; preserve verbatim)
- **Variable** `{ $name }` — runtime arg (non-translatable). Names can include `-` and UPPER →
  detection `\{\s*\$([A-Za-z][A-Za-z0-9_-]*)\s*\}`.
- **Selector** `{ $x -> [key] … *[key] … }` — inline plural/conditional. Keys = **CLDR
  categories** {zero,one,two,few,many,other} and/or **explicit integers**; **exactly one**
  default, marked `*`. Plurals are INLINE (contrast gettext `msgstr[]` rows); arity is chosen
  per target language. Keep the whole selector intact as one value.
- **Function** `{ FUNC(...) }` — built-ins are `NUMBER()` / `DATETIME()`; anything else is a
  PROJECT-registered custom function (infer + label its origin).
- **Reference** `{ -term }` / `{ message }` / `{ message.attr }`.
- **Literal** `{ "…" }` — forces a value Fluent can't otherwise express (`{""}` = blank).

## Special characters
- Only `{` and `}` are special (a literal brace = `{"{"}`). `<`, `>`, `&`, `%` are **ordinary
  text** — Fluent has NO angle-bracket markup, so [[markup-families]] returns negative unless a
  project embeds markup as content.

## Detecting a Fluent lockit
`.ftl` extension; lines `ident =` / indented `.attr =` / `{ $var }` / `{ $x -> … }`; **no**
`msgid`/`msgstr` (that's gettext, [[gettext-po]]); often a sibling `_manifest.ron` and
per-locale directories named by BCP-47 tag. If gettext-detection says *not gettext* and you see
`{ $… }` placeables + `.attr =` lines → reach for this convention (don't re-infer from scratch).

## Section markers are structural context — capture them, don't discard them
`##` (group) and `###` (file-level) comment lines are **not** prose to skip: they are the
finest-grained structural signal Fluent offers, and the only one between "the whole file" and
"one message". A reader that drops them throws away the classification hint a consumer's
pre-pass wants — for one corpus, **3,979 of 7,131 units** carry a section versus **11** carrying
an entry-level `#` comment, and the files are coarse (48 files over 7,131 units).

**Join consecutive marker lines into one section.** Authors write multi-line blocks; keeping only
the last line made an incidental closing aside the corpus's most common "section", on 564
entries — a real signal turned into a fragment. (Synthetic illustration: `## Combat abilities` /
`## Listed in the order the UI shows them.` is ONE section, not a section named after the second
line.)

## Tooling guidance
- Reader: [[ftl_parse_template]] (dependency-free) — note its `placeables()` returns
  **`(start, end, inner)` spans**, not bare text ([[construct-spans-not-tokens]]). Cross-locale:
  [[cross-locale-invariants]] (Fluent instance = `$var` set + selector presence +
  gender-attribute coverage).
- Label each construct fluent-native vs project-native, with an unknown bucket for drift:
  [[construct-origin-labeling]].
