---
type: convention
id: gettext-po
status: accepted
first_seen: wesnoth
also_seen: []
promoted_session: "000"
---

# GNU gettext PO/POT — standard conventions (reusable for ANY .po/.pot lockit)

Client-free reference distilled at session 000 (sources: GNU gettext manual). **Recognise
these before re-inferring** on any gettext lockit; only the *project-specific* extras
(e.g. Wesnoth's `^`, `$vars`) need fresh inference. See heuristic [[gettext-detection]].

## Files
- **`.pot`** = template, `msgstr` empty (extraction output). **`.po`** = one per language,
  `msgstr` filled. First entry has empty `msgid ""`; its `msgstr` is the **header** block
  (`Content-Type: … charset=UTF-8`, `Plural-Forms`, …).

## Entry fields
- `msgid` = source string; `msgstr` = translation; optional `msgctxt` (context); optional
  `msgid_plural` (+ `msgstr[0..N-1]`).
- **Identity key = `msgctxt` + `msgid`** (an absent `msgctxt` ≠ an empty one). Generalise
  with the textdomain: `(domain, msgctxt, msgid[, msgid_plural])`.

## Comment types (the leading char is meaningful)
| prefix | meaning | author |
|---|---|---|
| `#.` | extracted programmer→translator notes | programmer (via `xgettext`) |
| `#:` | source references `file:line` | tool |
| `#,` | flags: `fuzzy` (needs review; not used at runtime), `c-format` (validate `%`), … | tool/translator |
| `#\|` | previous msgid (shown when `fuzzy`) | tool |
| `# ` | free translator comments | translator |

## Plurals (how they work)
Header `Plural-Forms: nplurals=N; plural=EXPR;`. `EXPR` is a C expression on count `n`
returning the `msgstr[]` index. English: `nplurals=2; plural=(n!=1)`. Polish: 3 forms
(1→[0], 2–4→[1], else→[2]). The rule is **per-language, in each `.po` header** — the
`.pot` only marks which strings are pluralizable.

## Tooling guidance
- Preserve `%`/format tokens, entities, and markup verbatim; translate text only.
- A dependency-free reader is in [[po_parse_template]] (script-template).
- Detecting a gettext lockit: [[gettext-detection]]. Common project extra — an inline
  context prefix instead of `msgctxt`: [[inline-context-prefix]].
