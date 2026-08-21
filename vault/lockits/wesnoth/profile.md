---
type: lockit-profile
lockit: wesnoth
format: gettext-pot
textdomains: all-32
profiled_textdomains: [wesnoth-lib, wesnoth, wesnoth-units, wesnoth-httt]
locales: [en, de, pl]
row_count: 26312
markup_families: [pango, docbook, po4a]
profiled_at: 2026-07-02
session: "001"
status: confirmed
---

# Wesnoth — profile (the chart)

The data dictionary for the Wesnoth lockit. Confirmed with Marcin at GATE 1 on a 4-domain
English subset (session 000), then **confirmed corpus-wide across all 32 domains + a de/pl
translation pilot** (session 001). **No lockit content here** — examples are synthetic; real
strings live in gitignored `sources/wesnoth/` (+ `data/wesnoth/`). Companions: [[structure]],
[[variables]], [[context-prefixes]], [[open-questions]], [[toolkit]]. Standard-vs-Wesnoth
conventions are proposed for promotion in [[gettext-po]].

> **What kind of lockit this is:** a **GNU gettext** localisation set — *not* a spreadsheet.
> There is no key column, no char-limit column, no locale columns; identity is the source
> text itself, metadata lives in comments, and one file = one *textdomain* (string type).
> A profiler expecting rows/columns must not force that shape onto it.

## Shape
- Format: gettext PO **template** (`.pot`), UTF-8, flat entry list (blank-line separated).
- **All 32 textdomains, 26,312 entries** (~520k tokens). GATE 1 deep-profiled 4 domains
  (5,258 entries); session 001 confirmed the anatomy across the remaining 28 with no
  re-profiling — **`internal_id` 26,312/26,312 unique, 0 collisions**.
  > **An identity proof is a proof about ONE function (added s008, 2026-08-21).** The result
  > above measures `po_parse.internal_id` — 10 hex chars over
  > `domain ⋮ msgctxt ⋮ msgid ⋮ plural`. It says nothing about any other id over any other
  > preimage. s008 minted a *second* id for bundle export, `segment_id` (12 hex over
  > `msgctxt|msgid_raw`), and had to measure it separately: **also 26,312/26,312 unique, 0
  > collisions**, but that is a second result, not the same one. Whenever a count like this is
  > quoted, name the function it covers — otherwise good news reads as coverage it does not have.
- Per file: a header entry (empty `msgid`) then entries of `msgid` (+ optional
  `msgid_plural`) with `#. #: #, #|` comments; `msgstr` empty in templates (filled per
  locale in the `.po`). Details: [[structure]].

## String types
- **Primary axis = the textdomain (file):** UI/settings → `wesnoth-lib`; core system →
  `wesnoth`; unit names/descriptions → `wesnoth-units`; campaign narrative → `wesnoth-httt`
  (one of ~24 campaign domains).
- **Markup family also stratifies the domains** (session 001): **Pango** in the 29
  game-content domains; **DocBook** in `wesnoth-manual`; **po4a/POD man** in
  `wesnoth-manpages`; the `wesnoth` core also carries `{brace}` name-generator grammar.
  See [[variables]] §3.
- **Secondary axis = the `^` context prefix** (**129 corpus-wide**), e.g. `scenario name^…`,
  `log_level^…`, gender `female^…`, SI `prefix_kilo^…`. Full registry: [[context-prefixes]].

## Identity / keys  (GATE 1 decision)
- No key column. Natural key = **`(textdomain, msgctxt, msgid[, msgid_plural])`** — the
  standard gettext key. `msgctxt` is **always empty** in Wesnoth (it uses `^`), so
  `(domain, msgid)` is unique (proven 5,258/5,258).
- **Internal id** we mint: `"<domain>:" + sha1(domain ⋮ msgctxt ⋮ msgid ⋮ msgid_plural)[:10]`
  — stable across reordering; line number is a locator only.
- **Lossless rule:** preserve every field separately — msgid, plural, `^`-context, *all*
  `#.` comments (WML `[tag]`/`[tag]:id` + freeform notes), *all* `#:` refs, flags. Never
  merge or drop. Rationale: `^`-prefix (~7% of entries) and `#.[tag]:id` (partial, 509
  non-unique) are each too incomplete to be the key.

## Key / naming conventions
- Provenance (not identity) in `#.` comments: `[wml_tag]` and `[wml_tag]: id=<id>` name the
  WML element that produced the string; `#:` gives `source_file:line`.
- Gender via caret: `female^…` (×80), `male^…` (×1), `gender^…` (×3); base string = default.

## Variables & placeholders  (detail + regex in [[variables]])
- `$var` / `$obj.attr` / `$arr[0]` WML substitution; `|` terminates a name (`$var|`), space
  also terminates but is shown. **Preserve verbatim.** (Tokenizer stops at a sentence period,
  session 001.)
- `{brace}` name-generator grammar (`{prefix}{suffix}`) in the `wesnoth` core domain —
  preserve every `{key}`.
- Caret `context^string`: engine strips through the first `^`; translate only the payload.
- Markup, **three families** (auto-detected): **Pango** `<b> <i> <span>` (+ legacy
  `<italic>text='…'>`); **DocBook** `<emphasis> <link> <imagedata/>` (manual); **po4a**
  `B<…> I<…> E<lt>` (manpages). Translate only prose / `text='…'`; preserve tags.
- Bare `<side>`/`<nickname>` = CLI argument metasyntax (not markup) — preserve whole token.
- XML/Wesnoth entities `&quot; &lt; &amp; &#8217; &#x7B; &#0x7B;` — preserve escaped.

## Numbers
- No numeric ID/limit columns. Numbers arrive via `$vars`, printf `%d`/`%s` (rare), and
  strftime date formats (`%B %d %Y`). `#, c-format` flags mark `%`-bearing entries.

## Conventions & control codes
- Escapes present: `\n` (line break), `\t` (tab, in code-like strings), `\"`, `\\`.
- Plurals: standard gettext `msgid_plural` + `msgstr[N]`, selected by each `.po` header's
  `Plural-Forms`. The `.pot` only flags pluralizable strings. No `_pl/_sg` markers.

## Limits & constraints
- **None in the format.** gettext PO carries no char-limit/width metadata; none found.
  (Contrast with UI-spreadsheet lockits.) Revisit only if a future domain adds hints.

## Open questions resolved / tracked
See [[open-questions]]: identity (Q1), gender/escape corrections (C3.1/C5.3), rare tags (Q2),
entities (Q3), prefix taxonomy (Q4); **session 001** resolved T2 (CLI metasyntax classified),
T3 (help/man markup covered by DocBook+po4a families), T4 (registry regenerated 105→129).
Still tracked: T1 (value-level cross-domain agreement hazard), T5 (`family()` heuristic misses
gender/plural agreement variants), T6 (corpus-wide multi-locale QA sweep).
