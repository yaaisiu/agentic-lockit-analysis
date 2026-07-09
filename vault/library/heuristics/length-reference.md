---
type: heuristic
id: length-reference
status: accepted
first_seen: hoi4
promoted_session: "004"
---

# Heuristic: no char-limit column? offer localised-vs-source LENGTH as a soft reference

**Rule (Marcin, session 004):** many lockits carry **no `max_length`/`char_limit` column** (there
is nothing to check against). Instead of giving up on length entirely, compute a **soft reference**
— compare each translation's length to the source string's — and surface large ratios. It is
**informational, never pass/fail**: long or short translations often overflow fixed-size UI
(buttons, tooltips, name plates), so the ratio is a *hint* worth a human glance, not a defect.

**When it applies:** any lockit where [[csv-tabular]]'s optional `max_length` column is absent and
the format has no length metadata — e.g. Clausewitz ([[clausewitz-pdx-yaml]]), gettext, Fluent.
(When a real char-limit column *does* exist, use a hard `find_over_limit`-style check instead.)

**How to apply (deterministic):**
1. Measure the **translatable** text length, not the raw value — strip the non-translatable
   constructs first (colour/icon/var/scope/escapes) so codes don't skew the count. Reuse the
   toolkit's `clean_text`/extract-clean pass.
2. Per key present in both source and target, compute `ratio = len(target) / len(source)`.
3. Flag `ratio ≥ R` or `ratio ≤ 1/R` (default **R = 1.6**); sort worst-first; **report the count
   and the top offenders**, labelled explicitly as a soft reference, not an error.
4. Ship it as a **prepared** tool (`validate --length-ref <src> <tgt>`) — it needs a translation,
   so when the current focus is the source locale, build+test it and run it in earnest later.

**Why:** it recovers *some* of the value a char-limit column would give, on the many lockits that
lack one, without inventing a false hard limit. Pairs with [[cross-locale-invariants]] (which
checks what must be *preserved*); this checks what might *overflow*.

**first_seen:** hoi4 (session 004) — Clausewitz has no length metadata; built as
`validate.py --length-ref` (soft ratio, translatable-text-based), verified on synthetic fixtures.
