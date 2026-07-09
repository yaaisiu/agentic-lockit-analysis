---
type: heuristic
id: clausewitz-detection
status: accepted
first_seen: hoi4
promoted_session: "004"
---

# Heuristic: is this lockit a Paradox Clausewitz pseudo-YAML file?

**Recognise → don't re-infer.** The third recogniser alongside [[gettext-detection]] and
[[csv-detection]], for the **Paradox** family (EU4, HoI4, Stellaris, CK3, Victoria 3, EU5). On a
match, jump to the [[clausewitz-pdx-yaml]] convention and read with [[clausewitz_parse_template]];
only infer the per-game dialect + project extras.

**Signals (the header + `key:VER "value"` line shape is the strong one):**
- Extension `.yml` **but NOT valid YAML** — a standard YAML parser errors. **Never use PyYAML.**
- A first line `l_<language>:` (lowercase L), e.g. `l_english:`, `l_french:`; the filename ends
  `<name>_l_<language>.yml`.
- Entries `KEY:[VERSION] "VALUE"` — key, colon, **optional integer**, space, double-quoted value.
- **UTF-8 with BOM** (`EF BB BF`) is the norm — read with `utf-8-sig`.
- Inline codes from the dialect: `§X…§!` colour, `£icon`, `@TAG`, `$VAR$`/`$VAR|fmt$`,
  `[scope.fn]`, or the new-style `#key…#!` / `@icon!` / `[concept|E]`.

**On match, expect** ([[clausewitz-pdx-yaml]]): identity = the key; the version integer is
**optional deprecated metadata** (a revision counter, not a selector, not identity); values hold
**unescaped inner `"`** → extract greedy first→last quote; `#` is a comment **only outside
quotes**; log-and-skip malformed lines. **Two dialects** — old-style (`§`/`£icon`/`@TAG`:
EU4/HoI4/Stellaris) vs new-style (`#key…#!`/`@icon!`: CK3/Vic3/EU5). DLC loc may be zipped.

**Rule out the neighbours:**
- Not gettext ([[gettext-detection]]): no `msgid`/`msgstr`.
- Not tabular CSV ([[csv-detection]]): no header row / locale columns — one language per file
  (or per `l_<lang>:` block), keyed lines not rows. (CK2 legacy IS semicolon-CSV — different.)
- Not Fluent ([[fluent-ftl]]): no `id = value` tree, no `{ $var }` placeables.

**Then reach for** [[clausewitz_parse_template]] (line-regex reader, not PyYAML); label the
dialect constructs via [[construct-origin-labeling]]. Note the morphology model differs sharply
from selector-based formats — see [[morphology-location]].

**first_seen:** hoi4 — 206 loose `_l_english.yml`, 129,087 entries, all UTF-8-BOM; old-style
dialect (`§Y…§!`, `£icon` with no closing £, `@TAG`); the line-regex matched 100%.
