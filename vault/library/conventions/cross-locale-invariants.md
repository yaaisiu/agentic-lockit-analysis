---
type: convention
id: cross-locale-invariants
status: accepted
first_seen: wesnoth
also_seen: [veloren]
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
   For a **non-plural** string it must not **drop** a source name either.
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

**Scope note:** this is a *translation-phase* capability. When the current focus is the
**source** (English) analysis, build + test the checker as a prepared tool and run it in
earnest later. Template: [[validate_placeholders]].
