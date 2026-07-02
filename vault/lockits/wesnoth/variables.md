---
type: lockit-variables
lockit: wesnoth
updated: 2026-07-02
---

# Wesnoth — variables, markup & control codes

_Inventory of in-string token conventions, with detection regex + translatability.
Examples are **synthetic** (no lockit content); real occurrences are pointed to by
`file:line` into gitignored `data/wesnoth/`. Standard-vs-Wesnoth split matters for reuse —
see the proposed [[gettext-po]] library note._

Legend: **T?** = translatable · **preserve** = copy verbatim, may reorder.

## 1. `$variable` substitution (Wesnoth) — **preserve**
Runtime substitution of WML variables.
- Forms: `$name`, dotted `$unit.name`, arrays `$houses[0].title`. Names may contain
  letters, digits, `_`, `.`, `[` `]`, `?`.
- **Terminators:** a **space** ends the name *and is shown*; a **`|`** ends the name and
  is *not* shown. Use `$var|` before punctuation/adjacent text.
- Synthetic examples: `$unit.name| has $gold gold.` · `Welcome $village|!`
- Detection (start point): `\$\|?[A-Za-z_][\w.\[\]?]*\|?`
- Counts (subset): core 276, lib 90, httt 18, units 0.
- **T?** no — preserve tokens verbatim.
- TRACKED (T1): dotted `$obj.attr` roots overlap WML `[tag]` names and `.name` overlaps a
  WML id — possible reference into the WML entity graph; confirm with more domains.

## 2. Caret context `context^string` (Wesnoth) — prefix **not shown**
The engine strips everything up to and including the **first `^`** before display; only
the post-`^` text is shown. Translators translate the post-`^` payload and must **not**
keep the prefix (a forgotten caret is displayed to the player).
- Used **instead of** the standard `msgctxt`. Gender is the same idiom.
- Synthetic examples: `female^<adjective>` → shows "<adjective>"; `menu section^Save`.
- Detection: leading `PREFIX^` where PREFIX is a short context token: `^([^\^]{1,40}?)\^`.
- 105 distinct prefixes / 350 entries (subset) — full list in [[context-prefixes]].
- **T?** payload after `^` only; the prefix is metadata (drop in translation).

## 3. Pango text markup (Wesnoth) — tags **preserve**, `text='…'` **translatable**
- Recommended HTML-style: `<b> <i> <u> <span …>` (attrs `color`, `size`, `weight`, …).
- Legacy (pre-1.19) attribute form: `<italic>text='…'>…</italic>`, `<format …>`.
- Only the `text='…'` **value** (and surrounding prose) is translatable; tag names and
  attribute names/values are preserved.
- Detection: tags `</?[A-Za-z][\w]*(?:\s[^>]*)?/?>` · attr `text='[^']*'`.
- Counts (subset): `<i>` 216, `<b>` 80, `<span>` 78, `<italic>` 50; `text='…'` on 23.
- QA (per Marcin C5.1): a validator should check tags are **balanced/well-formed** →
  planned `validate_markup.py`.

## 4. Help / command markup (Wesnoth) — **preserve** (TRACKED)
- `<ref dst='…' text='…'>` (translate only `text=`, keep `dst=`), `<command>`.
- Command-usage metasyntax in `:command` help: `<side>`, `<var>=<value>`, `<unit type id>`
  — preserve the tokens; translate only surrounding prose. No cited Wesnoth rule → T2/T3.
- Also seen: literal `<unknown>` shown to the user (angle brackets are real text).

## 5. XML/Pango character entities — **preserve escaped**
`&quot; &lt; &gt; &amp; &apos;` (and `&#NNN;`). Required because markup strings must
escape `" < > &`. (This was the Q3 `&` case.)
- Detection: `&(?:quot|lt|gt|amp|apos|#\d+);`

## 6. Escapes / control codes — **preserve**
- `\n` line break (subset: 543), `\t` tab (104, in code-like example strings),
  `\"` escaped quote (34), `\\` literal backslash (3).
- Detection: `\\[nt"\\]`.
- QA (per Marcin C5.3): flag any **lone `\`** not part of a known escape.

## 7. printf / date formats (standard) — **preserve**
- printf `%d`/`%s` (rare: core 4, lib 2) and strftime date patterns (`%B %d %Y, %I:%M %p`).
- Detection: `%[-#0-9.]*\d*\$?[sdfeEgGxX%]` · date `%[A-Za-z]`.
- `#, c-format` flag (standard) marks entries whose `%` tokens tools should validate.

## 8. Plurals (standard gettext) — **structure**
`msgid` + `msgid_plural`; translations fill `msgstr[0..N-1]`. The selection rule lives in
each `.po` header `Plural-Forms: nplurals=N; plural=EXPR;` (English 2 forms, Polish 3).
The `.pot` only marks which strings are pluralizable. See [[gettext-po]].

## 9. Localization-craft patterns (confirmed at GATE 2)
- **SI number-unit prefixes** — `^`-prefixes `prefix_kilo…yotta`, `prefix_milli…yocto`,
  `infix_binary` carry one-character magnitude symbols (`k M G T … m µ n …`, binary `i`).
  Preserve verbatim; a few (`µ`, the binary infix) may be localized in some locales.
- **List grammar (CLDR)** — `conjunct`/`disjunct` × `pair/start/mid/end` build "A, B, and C"
  / "A, B or C" from join templates with `$first/$second/$prefix/$next/$last`. Rebuild per
  target language (Oxford comma, conjunction word, order) — never translate literally. See
  library candidate [[list-grammar-cldr]].
- **Value-level cross-domain dependency (T1)** — dotted vars like `$unit.language_name`
  expand to a **localized noun from another textdomain** (`wesnoth-units`) inserted
  mid-sentence → gender/case agreement hazard the translator can't see at the string. Dotted
  `$obj.attr` are runtime WML object properties (`unit.name/.side/.language_name`), not
  references to other lockit ids.
