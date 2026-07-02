---
type: heuristic
id: review-dossier
status: accepted
first_seen: wesnoth
promoted_session: "000"
---

# Heuristic: present GATE 1 as a review dossier (claim → evidence → reasoning → confirm)

**Why.** A human can only confirm structure they can *verify*. Asserting "here's the
structure" invites rubber-stamping; a dossier that points at the real data makes the human
an effective check and surfaces corrections early (this is how the Wesnoth `male^`/escape/
identity corrections were caught).

**Method.** Before documenting, write a dossier (in **gitignored** `data/<name>/`, since it
cites real content) with one block per anatomy claim:
- **Claim** — what you infer.
- **Evidence** — exact `file:line` (+ context/entry id) and a short real example, so the
  reviewer can navigate straight to it.
- **Reasoning** — *why*, in plain language a weaker agent could follow.
- **Confirm / Correct** — a slot for the human's decision; flag ambiguities as questions.

**Back every quantitative claim with a number** (counts, coverage %, uniqueness) produced
by a script, not memory. When the reviewer confirms, record decisions in `open-questions.md`
and only then write the content-free committed notes. Re-open the dossier when new patterns
appear ("Round 2").

**Payoff:** the committed profile is *pre-verified*, and the dossier is a reusable audit
trail. Works for any lockit/dataset, not just gettext.
