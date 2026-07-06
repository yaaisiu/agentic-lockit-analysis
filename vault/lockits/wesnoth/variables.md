---
type: lockit-variables
lockit: wesnoth
updated: 2026-07-02
---

# Wesnoth — variables, markup & control codes

_Inventory of in-string token conventions, with detection regex + translatability.
Examples are **synthetic** (no lockit content); real occurrences are pointed to by
`file:line` into gitignored `sources/wesnoth/`. Standard-vs-Wesnoth split matters for reuse —
see the proposed [[gettext-po]] library note. Patterns are the ones in
`scripts/wesnoth/po_tokens.py` (the single source of truth); this note is their chart._

Legend: **T?** = translatable · **preserve** = copy verbatim, may reorder.

> **Scope note (session 001):** confirmed corpus-wide across all **32 domains / 26,312
> strings** (was a 4-domain subset). The corpus revealed **three markup systems** cleanly
> separated by domain — see §3 — plus a `{brace}` placeholder class (§3b). Counts below are
> corpus-wide unless marked "(subset)".

## 1. `$variable` substitution (Wesnoth) — **preserve**
Runtime substitution of WML variables.
- Forms: `$name`, dotted `$unit.name`, arrays `$houses[0].title`. Names may contain
  letters, digits, `_`, `.`, `[` `]`, `?`.
- **Terminators:** a **space** ends the name *and is shown*; a **`|`** ends the name and
  is *not* shown. Use `$var|` before punctuation/adjacent text.
- Synthetic examples: `$unit.name| has $gold gold.` · `Welcome $village|!`
- Detection: `\$[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\[\d+\])?\|?` — a dotted segment counts
  only when the `.` is **followed by an identifier** (`$unit.name`), so a var at a sentence
  end (`$version.`) does **not** swallow the period.
  - **Why this matters (session 001):** the earlier `[\w.]*` form greedily ate a trailing
    `.`, which then made a translation's `$version` look like it *dropped* the source's
    `$version.` → **false** cross-locale mismatches. The refined pattern fixed 6 such
    false positives in the de/pl pilot with no loss of real dotted-attr detection.
- Counts (corpus): **686 occ / 506 entries** (subset was: core 276, lib 90, httt 18).
- **T?** no — preserve tokens verbatim.
- TRACKED (T1): dotted `$obj.attr` are runtime WML object properties (not lockit-id refs);
  but `$unit.language_name` inserts a localized noun from another domain → agreement hazard
  (see §9).
- TRACKED (T7 — rare constructs the tokenizer handles imprecisely but safely; corpus audit
  session 001): **`$(…)` WML formula/arithmetic** (8 occ, e.g. `$($student_hp-15)`) — the
  inner `$var` is captured, the `$(…)` wrapper is not a recognised token; **`$x[$i]` variable
  array index** (6 occ, e.g. `$stored_changers[$i].type`) — captured as `$stored_changers`
  + `$i` with `.type` orphaned. Neither breaks cross-locale checks (both sides tokenize the
  same). Revisit if `$(…)` needs its own class.

## 2. Caret context `context^string` (Wesnoth) — prefix **not shown**
The engine strips everything up to and including the **first `^`** before display; only
the post-`^` text is shown. Translators translate the post-`^` payload and must **not**
keep the prefix (a forgotten caret is displayed to the player).
- Used **instead of** the standard `msgctxt`. Gender is the same idiom.
- Synthetic examples: `female^<adjective>` → shows "<adjective>"; `menu section^Save`.
- Detection: leading `PREFIX^` where PREFIX is a short context token: `^([^\^]{1,40}?)\^`.
- **129 distinct prefixes / 712 entries (corpus)** — was 105/350 subset. Full evidenced
  registry (script-generated) in [[context-prefixes]]. Includes gender/plural agreement
  variants (`female_speaker`, `race+female`, `addressed_plural`, …) — translation-critical.
- **Confirmed in real translations:** the msgstr carries **only** the post-`^` payload —
  e.g. `scenario name^Blackwater Port` → de `Der Hafen von Schwarzwasser` (no prefix). So
  cross-locale checks compare the source's `display` (post-caret), never the raw msgid.
- **T?** payload after `^` only; the prefix is metadata (drop in translation).

## 3. Markup — THREE systems, cleanly separated by domain (session 001)
The corpus carries three distinct markup families. `po_tokens.markup_family(s)` classifies a
string as `po4a` or `tag` (pango+docbook share the open/close balance model);
`validate_markup.py` auto-selects the right check. Corpus split: **tag = 26,096 strings,
po4a = 216**. All tag names/attrs are **preserved**; only prose (and `text='…'` values) is
translatable.

**3a-i · Pango (game content — 29 domains) — tags preserve, `text='…'` translatable.**
- HTML-style `<b> <i> <u> <span …>` (attrs `color`, `size`, `weight`, …); legacy attribute
  form `<italic>text='…'>…</italic>`, `<format …>`. Help markup `<ref dst='…' text='…'>`.
- Detection: tags `</?[A-Za-z][\w]*(?:\s[^>]*?)?/?>` · attr `text='[^']*'`.
- Counts (corpus): `markup_tag` 4064 occ / 1383 entries; `text='…'` on 33.
- Recognised tag set (`MARKUP_FAMILIES['pango']`): b i u s tt big small sub sup span · bold
  italic underline header h format · ref img jump character.

