---
type: convention
id: inline-context-prefix
status: accepted
first_seen: wesnoth
also_seen: []
promoted_session: "000"
---

# Inline context prefix (context baked into the source string)

**Pattern.** Instead of the standard gettext `msgctxt` field, some projects put the
disambiguation *context inside the source string*, separated by a delimiter, and strip it
before display. Wesnoth uses a **caret**: `"<context>^<displayed text>"` — the engine
removes everything up to and including the first `^`, so only the post-delimiter text is
shown. Other delimiters exist in the wild (`|`, `\x04` for GNU `pgettext`'s `EOT`).

**Why it matters.**
- The prefix is **metadata, not content** — translators translate only the payload and
  must **not** reproduce the prefix (a forgotten delimiter is shown to the user).
- It doubles as a **subtype/grouping axis** (e.g. `female^`, `menu section^`, `prefix_kilo^`).
- **Gender** is often encoded this way (`female^…`, base = default).

**Detection.** A short identifier-ish token before a delimiter at the start of many msgids,
with `msgctxt` unused. Heuristic regex (caret): `^([^\^]{1,40}?)\^`.

**Do (tooling).** Split into `context_prefix` + `display` for reporting/subtyping, but keep
the **whole msgid** as the identity key (the prefix is part of the unique string). Maintain
an evidenced prefix registry (it grows across files). Never treat the prefix as translatable.

**first_seen:** wesnoth (caret `^`; 105 distinct prefixes in the 4-domain subset). Related:
[[gettext-po]] (`msgctxt` is the standard alternative), [[list-grammar-cldr]].
