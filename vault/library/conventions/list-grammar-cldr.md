---
type: convention
id: list-grammar-cldr
status: accepted
first_seen: wesnoth
also_seen: []
promoted_session: "000"
---

# Natural-language list grammar (CLDR-style conjunct / disjunct)

**Pattern.** A UI builds human lists — "A, B, and C" (conjunct / "and") or "A, B, or C"
(disjunct / "or") — from a set of **reusable join templates**, not one flat string. The
canonical shape (as in Unicode CLDR list formatting) is **four parts per list type**:

| part  | joins | generic illustration |
|-------|-------|----------------------|
| pair  | exactly two items            | `{first} and {second}` |
| start | first item + the rest        | `{first}, {rest}` |
| mid   | middle items                 | `{prefix}, {next}` |
| end   | the last item                | `{prefix}, and {last}` |

(disjunct = the same four with "or".)

**Why it matters (localization craft).** List conventions are **language-specific**: the
conjunction word, whether a comma precedes it (Oxford comma), spacing, and item position
all vary. These templates must be **rebuilt for the target language**, never translated
literally — a wrong join renders every list in the product ungrammatical. This is a
high-leverage, low-visibility detail: one bad template affects many surfaces.

**Detection heuristic.** Look for: keys/contexts naming `conjunct`/`disjunct`; a 4-way
`pair`/`start`/`mid`/`end` set; or use of an ICU/CLDR list-format API. When you see this in
a new lockit, **recognise it here** (add the lockit to `also_seen`) instead of re-inferring.

**Guidance for tooling.** Treat the join words/punctuation as translatable *structure*;
preserve the `{...}`/`$...` slots verbatim; validate that a translation keeps all slots.

**first_seen:** wesnoth — `wesnoth-lib`, `^`-context prefixes `conjunct pair/start/mid/end`
and `disjunct pair/start/mid/end` (slots as `$first/$second/$prefix/$next/$last`).
Related: the standard-gettext conventions note (proposed) `[[gettext-po]]`.
