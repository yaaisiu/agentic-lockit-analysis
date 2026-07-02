---
type: lockit-profile
lockit: wesnoth
format: gettext-pot
textdomains: [wesnoth-lib, wesnoth, wesnoth-units, wesnoth-httt]
locales: [en]
row_count: 5258
profiled_at: 2026-07-02
session: "000"
status: confirmed
---

# Wesnoth — profile (the chart)

The data dictionary for the Wesnoth lockit (English source, 4-domain subset). Confirmed
with Marcin at GATE 1 (2026-07-02). **No lockit content here** — examples are synthetic;
real strings live in gitignored `data/wesnoth/`. Companions: [[structure]], [[variables]],
[[context-prefixes]], [[open-questions]]. Standard-vs-Wesnoth conventions are proposed for
promotion in [[gettext-po]].

> **What kind of lockit this is:** a **GNU gettext** localisation set — *not* a spreadsheet.
> There is no key column, no char-limit column, no locale columns; identity is the source
> text itself, metadata lives in comments, and one file = one *textdomain* (string type).
> A profiler expecting rows/columns must not force that shape onto it.

## Shape
- Format: gettext PO **template** (`.pot`), UTF-8, flat entry list (blank-line separated).
- Subset: 4 of 32 textdomains, **5,258 entries**; ~105k tokens (full corpus ≈520k).
- Per file: a header entry (empty `msgid`) then entries of `msgid` (+ optional
  `msgid_plural`) with `#. #: #, #|` comments; `msgstr` empty in templates. Details:
  [[structure]].

## String types
- **Primary axis = the textdomain (file):** UI/settings → `wesnoth-lib`; core system →
  `wesnoth`; unit names/descriptions → `wesnoth-units`; campaign narrative/dialogue →
  `wesnoth-httt` (one of ~24 campaign domains).
- **Secondary axis = the `^` context prefix** (105 in subset), e.g. `menu section^…`,
  `log_level^…`, SI `prefix_kilo^…`. Full list: [[context-prefixes]].

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
- `$var` / `$obj.attr` / `$arr[0]` WML substitution; `|` terminates a name (`$var|`),
  space also terminates but is shown. **Preserve verbatim.**
- Caret `context^string`: engine strips through the first `^`; translate only the payload.
- Pango markup `<b> <i> <span>` (+ legacy `<italic>text='…'>`); translate only `text='…'`
  and prose. Help/command markup `<ref dst='' text=''>`, `<command>`, and command-usage
  metasyntax `<side>`/`<var>=<value>` — preserve tokens.
- XML entities `&quot; &lt; &gt; &amp;` — preserve escaped.

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
See [[open-questions]]: identity (Q1), gender/escape corrections (C3.1/C5.3), rare tags
(Q2), entities (Q3), prefix taxonomy (Q4); tracked T1 (var↔id link), T2/T3 (command/help
markup), T4 (registry growth as more domains arrive).
