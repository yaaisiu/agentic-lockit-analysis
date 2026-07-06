---
type: system-doc
id: glossary
status: active
updated: 2026-07-06
---

# Glossary (client-free)

Generalised terms. **No lockit content here** — definitions only.

- **Lockit** — the tabular localisation file a localisation vendor receives from a game
  studio: source strings + metadata (keys, char limits, context, locale columns).
- **Chart** — the documented structure of a lockit (`profile.md` and friends). The
  human-readable map produced at GATE 1.
- **Toolkit** — the tested deterministic scripts + packaged skill for one lockit.
- **Placeholder / variable** — a token the engine substitutes at runtime
  (`{name}`, `%s`, `{0}`). Preserve verbatim; do not translate.
- **Control code** — a non-text token controlling rendering (`[PC]`, `<br>`, colour
  tags, `\n`). Non-translatable.
- **Key / string ID** — the stable identifier for a string; often carries convention
  (namespace prefix, gender/number markers, hierarchy).
- **Library** — cross-lockit, generalised knowledge (conventions, heuristics,
  script-templates) that makes the *next* file faster. Recognise before re-inferring.
- **Markup family** — a distinct in-string markup syntax. One lockit can carry several,
  separated by sub-file/string-type: **Pango** (`<b>…</b>`), **DocBook** (`<emphasis>…`),
  **po4a/POD man** (`B<…>`, `E<lt>`). Detect + balance-check per family. See
  [[markup-families]].
- **Metasyntax** — a `<slot>`-style token that looks like markup but is an argument
  placeholder (CLI help: `<file>`, `<side>`). Single token, never balanced; preserve verbatim.
- **Cross-locale invariant** — structure that must survive translation (placeholder names,
  printf specifiers, markup balance, plural arity). Checkable source-vs-translation. See
  [[cross-locale-invariants]].
- **nplurals** — the number of plural forms a language uses (from a `.po` `Plural-Forms`
  header); e.g. English/German 2, Polish 3. A translation must supply exactly this many.
