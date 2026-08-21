---
type: heuristic
id: construct-origin-labeling
status: accepted
first_seen: veloren
also_seen: [a-dark-forest, hoi4, wesnoth]
promoted_session: "002"
---

# Heuristic: label every construct's ORIGIN, and keep an UNKNOWN bucket (drift detector)

**Rule (Marcin, session 002):** whenever the toolkit recognises a construct — a placeholder
class, an attribute role, a function, a markup token, a column type — **label it with an
ORIGIN**, and route anything unrecognised to an explicit **`unknown`** bucket that a **drift
audit** surfaces. Never silently fold the unknown into "other".

**Origin values (three):**
- **`format`** — defined by the file format's spec (Fluent placeables, gettext `msgctxt`,
  CSV quoting…). Portable → this knowledge is a candidate to promote to `library/`.
- **`project`** — a convention the specific lockit layers on top (a custom function, what
  `.desc`/`.fem` *mean*, a project's key-prefix scheme). Stays in that lockit's toolkit.
- **`unknown`** — not in the registry → **FLAG**. This is the point: when the lockit changes
  (a new attribute role, a new function, a new column), it must SURFACE for a human to
  classify, not be mis-handled quietly.

**Why it matters:**
- **Drift detection.** Lockits evolve between deliveries. The `unknown` bucket + audit is how
  you notice a new construct the moment it appears. (First use: the audit found an entire
  uncatalogued attribute role — named-enum lookups — that the initial registry missed.)
- **Keeps the library clean.** Separating `format` from `project` tells you exactly what is
  reusable on the next file (promote) vs. what is one-lockit-specific (don't). Without the
  split, project quirks leak into `library/` and pollute the next inference.
- **Followable by a weak model.** Labeling is a table lookup; the audit is "list everything
  whose origin == unknown". Both are deterministic and cheap.

**How to apply:**
1. Put the labels in ONE registry module (single source of truth) that every tool imports —
   one edit updates the whole toolkit. The registry's comments ARE its documentation.
2. Provide `label_<thing>(x) -> (kind, origin, note)`; default the miss to `unknown`.
3. Ship a `--audit <dir>` that lists every `unknown` construct + where it first appears; wire
   an assertion into the tests (known corpus ⇒ 0 unknown; a synthetic novel token ⇒ flagged).
4. When the audit flags something, classify it deliberately and extend the registry (cite the
   session), or raise it at the next gate — do not widen a pattern just to silence it.

**Origin `format` generalises the per-format label (a-dark-forest, s003):** s002 used
`fluent` for spec-defined constructs; the portable name is **`format`** (defined by whatever
file format — Fluent, gettext, **CSV/JSON**). Use `format` going forward; `fluent`/`gettext` are
that origin for a specific format. First tabular application: labeled **columns** (locale vs
context vs identity), the **context-column tag DSL** (`[EMPTY]`/`[noun]`/…), **value shapes**
(scalar/array/empty), and **key-embedded constructs** (`-N` variant, `X` template slot) — with a
`--audit` that re-checks every run that no hidden markup/token crept in (0 unknown on the corpus).

**Two-tier drift audit (refinement, hoi4 s004):** a flat "unknown bucket" over-flags when a
construct space has an **expected but rare tail**. Split the audit into two tiers so
"unknown: 0" stays meaningful:
- **Tier 1 — DRIFT (fail):** genuinely foreign syntax that should NOT exist → nonzero = a real
  surprise. (HoI4: an escape beyond `\n`/`\t`, a colour letter outside the known set, a CK3-style
  `#…#!` span in an old-style file, a `{brace}`.) Wire the test/exit code to THIS.
- **Tier 2 — NOTED (report, don't fail):** real, expected-rare patterns worth surfacing but not
  drift. (HoI4: the ~21 escaped `\"`; colour spans that don't balance within one string because
  the colour is closed after a `$VAR$` concatenation.) List them with locations; don't count them
  as unknown.
Also: some vocabularies are **semi-open by design** — classify them into KINDS and never flag
them as drift. (HoI4 event-key `part`s: a closed core `t`/`desc`/options/`tt` **plus** open-ended
NAMED conditional variants writers invent, e.g. `keep_leader`, `desc.baltics` — expected, origin
`project`; catalogue their distribution rather than flagging each.)

**Origin `format` per family:** for Clausewitz ([[clausewitz-pdx-yaml]]) the `format`-origin
constructs are `§X`/`§!`, `£icon`, `@TAG`, `$VAR$`/`$VAR|fmt$`, `[scope.fn]`, `\n`/`\t`; the event
`part` meanings + key tag/suffix vocab are `project`. Verified: tier-1 drift = 0 across all 206
HoI4 files / 129,087 entries.

**Exporting a labeled value to a consumer (s007 proposed, s008 confirmed with a 2nd instance):**
a downstream contract will spell these labels differently from us. **Map at the boundary — never
rename this registry to chase a consumer**, because the registry also serves the inventory report,
the vault note and the GATE-1 dossier, where a human reads it. And **pass `unknown` through
UNCHANGED**: it is the drift signal telling the consumer not to trust the classification and to
escalate to a reviewer, so a map that helpfully collapses it to a plausible neighbour destroys the
only evidence that the lockit changed. Full rule, with both worked instances
(`ORIGIN_MAP` for Fluent origins, `CARET_SLUG` for gettext caret families):
[[boundary-vocabulary-mapping]].

**Companion:** pairs naturally with [[outlier-hunting]] (actively look for the unexpected) and
with any format convention ([[fluent-ftl]], [[gettext-po]], [[csv-tabular]], [[clausewitz-pdx-yaml]])
whose constructs get labeled. On the export side: [[boundary-vocabulary-mapping]].
