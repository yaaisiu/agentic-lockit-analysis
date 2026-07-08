---
type: heuristic
id: outlier-hunting
status: accepted
first_seen: veloren
also_seen: [a-dark-forest]
promoted_session: "002"
---

# Heuristic: hunt outliers — never assume a lockit is uniform

**Rule (Marcin, standing project rule, session 002):** when analysing any lockit, **actively
probe for outliers and inconsistencies** rather than describing the common case and moving on.
The interesting, defect-prone, and structure-revealing things hide in the exceptions.

**Probe at least these axes (deterministically, with a script):**
- **Key naming** — do all ids match the inferred pattern? (Found: most keys lowercase-snake,
  but a subset was PascalCase mirroring code enum names — a real, documentable exception.)
- **Placeholder charset** — do variable/token names include chars your regex would miss?
  (Found: UPPER and hyphenated variable names → the naive regex under-matched.)
- **Sub-unit shapes** — do records have sub-fields you didn't expect? (Found: an entire
  attribute role — named-enum lookups — invisible from the top-level census.)
- **Value shapes** — empties, containers (record with no top value, all content in sub-fields),
  multiline, internal blanks, flush-left continuations.
- **Cross-locale** — where source and translation structure diverge (but distinguish real
  defects from legitimate divergence — see [[cross-locale-invariants]]).

**Why:** a profile that only captures the majority case is confidently wrong at the margins,
and margins are where extraction silently drops data and where translations break. Surfacing
outliers early turns them into explicit gate decisions instead of latent bugs. It also feeds
[[construct-origin-labeling]]: the outliers you can't classify become the `unknown` bucket.

**How to apply:**
1. After the census, run an explicit *outlier pass* (a script): list ids that don't match the
   key pattern, tokens that don't match the placeholder regex, attribute/column names not yet
   catalogued, and value-shape anomalies.
2. Put the outliers in the GATE-1 review dossier ([[review-dossier]]) as questions, with
   `file:line` evidence — let the human confirm whether each is an exception, a defect, or a
   new rule.
3. Bake the resolved outliers into the profile + the labeling registry so the *next* run
   recognises them.

**Reflex, not a one-off:** treat "what are the outliers here?" as a required step at recon and
again at toolkit-build, on every lockit.

**Also seen (a-dark-forest, s003, tabular CSV):** the pass surfaced a **duplicate key** (identity
not unique), **malformed array cells** in one locale (`["?"],` stray trailing comma — a JSON-array
broken into scalar, which the *manual* scan missed but the strict parser caught), and the
**active-vs-deprecated** completeness distinction (most "untranslated" cells were `[DEPRECATED]`
rows; only one locale was genuinely partial). Confirms: outliers hide in value-shape corruption
and in status columns, not just key names.
