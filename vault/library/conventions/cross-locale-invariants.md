---
type: convention
id: cross-locale-invariants
status: accepted
first_seen: wesnoth
also_seen: [veloren, a-dark-forest, hoi4]
promoted_session: "001"
---

# Convention: what must survive translation (cross-locale invariants)

When a lockit has a **source** locale and **translation** locales, most structure in the
source string must appear intact in every translation. A deterministic check (source vs. a
translation, matched by the natural key) catches the common, game-breaking defects that a
human reviewer misses at scale.

**Match** source ↔ translation by the identity key (for gettext:
`(msgctxt, msgid, msgid_plural)` — the translation keeps the source `msgid` as its key).
Compare against the source's **display** form (strip any inline context prefix — a
translation never carries it).

**Invariants to enforce (per translated entry):**
1. **Named placeholders** (`$var`, `{brace}`, `%(name)s`, `{0}`…): a translation must not
   **invent** a name absent from the source (`$num`→`$number` = misspelling, renders literal).
   For a **non-plural** string it must not **drop** a source name either. (Tabular case,
   a-dark-forest: positional `{0}`–`{N}` slots — compare the SET of indices, not their order.)
5. **Positional-collection length** (added a-dark-forest, s003): when a cell holds a **list**
   of interchangeable/tiered values (a JSON-array cell, e.g. `["Yes","No"]`, or Fluent `.aN`),
   the translation must keep the **same element COUNT** as the source — dropping an option
   breaks the engine's indexing. Check length (an always-valid invariant); leave per-element
   **order** to human review, because the order rule is per-key (ordered tiers must align;
   random-pick sets may reorder — same caution as the random-pick note below).
2. **printf/positional specifiers** (`%d`, `%s`, `%1$s`): a translation must not introduce a
   specifier the source lacks (count/position sensitive).
3. **Markup**: each translated form balances in its own family (see [[markup-families]]).
4. **Plural arity**: a plural entry supplies exactly the locale's `nplurals` non-empty forms
   (from the `.po` header `Plural-Forms`; the count is per-language, e.g. en/de=2, pl=3).

**Do NOT over-constrain — legitimate divergence exists (Marcin, from practice):**
- **Plural forms may omit a variable** the other form needs (a singular form without the
  count var is correct) → never flag "dropped" on plural forms, only on non-plural.
- **Some strings legitimately add or drop content** in translation (a locale may need an
  extra particle, or drop an English-only distinction). Treat invariant violations as
  **flags for human review**, not automatic "bugs" — especially adds/drops of *whole words*
  vs. the hard cases (placeholder/markup/arity) which are almost always real.
- **Engine-supplied agreement variables** (added at Veloren, s002): a locale may legitimately
  **introduce** a placeholder the source lacks when the engine provides it for grammatical
  agreement (e.g. a `*_gender` context var an inflecting language needs but English doesn't).
  Do NOT flag these as "invented" — maintain a small allow-list / pattern of engine-supplied
  vars per lockit and exempt them (they're a `project`-origin construct, [[construct-origin-labeling]]).
- **Random-pick / positional variant collections** (added at Veloren, s002): when a message
  holds a SET of interchangeable variants (a random-pick array, e.g. Fluent `.a0/.a1/…`),
  matching a translation's variant *by index* to the source's is **unsound** — locales reorder
  them. Don't per-index diff placeholders on these; treat like plural forms (compare softly, or
  at the whole-set level), never a hard drop/invent ERROR.

**Severity:** placeholder invent/drop, extra printf, broken markup, wrong plural arity →
report; but remember the tool **surfaces** defects — when the data is third-party/upstream
(e.g. GPL translations), we do not fix it, we report it.

**Engine-delegated formats — token preservation is the real invariant (added hoi4, s004):** when
a format delegates morphology to engine functions rather than in-string selectors
([[morphology-location]]), **plural arity is meaningless** (there are no plural forms to count).
The invariant that matters is the **multiset of machine-readable tokens** the translation must
preserve. For Clausewitz ([[clausewitz-pdx-yaml]]): `$VAR$` variables, `[scope.fn]` data
functions, `£icon` icons, `@TAG` flags — a translation that DROPS or INVENTS one breaks rendering.
Normalise `$VAR|fmt$` on the **name only** (drop `|fmt`), so a legitimate colour/number-format
change isn't a false positive but a dropped variable still is. Colour codes (`§`) and `\n` are
**advisory** (formatting can legitimately shift). Same "surface, don't fix" rule on proprietary/
upstream data.

**Scope note:** this is a *translation-phase* capability. When the current focus is the
**source** (English) analysis, build + test the checker as a prepared tool and run it in
earnest later. Template: [[validate_placeholders]].
