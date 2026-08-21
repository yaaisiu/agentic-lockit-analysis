---
type: system-doc
id: glossary
status: active
updated: 2026-08-21
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
- **Bundle** — a normalized artifact this system *produces* for a downstream consumer that never
  opens a raw lockit: a manifest plus one row per translatable unit. See [[byte-stable-artifact]].
- **Report vs artifact** — a **report** is read once by a human and discarded; an **artifact** is
  stored and joined against later by another system. A report describes; an artifact **promises**
  the same input yields the same bytes forever. Different disciplines, not different polish.
- **Normative field** — the field of an artifact a consumer anchors to (ids computed over it,
  offsets stored into it). Everything **derived** from it — an unescaped display form, a
  convenience duplicate — is **non-normative** and must be labelled so in the schema.
- **Join key / segment id** — the id a *consumer* joins on. A pure function of a named tuple of
  source fields, never of a locator, and **not** the same function as the toolkit's own internal
  id even when it is the same shape. See [[derived-identity-keys]].
- **Structural error vs content finding** — a **structural** error makes the rows untrustworthy
  (refuse to emit); a **content finding** is well-formed data that says something wrong, usually
  an upstream defect (never refuse — emit a per-row verdict). See [[refusal-scope-discipline]].
- **Boundary map** — the one dict in an exporter that translates *our* vocabulary into a
  consumer's enum, so the registry is never renamed to chase a consumer.
  See [[boundary-vocabulary-mapping]].
- **Span vs token** — a **token** is the construct's text; a **span** is `(start, end, text)`
  against the string it came from. A span used as a *mask* must never contain translatable text.
  See [[construct-spans-not-tokens]].
