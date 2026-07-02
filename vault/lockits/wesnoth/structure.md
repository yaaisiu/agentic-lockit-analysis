---
type: lockit-structure
lockit: wesnoth
format: gettext-pot
encoding: utf-8
profiled_at: 2026-07-02
---

# Wesnoth — structure (recon snapshot)

_Facts only; no lockit content. Real files live in gitignored `data/wesnoth/`._

## Source & scope
- Origin: `wesnoth/wesnoth` repo, `po/` tree (sparse/shallow clone in gitignored
  `sources/wesnoth/`). English source templates only.
- Profiled subset: **4 of 32 textdomains** — `wesnoth-lib` (UI), `wesnoth` (core),
  `wesnoth-units` (units), `wesnoth-httt` (campaign dialogue).
- Working copies: `data/wesnoth/pot/<domain>.pot`.

## Format
- **GNU gettext PO template (`.pot`)** — not tabular. A flat sequence of *entries*
  separated by blank lines. UTF-8 (from each file's header `Content-Type`).
- Each file opens with the standard empty-`msgid ""` **header entry**, whose `msgstr`
  holds metadata (`Content-Type`, a `Plural-Forms` placeholder in templates, etc.).

## Shape (subset)
| textdomain     | entries | with `^`prefix | with `#.[tag]:id` | with `#:` ref |
|----------------|--------:|---------------:|------------------:|--------------:|
| wesnoth-lib    |   1,682 |            164 |               690 |    1,682 (100%) |
| wesnoth (core) |   1,468 |             87 |               274 |    1,468 (100%) |
| wesnoth-units  |     878 |             90 |               664 |      878 (100%) |
| wesnoth-httt   |   1,230 |              9 |               119 |    1,230 (100%) |
| **total**      | **5,258** |          350 |             1,747 |         100% |

- Size: ~419k msgid chars ≈ **105k tokens** (subset). Full 32-domain corpus ≈ 26,312
  strings ≈ **520k tokens** → corpus-wide work must be **deterministic scripts**, not
  per-string LLM (see [[open-questions]] Q4).

## Per-entry fields (gettext model)
- `msgid` — source (English) string. **Unique within a domain** (0 dups in all 4).
- `msgstr` — translation; **empty** in these templates.
- `msgid_plural` — present on pluralizable entries (core 44, lib 2, httt 2, units 0).
- `msgctxt` — standard context field; **0 uses in Wesnoth** (it uses `^` instead).
- Comments: `#.` extracted (programmer→translator), `#:` source refs (`file:line`),
  `#,` flags, `#|` previous-msgid, `# ` translator notes. See [[variables]] for the
  in-string token conventions.

## `#.` comment composition (mixed field — preserve whole)
Per comment-line across the subset: `[tag]:id` provenance **2,180** · `[tag]` w/o id
**2,228** · freeform translator notes **148** · `TRANSLATORS:` **85** · other `#` hints
**70**. A script can split `[tag]:id` provenance from freeform hints, but keep all of it.

## Identity (confirmed GATE 1)
Natural key `(textdomain, msgctxt, msgid[, msgid_plural])`; `msgctxt` empty here so
`(domain, msgid)` is unique. Internal id `"<domain>:" + sha1(domain ⋮ msgctxt ⋮ msgid ⋮
msgid_plural)[:10]`. Nothing merged/dropped; line number is a locator, not the id.