**3a-ii · DocBook (the `wesnoth-manual` domain) — balanced XML, preserve.**
- Real DocBook inline tags: `<emphasis> <link> <ulink> <literal> <imageobject>` and the
  **empty/self-closing** `<imagedata …/>` (never paired — `po_tokens.DOCBOOK_EMPTY`).
- Balance-checked exactly like Pango (open/close). Validated clean on all 433 manual strings.

**3a-iii · po4a / POD man markup (the `wesnoth-manpages` domain) — preserve.**
- POD font/entity escapes: `B<bold>`, `I<italic>`, and `E<lt>`/`E<gt>`/`E<amp>` standing in
  for literal `< > &` (a literal `<` MUST be `E<lt>`). Openers are an uppercase letter
  immediately before `<`; each closes at the matching `>`. Counts: `B<` 285, `I<` 107,
  `E<` 32.
- Detection/validation: `po4a` family iff a `[A-Z]<` opener is present and there is **no**
  real close tag `</name>` (a path like `B</var/run/socket>` is content, not a close tag).
  Balance rule: `#[A-Z]< == #'>'`, and no bare `<`.

**QA (Marcin C5.1/C5.3):** `validate_markup.py` checks balance per family + stray `\` +
unescaped `&`-in-markup, returning **`ERROR`** (structural: unbalanced/unclosed, bad po4a,
stray `\`) vs **`WARN`** (unescaped `&` in markup — the engine tolerates a literal `&` used
as "and", so it's flagged for a human, not a hard fail — decided session 001 B1). Full corpus
→ **0 errors, 1 warning** (`& snow` in wesnoth-h2tt).

**DocBook tag set (session 001 B4):** the 7 evidenced tags plus a pre-seeded DocBook-
distinctive inline/GUI set (`phrase quote citetitle superscript subscript keycap keycombo
guimenu guimenuitem guibutton guilabel guiicon menuchoice varlistentry listitem simpara
inlinemediaobject mediaobject screenshot`) so translated manuals balance-check. **Deliberately
excluded**: DocBook names that collide with Wesnoth bare CLI slots — `command`, `option`,
`filename`, `replaceable`, `parameter`, `varname`, `prompt`, … — those appear as single bare
`<slot>` tokens (§4) and would otherwise report false "unclosed".

### 3b. `{brace}` placeholders — name-generator grammar / brace-format — **preserve**
- `{prefix}{suffix}`, `{vowel}`, `{consonnant}`, `{name_mid}` … appear in the **`wesnoth`
  core** domain's `[naming]`/`[village_naming]` **markov name-generator** config strings
  (mixed with `$vars`, `|` alternation, and the `{!}` null-join). Also the
  `python-brace-format` flag class.
- Detection: `\{[A-Za-z_][A-Za-z0-9_]*\}`. Counts (corpus): **286 occ / 39 entries**.
- **T?** the name-list *values* are localized, but every `{key}` is a rule reference —
  preserve verbatim (a dropped/renamed brace breaks generation).

## 4. Command / CLI metasyntax (bare `<slot>`) — **preserve** (T2 classified)
- Bare single-token angle slots in `:command` help and man pages: `<side>`, `<nickname>`,
  `<file>`, `<number>`, `<var>=<value>`, `<command>`. These are **argument placeholders**,
  **not markup** — they never pair/close, so `validate_markup` counts them (30 occ, 17
  distinct across `wesnoth`/`lib`) and deliberately does **not** balance-check them.
- Distinguish from po4a: a bare `<side>` has no uppercase-letter prefix; `I<file>` (§3a-iii)
  does. Distinguish from Pango: no matching `</side>` ever exists.
- **T2 status:** classified (was "rare `<…>` tags"). Still no cited rule on translating the
  inner word → keep preserving the whole token.

## 5. XML/Pango character entities — **preserve escaped**
`&quot; &lt; &gt; &amp; &apos;` and numeric refs in **three** forms — decimal `&#8217;`,
XML hex `&#x7B;`, and **Wesnoth hex `&#0x7B;`** (a literal `{`, escaped because `{}` are WML
macro delimiters). Required because markup strings must escape `" < > &`. (This was the Q3 `&`
case; the hex forms were added session 001 after `&#0x7B;`/`&#0x7D;` caused false "unescaped
&" reports.)
- Detection: `&(?:quot|lt|gt|amp|apos|#(?:0x[0-9A-Fa-f]+|x[0-9A-Fa-f]+|\d+));`
- Counts (corpus): 90 occ / 63 entries.

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

## 10. Cross-locale invariants (multi-language, session 001)
`scripts/wesnoth/validate_placeholders.py` compares a translation `.po` against the source
`.pot` (matched by the natural key `(msgctxt, msgid, msgid_plural)`) and enforces what must
survive translation:
- **Named placeholders** (`$var`, `{brace}`): a translation may never **invent** a name
  (`$num`→`$number`) — hard error; a **non-plural** string may not **drop** one. Plural forms
  may legitimately omit the count var, so drops aren't flagged there.
- **printf** specifiers: a translation may not introduce a `%`-specifier the source lacks.
- **Markup**: each `msgstr` is balance-checked in its own family (§3).
- **Plural arity**: a plural entry must supply exactly the locale's `nplurals` (from the
  `.po` header `Plural-Forms`; en/de = 2, pl = 3) non-empty forms.
- **Pilot result (de/pl × 4 domains):** 8 **real** defects, 0 false positives — e.g. de
  `$num`→`$number` (misspelled), pl `$count` dropped, pl `$tag`→`$key` (wrong var).
