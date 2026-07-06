---
type: heuristic
id: construct-origin-labeling
status: accepted
first_seen: veloren
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

**Companion:** pairs naturally with [[outlier-hunting]] (actively look for the unexpected) and
with any format convention ([[fluent-ftl]], [[gettext-po]]) whose constructs get labeled.
