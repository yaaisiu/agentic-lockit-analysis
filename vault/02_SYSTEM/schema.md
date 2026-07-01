---
type: system-doc
id: schema
status: active
updated: 2026-07-01
---

# Note schemas (frontmatter contracts)

The durable artifacts of this system are files, not chat. Every note carries YAML
frontmatter so it is queryable (Dataview) and machine-readable (portable to an API
runner later). Keep frontmatter minimal and typed; put prose in the body.

**Conventions**
- Dates are absolute ISO (`YYYY-MM-DD`), never "today".
- `lockit` values are the kebab-case `<name>` used under `vault/lockits/<name>/`,
  `data/<name>/`, `scripts/<name>/`.
- Cross-link related notes with `[[wikilinks]]`.
- **Never** put lockit *content* (source strings, keys) in `vault/library/` or any
  shared skill — the library holds generalised conventions only (spec §9).

---

## Per-lockit notes (`vault/lockits/<name>/`)

### `profile.md` — the data dictionary (the "chart")
```yaml
---
type: lockit-profile
lockit: <name>
format: xlsx | csv | po | json | ...
sheets: [<sheet>, ...]        # omit if not tabular-multisheet
locales: [en, pl, ...]        # source first if known
row_count: <int>
profiled_at: <YYYY-MM-DD>
session: <NNN>                # session id that produced/updated this
status: draft | confirmed     # confirmed only after GATE 1
---
```
Body headings (spec §5): Shape · String types · Key conventions · Variables & placeholders · Numbers · Conventions & control codes · Limits · Open questions resolved.

### `structure.md` — recon snapshot
```yaml
---
type: lockit-structure
lockit: <name>
format: <fmt>
encoding: <e.g. utf-8>
profiled_at: <YYYY-MM-DD>
---
```
Body: sheets/files, columns per sheet, row counts, delimiters, header rows, samples.

### `variables.md` — placeholder/variable inventory
```yaml
---
type: lockit-variables
lockit: <name>
updated: <YYYY-MM-DD>
---
```
Body: one entry per placeholder style — syntax, meaning, where it appears, detection
regex, translatable? Link to `[[library/conventions/<id>]]` when it matches a known one.

### `open-questions.md` — ambiguities + resolutions
```yaml
---
type: lockit-open-questions
lockit: <name>
updated: <YYYY-MM-DD>
---
```
Body: one entry per question → `status: open | resolved`, the decision, `decided_by`,
`decided_at`, and the gate (GATE 0/1/2) it was resolved at.

### `toolkit.md` — index of this lockit's scripts/skill
```yaml
---
type: lockit-toolkit
lockit: <name>
skill: lockit-<name>-toolkit
updated: <YYYY-MM-DD>
---
```
Body: one row per script — name, what it does, example invocation, tested? (date).

---

## Library notes (`vault/library/`) — client-free, generalised

### `conventions/<id>.md`
```yaml
---
type: convention
id: <kebab-id>
status: proposed | accepted
first_seen: <lockit>
also_seen: [<lockit>, ...]
promoted_session: <NNN>
---
```

### `heuristics/<id>.md`
```yaml
---
type: heuristic
id: <kebab-id>
status: proposed | accepted
first_seen: <lockit>
promoted_session: <NNN>
---
```
Body: the detection rule the inference step consults (what to look for → what it means).

### `script-templates/<id>.py`
A reusable, parameterised Python script. Header comment must state: purpose, the
convention/heuristic it embodies, `first_seen` lockit, and how to parameterise it.

---

## Dev notes (`vault/dev/`)

### `STATE.md` — "you are here" (single file, always current)
```yaml
---
type: dev-state
updated: <YYYY-MM-DD>
phase: <0-6>
active_lockit: <name | none>
---
```

### `sessions/NNN-<slug>.md` — session log
```yaml
---
type: session
id: <NNN>
date: <YYYY-MM-DD>
lockit: <name | none>
gates_cleared: [GATE 0, GATE 1, ...]
telemetry: { model_calls: <int|null>, input_tokens: <int|null>, output_tokens: <int|null>, est_cost_usd: <float|null> }
---
```
Body: what happened, decisions, promotions proposed/applied, next steps.

---

## Telemetry seam (north-star: token/cost awareness) — design-only for now

We are **not** building metering yet, but every note that represents a unit of work
reserves a `telemetry` block so cost/token data can be attached later without a schema
change. Shape (all fields nullable until wired):

```yaml
telemetry:
  model_calls: <int|null>       # count of LLM calls in this step/session
  input_tokens: <int|null>
  output_tokens: <int|null>
  est_cost_usd: <float|null>
  model: <string|null>          # which model did the work (routing decisions live here)
```

Rationale: the pipeline (spec §4) is a sequence of typed steps; attaching per-step
telemetry later lets us measure what each stage costs and route cheap vs. expensive
work deliberately. When this is wired, add a `library/` note describing the metering
contract so an API runner can emit the same shape. See [[STATE]] north-star goals.
