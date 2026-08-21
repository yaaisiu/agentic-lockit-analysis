---
type: heuristic
id: refusal-scope-discipline
status: accepted
first_seen: veloren
also_seen: [wesnoth]
promoted_session: "008"
---

# Heuristic: a refusal must be keyed to something the OUTPUT depends on

Refusing to produce output is the most expensive thing a deterministic tool can do: it converts
a partial, useful, honest result into nothing at all. That makes it the right response to a
defect that would make the output **wrong**, and the wrong response to everything else.

**Rule:** before writing a refusal, name the field of the output that becomes unreliable if this
defect stands. **If you cannot name one, it is not a refusal** — it is a reported number, a
per-row verdict field, or a warning in the census.

## Why this is a rule and not an anecdote — it has bitten twice

- **s007 (Veloren).** Refuse on structural `validate.py` ERRORs, `--force` to override. Correct,
  and the reasoning names the field: `m1 = hello { $x` yields `placeholders: []`, and in that
  contract an empty placeholder list is a **positive assertion** that there is no substitution
  point. The refusal protects a specific claim.
- **s008 (Wesnoth), the same class, the other way round — twice in one task.** The brief had
  already had to carve out an explicit exception so that **cross-locale content findings never
  block**: a target that dropped a `$var` is a real upstream translation bug that has been in
  the locale for years, and refusing on it means declining to export a corpus that legitimately
  contains them — the whole job returns nothing. Then, despite that, the first structural rule
  I wrote **refused all 26,312 rows** because two `.po` files carry no `Plural-Forms` header.
  Both of those domains have **zero plural entries**. No row in the bundle depended on the
  header. The check was *correct*; its **scope** was wrong.

Two instances in consecutive passes, one of them immediately after the same defect had been
fixed elsewhere in the same task. That is a rule.

## The seductive part

The failing check is usually *true*. The header really is missing; the metadata really is
malformed. It feels like diligence. What makes it wrong is that diligence about well-formed
metadata is being paid for with the entire output — and the person who wanted the output is not
in the room to object.

## The two categories, and their two reactions

| | what it is | reaction |
|---|---|---|
| **Structural** | the rows themselves are untrustworthy — a file that will not parse, a broken record block, a span that cannot be anchored | **refuse**; `--force` overrides *loudly* and records the fact in the artifact |
| **Content finding** | the data is well-formed and says something wrong — a dropped variable, a stale translation, a defect that is genuinely upstream | **never refuse**; emit a **per-row verdict field** and report the counts |

**Never conflate them.** The content-finding row is not bookkeeping: a later curation step is
required to either exclude those rows or include them *deliberately labelled* as known-bad
reference cases, and without the field it has nothing to label them from.

## How to apply

1. For each candidate refusal, write the sentence: *"without this, `<field>` in the output would
   be wrong."* No sentence → no refusal.
2. **Scope the condition to the rows that actually depend on it.** "Missing `Plural-Forms`" →
   "missing `Plural-Forms` **and the domain has a plural entry**". The narrow version is usually
   one clause longer and catches exactly the same real defects.
3. Give content findings a **closed-vocabulary verdict field** in the artifact, report the count
   per value, and name the affected ids. Ids only, never text ([[proprietary-vault-discipline]]
   / licence discipline).
4. Accumulate all problems and refuse **once**, printing the first ~25 — don't fail on the first.
5. When a refusal does fire in an unattended run, its message must say what to do: fix the
   source, or re-run with `--force`.
6. Expect a plausible finding count, and **say so in the brief**: a total far above the expected
   order of magnitude is itself a finding worth stopping to report, rather than an excuse to
   loosen the check until the number looks nice.

**Companion:** [[byte-stable-artifact]] (accumulate, then refuse once) ·
[[cross-locale-invariants]] (the classic source of content findings) · [[outlier-hunting]].
