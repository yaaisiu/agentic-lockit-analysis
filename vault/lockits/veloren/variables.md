---
type: lockit-variables
lockit: veloren
updated: 2026-07-06
---

# Veloren — placeholder / variable inventory (Fluent `.ftl`)

Everything between `{ … }` is a Fluent **placeable**; the surrounding text is translatable,
the placeable is **not** (preserve verbatim). Counts from `data/veloren/en/` (session 002).
No angle-bracket markup family present (see [[markup-families]] → negative). Detection regexes
are dependency-free; the spec-grade parser is a `/toolkit` job.

## 1. External variables `{ $name }`
- **Syntax:** `{ $name }` — a runtime argument the engine substitutes.
- **Meaning / where:** 448 refs (329 on message values + **119 on attribute values** — scan
  both), 115 unique names. Top: `$SP`, `$victim`, `$boost`, `$name`, `$key`, `$duration`,
  `$attacker`, `$site`. Some inject another message's value, e.g. `{ $gameinput-togglelantern }`.
- **Charset (outlier-checked):** lowercase_snake (majority) **+ UPPER** (`$SP`, 37) **+
  hyphenated** (`$shader-backend`, `$gameinput-*`, 14). Regex must allow all three.
- **Detection:** `\{\s*\$([A-Za-z][A-Za-z0-9_-]*)\s*\}`
- **Translatable?** No. New placeholder class for the library (partial precursor: Wesnoth `{brace}`).

## 2. Selectors (inline plurals / conditionals) `{ $x -> … }`
- **Syntax:** `{ $x -> [key] variant  *[other] variant }`; `*` marks the default variant.
- **Meaning / where:** 26 total. Variant keys = **CLDR categories** (`one`,`other`) **+ explicit
  numbers** (`[0]`,`[1]`). Concentrated in `buff.ftl .stat` (8) + bag/chat/trade/misc/dialogue.
  Example `buff.ftl:4`: `.stat = { $duration -> [1] …second. *[other] …seconds. }`.
- **Detection:** presence of `->` inside a placeable; variant keys `\*?\[\s*([A-Za-z0-9_ .-]+?)\s*\]`.
- **Translatable?** The variant *text* yes; keep the whole selector **intact as one value**
  (don't split into rows). Cross-locale QA: target language must supply the right plural
  categories/arity ([[cross-locale-invariants]], [[list-grammar-cldr]]).
- **A selector is NOT a token — never mask it as one** (s008). It is syntax wrapped *around*
  translatable prose, so anything that treats the construct as a single opaque span deletes
  that prose. When a span will be used as a mask, flatten: head `{ $x ->` · each variant key
  `[1]` / `*[other]` · closer `}` are the tokens; the variant bodies are text. In this corpus
  the 26 constructs are **105 syntax tokens**, and **65 `{ $var }`** sit *inside* variant bodies
  — invisible until flattening. Tool: `ftl_parse.placeable_tokens()` (vs `placeables()`, which
  stays one-span-per-construct for counting/validation).
  See [[library/heuristics/mask-the-syntax-not-the-construct]].

## 3. Functions `{ FUNC(...) }`
- **Syntax:** `{ TAIL($body) }`. Fluent built-ins are `NUMBER()`/`DATETIME()` (unused here).
- **Meaning / where:** `TAIL()` only, **1 real call** (`dialogue.ftl:46`) — **Veloren-custom**,
  strips a noun's leading article. Lockit-specific, not portable to the library as-is.
  *(Corrected s007: this said "2×". The second was never a call — `noun.ftl:1` and
  `dialogue.ftl:45` are `#` COMMENTS documenting the function, and a comment is not a
  placeable. Verified by grep + the parser: exactly one `{ TAIL($body) }` in the corpus.
  Nothing vanished when `placeables()` changed — see [[toolkit]].)*
- **Detection:** `\{\s*([A-Z][A-Z0-9_]+)\s*\(`
- **Translatable?** No (function + its args are code); the surrounding text is.

## 4. Message / term references `{ -term }` / `{ msg }`
- **Syntax:** `{ -term }` (term), `{ message }` / `{ message.attr }` (message ref).
- **Meaning / where:** 13 refs, dominated by the 2 terms `-server`/`-client` (`hud/misc.ftl:79`).
  Terms are shared reusable snippets, translatable, included into messages.
- **Detection:** `\{\s*(-?[a-z][A-Za-z0-9_-]*(?:\.[a-z][A-Za-z0-9_-]*)?)\s*\}`
- **Translatable?** The term/message definition yes; the reference token no.

## 5. String literals `{ "…" }`
- **Syntax:** `{ "…" }` — a literal, used to force a value Fluent otherwise can't express.
- **Meaning / where:** 773; **771 are `{""}`** (intentional blank, mostly `.desc` of internal
  modular fragments in `item/items/internal.ftl`) + one `{"
"}` literal newline.
- **Detection:** `\{\s*"([^"]*)"\s*\}`  ·  empties: `\{\s*""\s*\}`
- **Translatable?** No. **Track and report** (total vs translatable counts), **exclude** from
  the translatable inventory.

## Labeling & origin (Marcin's rule — single source of truth: `scripts/veloren/labels.py`)
Every construct the toolkit recognises is labeled with an **origin** so we know what is
reusable vs Veloren-specific, and so **drift is caught**:
- **`fluent`** — defined by the Fluent spec (portable to any `.ftl`): all placeable kinds
  (var, selector, term-ref, msg-ref, literal), built-in functions `NUMBER`/`DATETIME`,
  CLDR/integer selector variant keys.
- **`project`** — a Veloren convention on top of Fluent (stays in this toolkit): the four
  attribute roles (metadata/variant/gender/enum) and the custom function `TAIL()`.
- **`unknown`** — not in the registry → **surfaced** by `labels.py --audit <dir>` and by the
  test suite, never silently bucketed. This is how a new attribute role, function, or variant
  key gets noticed the moment the lockit changes. (The `enum` role itself was found this way.)
`fluent`-origin knowledge is a candidate to promote to `library/`; `project`-origin is not.

## Literal special characters
- `{` `}` are the only Fluent-special chars → a literal brace is `{"{"}`. `<` `>` `&` `%` are
  **ordinary text** (no XML / printf / c-format meaning) — Veloren uses `<…>` as literal
  decoration (`hud/trade.ftl:32`) / metasyntax (`main.ftl:116 input:<item name>`), not markup.
