# Next-session kickoff

> **You don't need to paste this.** Run `/wake` — it reads this file automatically (with
> CLAUDE.md, STATE.md, the active lockit's notes, and the library) and summarises where we are.
>
> Context: s000 built the system + mapped Wesnoth (gettext). s001 corpus-wide + cross-locale QA.
> s002 Veloren (Fluent). s003 A Dark Forest (Godot CSV) — closed the tabular anatomy. **Next up:
> HoI4 (Paradox Clausewitz pseudo-YAML) — the biggest, most construct-heavy lockit yet, staged and
> researched at the end of s003.**

## Where we are
- **Three lockits, three formats, all gated + tooled.** Wesnoth · Veloren · A Dark Forest. Library
  has recognisers (`gettext-detection`, `csv-detection`), the origin-labeling + `--audit` drift
  machinery, `outlier-hunting`, `cross-locale-invariants`, and reader templates.
- **HoI4 is staged** in `sources/hoi4/` (gitignored — **proprietary Paradox content**, first
  NDA-class lockit; the gitignore discipline is now load-bearing). Includes the full **206 loose
  English `.yml`** files (14 MB) + `research.md` (Marcin's Clausewitz field guide).

## THE NEXT TARGET — HoI4 (Clausewitz pseudo-YAML). Intake → GATE 0 with a scoped slice.
Expect a multi-session lockit. `research.md` is essentially **pre-done recon for the whole
Paradox family** and was **validated against the real files** at end of s003:
- 206 files, all `l_english`, all **UTF-8-BOM**; **129,087 entries**.
- Format: `l_english:` header + `key:VERSION "value"` (version optional — present in only ~2%).
  **Not real YAML** → line-regex parser (`utf-8-sig`, comment-safe, malformed-tolerant); the doc's
  regex matched 100% of non-blank/comment lines. **Do not use PyYAML.**
- Construct density (entries containing): `§color…§!` 39.5k · `[scope/fn]` 17.9k · `$VAR$` 12.7k ·
  `\n` 6.2k · `£icon£` 1.4k · `@TAG` 200 · escaped `\"` 21. HoI4 is the OLD-style dialect
  (`§Y…§!` colours, `£icon£`, `@TAG` flags) — not the CK3/Vic3 `#key…#!` dialect.

### Step 0 — scope a representative SLICE (don't profile 129k entries at once)
Anatomy is uniform across files; value is **construct coverage**, not file count. Mirror Wesnoth
(one domain → all 32): profile a ~3–5 file slice that hits every construct, then scale.
- Candidate slice (confirm at GATE 0): a **focus** file (`$VAR$`/`[scope]`/`§`-heavy, e.g.
  `*_focus_l_english.yml`), an **events** file (`events_l_english.yml`, 3.4k entries, narrative +
  formatting), **`countries_l_english.yml`** (5.8k simple keys + `@TAG`), and one **`£icon£`**-rich
  file. Copy the confirmed slice into `data/hoi4/en/`; keep all 206 in `sources/` for the scale-up.
- These are the **loose English** files only — DLC-zip enumeration + cross-language alignment
  (the doc's big gotchas) are already sidestepped for this dataset.

### Then (later sessions)
- Build the shared line-regex reader + labeling registry (`§`/`£`/`@`/`$VAR$`/`[scope.fn]`/version)
  with `--audit` to surface the tail of surprises (unknown `§` letters, multi-line, odd keys).
- Scale across all 206; report construct inventory + any structural defects (dup keys across files).
- **Propose `library/conventions/clausewitz-pdx-yaml`** (through the gate) — the doc's per-game
  profile table (folder spelling, language set, encoding, colour/icon dialect, version-integer,
  replace-folder, DLC packaging) is exactly the "conventions as data" shape the library wants;
  HoI4 is the first profile row. Plus a `clausewitz-detection` heuristic + a reader template.

### Guardrails specific to HoI4
- **Proprietary content:** `data/hoi4/**` + `sources/hoi4/**` stay gitignored; **never** a string
  into `library/`, a skill, or any committed note. Surface defects; never redistribute dumps
  (non-commercial Paradox User Agreement — see `research.md` §Legal).
- Comments `#` only OUTSIDE quotes; don't hand-split on `#` or `,`. Version integer = optional
  metadata, never rely on it. Log-and-skip malformed lines (warn, don't silently truncate).

## Deferred (not blocking)
- **Char-limit column** — still the one untested §5 anatomy (`find_over_limit.py` never built);
  needs a dedicated hunt for a clean source that has it. Fallback if HoI4 stalls.
- North-stars still open: licence choice (#4), telemetry wiring (#3).

## Flow
`/intake hoi4` (files already staged) → GATE 0 (confirm the slice) → `/profile hoi4` → GATE 1 →
`/toolkit hoi4` → GATE 2 → scale + `/retro`. Library first (does anything recognise Clausewitz?).
