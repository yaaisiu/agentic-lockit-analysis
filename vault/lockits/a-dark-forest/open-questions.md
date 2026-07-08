---
type: lockit-open-questions
lockit: a-dark-forest
updated: 2026-07-07
---

# A Dark Forest — open questions & decisions

## Resolved at GATE 0

### Q0.1 — Which file is the lockit? (scope)
- **status:** resolved
- **decision:** `assets/i18n/localization.csv` (Godot CSV translation table) is the lockit.
  Copied into `data/a-dark-forest/localization.csv` (+ `localization.csv.import` for the
  delimiter/locale-mapping metadata; + `UPSTREAM-LICENSE.txt`). The sibling
  `localization.*.translation` files are Godot's *compiled* binaries — outputs, not source
  — and are out of scope.
- **decided_by:** Marcin · **decided_at:** 2026-07-07 · **gate:** GATE 0
- **facts (from intake, pre-profile):** header `key,description,en,zh,fr,pt,pl,ua,th,es`;
  675 data rows; key column + `description` context column + 8 locale columns
  (en, zh, fr, pt, pl, ua, th, es); comma-delimited (`.import` `delimiter=0`). Godot compiles
  `description` as a pseudo-locale (`localization.description.translation`).

### Q0.2 — Licence: is the lockit content usable for this generality test?
- **status:** resolved
- **decision:** Yes — as **gitignored, non-commercial, test-only** data. The upstream
  LICENSE is MIXED: only `*.gd` **code** is MIT; the **localisation content** (every locale,
  incl. Polish, and the English narrative source) is **CC-BY-NC-SA 4.0**. This is *not* the
  "spotless MIT" the file was originally picked for — it is the same NonCommercial tier we'd
  have accepted for LocJAM. Acceptable because `data/**`/`sources/**` are gitignored, the
  content never ships publicly and never enters `library/` or any skill. **Attribution +
  NonCommercial + ShareAlike** to be honoured if any derived data were ever released (it is
  not). Source: `sources/a-dark-forest/LICENSE` (§ Localization, § Writing and Narrative Design).
- **decided_by:** Marcin · **decided_at:** 2026-07-07 · **gate:** GATE 0

## Resolved at GATE 1 (2026-07-07, dossier `data/a-dark-forest/gate1-review.md`)

All anatomy claims A1–A3 · B1–B3 · C1–C2 · D1–D2 · E1–E2 **confirmed** by Marcin. Decisions:
- **Q1 — duplicate key `ui_label:heart`:** upstream data bug; toolkit **flags** duplicate keys,
  reports (does not fix — third-party data). *(yes)*
- **Q2 — `description` column:** context-only; **excluded** from translate/extract output,
  **kept** as metadata + surfaced to translators; Godot pseudo-locale quirk noted. *(yes to both)*
- **Q3 — JSON-array cells:** toolkit **parses elements** individually **and enforces element-count
  parity** across locales. Order rule is **per-key** (ordered tiers must align; interchangeable
  pairs/random-pick are order-free, like Veloren `.aN`). *(yes to both)*
- **Q4 — `[DEPRECATED]` rows (27):** **excluded from extraction by default** (opt-in include),
  **counted** in the report. *(yes)*
- **Q5 — `X` template keys (`reborn_X_line_*`):** documented as a `project` key-template construct;
  no special handling; **explicit note** kept because the runtime mechanism isn't fully certain.
  *(agreed)*
- **B3 (Marcin):** completeness stats (intentional `[EMPTY]` vs untranslated) are a reported metric.
- **D2 (Marcin):** ran an explicit **hidden-markup drift sweep** — **clean** (0 unknown constructs;
  only a literal `&` in 2 English job titles). Confirms no markup family.
- **decided_by:** Marcin · **decided_at:** 2026-07-07 · **gate:** GATE 1

## Deferred (not this round)

### Q0.3 — Char-limit / max-length column anatomy — STILL UNTESTED
- **status:** open (deferred by Marcin, 2026-07-07)
- **context:** The one §5 anatomy no lockit has exercised. Three scouts hunted specifically;
  no verifiable, acceptably-licensed file with a real char-limit column was found (Godot CSV
  only supports optional `?context`/`?plural`; the one open sheet that had it is 410 Gone;
  the LocJAM 3 xlsx turned out to be board-game maps, not a lockit — dropped). A Dark Forest
  closes key-column + context + many-locales + CSV-escaping, but **not char-limit**. Revisit
  in a dedicated future hunt.

## To carry into GATE 1 (profiling)
- Confirm delimiter/quoting behaviour and any embedded commas/quotes/newlines in cells
  (CSV-escaping failure modes — a first for this system).
- Confirm the role of `description`: is it English-only translator context, or does it vary?
  Godot treats it as a pseudo-locale — worth an explicit note.
- Key convention: keys look namespaced with `:` (`ui_label:thank_you`). Confirm the scheme
  and hunt for outliers (`outlier-hunting` heuristic).
- Script variety across locales (CJK zh, Cyrillic ua, Thai th) — encoding sanity.
