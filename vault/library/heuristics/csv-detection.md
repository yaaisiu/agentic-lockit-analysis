---
type: heuristic
id: csv-detection
status: accepted
first_seen: a-dark-forest
promoted_session: "003"
---

# Heuristic: is this lockit a tabular key+locale-columns CSV/TSV?

**Recognise → don't re-infer.** The companion to [[gettext-detection]] for the *tabular* family.
If a lockit matches, jump to the [[csv-tabular]] anatomy and read it with [[csv_parse_template]];
only infer the project-specific extras (namespace scheme, context-column tag DSL, value shapes).

**Signals (a header row + locale columns is the strong one):**
- Extension `.csv` / `.tsv` (or a spreadsheet exported to one).
- **First row is a header** naming a key column (`key`/`id`/`string_id`/`name`) followed by
  **locale-code columns** (`en`, `pl`, `zh`, `pt_BR`, `fr`… — ISO-639-ish tokens).
- A **single file holds many locales as columns** (contrast: gettext/Fluent = one file per
  locale). One row = one string across all locales.
- Delimiter is comma or tab; the table is **rectangular** (every row == header width).
- Engine tells: a Godot `*.csv.import` sibling (`importer="csv_translation"`); or an Unreal/
  BYG-style `Key,SourceString,Comment,<Lang>` header.

**On match, expect** ([[csv-tabular]]): a namespaced key column (**not guaranteed unique**); a
non-locale **context/metadata column** (exclude from translation output); three cell value
shapes (scalar · JSON-array multi-value · empty, with intentional-vs-untranslated split); RFC-
4180 quoting (never hand-split on commas); optionally `max_length`/`char_limit`/`status` columns.

**Rule out the neighbours:**
- Not gettext ([[gettext-detection]]): no `msgid`/`msgstr`, no `.po`/`.pot`.
- Not Fluent ([[fluent-ftl]]): no `id = value` tree, no `{ $var }` placeables per-locale files.
- A `.csv` that is NOT a lockit (e.g. a change-log, a data table) has no locale-code columns —
  check the header, don't trust the extension.

**Then reach for** the dependency-free reader [[csv_parse_template]] rather than writing a parser
from scratch; label constructs (columns/tags/tokens) via [[construct-origin-labeling]].

**first_seen:** a-dark-forest — `localization.csv`, header `key,description,en,zh,fr,pt,pl,ua,th,es`,
Godot `.import` sibling confirmed the family.
