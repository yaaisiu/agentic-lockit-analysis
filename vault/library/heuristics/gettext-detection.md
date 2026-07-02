---
type: heuristic
id: gettext-detection
status: accepted
first_seen: wesnoth
promoted_session: "000"
---

# Heuristic: is this lockit GNU gettext?

**Recognise → don't re-infer.** If a lockit matches, jump straight to [[gettext-po]] for
the standard model and only infer the project-specific extras.

**Signals (any strong one is enough):**
- Extension `.po` / `.pot` (or `.pot` template with empty `msgstr`s).
- A first entry `msgid ""` whose `msgstr` is a header with `Content-Type:` /
  `Plural-Forms:` / `Project-Id-Version:`.
- Lines beginning `msgid`, `msgstr`, `msgctxt`, `msgid_plural`; comments `#. #: #, #|`.

**On match, expect:** no key/limit columns; identity = `(domain, msgctxt, msgid[,plural])`;
metadata in comments; one file ≈ one textdomain (a string-type axis). Watch for a project
**inline context prefix** ([[inline-context-prefix]]) used instead of `msgctxt`.

**Then reach for** the dependency-free reader template [[po_parse_template]] rather than
writing a parser from scratch.
