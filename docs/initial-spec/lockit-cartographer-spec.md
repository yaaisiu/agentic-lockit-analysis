---
title: "Lockit Cartographer — PoC Spec & Architecture"
subtitle: "A human-guided system in Claude Code that maps the structure of any lockit (or tabular dataset), documents it in an Obsidian vault, and generates reusable deterministic scripts/skills to work with it"
status: draft-v2
supersedes: "the Cowork-scoped draft — same idea, now targeting Claude Code"
owner: Marcin
runs_in: Claude Code
date: 2026-06-19
---

# Lockit Cartographer — PoC Spec & Architecture

> Written wearing every hat — **Architect, Producer/PO, DevSecOps + Security/Compliance, full-round engineer, OOP craftsman, AI generalist**. The name is a placeholder. The idea is simple and durable: point it at an unknown lockit, give your guidance at the decisions that matter, and it leaves you a **chart** (documented structure) and a **toolkit** (reusable scripts/skills) — getting smarter at it each time.

---

## 1. What this is (and is not)

**This is a structure-discovery and tooling system for lockits — and, by the same pattern, for any tabular dataset.** Given any game lockit (the localisation file a vendor receives), it profiles the file's anatomy — string types, number formats, naming conventions, variables/placeholders, control codes, limits — **documents** all of it in an Obsidian vault, and **generates reusable deterministic scripts** to extract and transform its data. Those scripts are packaged as Claude Code **skills/commands** so the agent (and every later session) can work with the file cleanly.

**The generality is the point: no matter what file we provide, the system should build its toolkit and its structured data — guided by you.** That guidance is not a fallback; it is the steering mechanism. The model proposes structure; you confirm or correct at the gates; the system records your decisions and gets it right unprompted next time. An unknown dataset is tractable precisely *because* a human is in the loop at the few moments interpretation is genuinely ambiguous.

**It is NOT** (yet) a translator, a localisation engine, or the Polish weak-point auditor — those are *downstream*. You cannot reliably audit or process a lockit until you can reliably **read and understand its structure**. This system is that foundation.

**The durable artifacts are the scripts and the documentation, not the chat.** The LLM is the cartographer that discovers structure and writes the tools; deterministic Python is what runs — reproducibly and for free — every time after.

---

## 2. The working principle — discover with the model, extract with scripts

- **LLM does discovery and judgment.** Inferring what a column means, recognising `[PC]` as a control code and `{0}` as a variable, spotting that `_m`/`_f` keys are a gender convention, deciding when something is ambiguous — interpretation needs a model.
- **Deterministic scripts do extraction and transformation.** Once structure is confirmed, pulling all dialogue, inventorying placeholders, or finding over-limit strings should be **reproducible, fast, free, and testable** — a script, not a per-run LLM call.
- **The handoff is everything.** The model writes and validates the scripts once; the scripts become the file's permanent toolkit. Re-running an extraction next month costs nothing and gives identical results.

This is the only way "works on *any* file, guided by a human, and gets better over time" is affordable and trustworthy.

---

## 3. The environment: Claude Code

Claude Code is the right tool: a terminal-native agent with a full execution environment and first-class memory/extension surfaces. We use each natively (no workarounds):

- **`CLAUDE.md`, auto-loaded and cascading.** The root cornerstone (separate doc) loads every session; subdirectory `CLAUDE.md` files load when Claude works in that subtree; `@imports` pull in shared docs. This *is* the standing-instruction layer.
- **Full execution: bash, Python, git.** Write, run, test, and save deterministic extraction scripts directly; version the vault and the toolkit.
- **Skills** (`.claude/skills/<name>/SKILL.md`) — auto-loaded capabilities that can bundle executable scripts. The per-lockit toolkit and the cross-lockit know-how are skills.
- **Slash commands** (`.claude/commands/*.md`) — explicit rituals and tasks: `/profile`, `/toolkit`, `/wake`, `/retro`.
- **Subagents** (`.claude/agents/*.md`) — scoped, least-privilege helpers (e.g. a security/script reviewer) for context isolation and repeatable review.
- **Permissions** (`.claude/settings.json`) — a deny-leaning baseline that protects secrets and client data and blocks arbitrary egress (see §9).
- **Plan-and-approve.** Use plan mode / approval prompts so the human-in-the-loop **[GATE]s** are explicit, not implied.

*Claude Code's config surface evolves — confirm exact frontmatter/settings syntax against current Claude Code docs when scaffolding.*

The vault (files) + the generated skills (files) + git history are the system's real long-term memory — they persist across sessions and are fully traceable.

---

## 4. The pipeline (human-guided)

```mermaid
flowchart TD
    S[Scaffold the repo - no lockit needed yet] --> A0[Intake: you provide a lockit file<br/>OR a game repo/folder to search]
    A0 --> A1{Source mode?}
    A1 -->|file| A3[Place under data/name/]
    A1 -->|repo/folder| A2[Locate loc files by extension + heuristics<br/>list candidates] --> AG{{GATE 0: you confirm which files are in scope}} --> A3
    A3 --> B[Recon: format, sheets, columns, shapes]
    B --> C[Consult library: recognise known conventions first]
    C --> D[Infer structure - LLM judgment<br/>types, numbers, conventions, variables; flag ambiguities]
    D --> E{{GATE 1: you confirm / correct}}
    E --> F[Document: write the lockit profile to the vault<br/>+ enrich the cross-lockit library]
    F --> G[Generate deterministic scripts<br/>extract / inventory / validate; run + test on the lockit]
    G --> H{{GATE 2: you review the toolkit}}
    H --> I[Package scripts as a skill + slash commands]
    I --> J[Reflect & learn: promote reusable patterns/templates<br/>write session note + prepare next kickoff]
```

Scaffolding (Phase 0) needs **no lockit** — the system is built first, then the lockit is brought in as the first real step of the process. **Intake has two modes:** (A) you hand it a lockit file (or files); or (B) you point it at a **game repository or folder** and it *finds* the localisation/lockit files itself — scanning for known formats (`.po`/`.pot`, lang `.txt`, `.ftl`, `.properties`, `.strings`, `.resx`, `.json`, `.csv`, `.xlsx`) plus name/content heuristics — and lists candidates for you to confirm (**GATE 0**) before anything is profiled.

| Step | Type | Output | Gate |
|------|------|--------|------|
| **Intake** | human + deterministic | the lockit acquired — file placed, or loc files located in a provided repo/folder and confirmed | **GATE 0** (repo mode) |
| Recon | deterministic | structural snapshot (sheets/files, columns, row counts, samples) | — |
| Library consult | retrieval | matches against known conventions (recognition before cold inference) | — |
| Infer structure | LLM | semantic column/field map, string-type scheme, number formats, variable/placeholder inventory, naming conventions, control codes, limits — **ambiguities flagged** | — |
| **Confirm** | human | corrected, approved structure | **GATE 1** |
| Document | deterministic write | `profile.md` + supporting notes; library updated | — |
| Generate tools | LLM writes, bash runs | tested Python extraction scripts | — |
| **Review tools** | human | approved/refined toolkit | **GATE 2** |
| Package | deterministic | a `lockit-<name>-toolkit` skill (+ optional `/lockit:*` commands) | — |
| Reflect | LLM + write | promoted templates/conventions, session note, next-session kickoff | — |

---

## 5. Lockit anatomy — what gets profiled

The concrete checklist the inference step works through (and the headings the profile note documents):

- **Format & shape** — file type, sheets/tabs, columns, row count, encoding, delimiters, merged cells, header rows.
- **Column semantics** — string ID/key, source text, locale columns, context/description, **character/length limit**, max width, speaker/character, audio reference, scene/quest id, workflow/status, notes, do-not-translate flags.
- **String types** — UI label, button, menu, dialogue/VO, subtitle, system message, tutorial, item name/description, error, achievement, marketing — *however this file marks them* (a type column, key prefixes, or separate sheets).
- **Key-naming conventions** — namespaces/prefixes (`UI_`, `DLG_`, `SYS_`), delimiters/hierarchy, gender/number markers (`_m`/`_f`, `_sg`/`_pl`), platform/variant suffixes.
- **Variables & placeholders** — every style present (`{0}`, `{name}`, `%s`, `%1$s`, `[TAG]`, `<tag>`, `{{var}}`, `$var`), control codes, colour/format tags, line-break codes, icon/sprite tokens — with **syntax, meaning, and where each appears**.
- **Numbers** — IDs, indices, counts, version numbers, char-limit values; whether numbers live in keys, in text, or in dedicated columns; number formatting.
- **Conventions & control codes** — markup (bold/colour), line breaks (`\n`, `<br>`), escapes, ICU/MessageFormat usage, plural markers, ruby/furigana, game-specific codes.
- **Limits & constraints** — character limits, display constraints, forbidden characters.

This list is itself a **library asset** — it sharpens as new files reveal new patterns. (For a non-lockit dataset, the same step generalises to: detect entities, types, identifiers, units, encodings, and conventions — the headings change, the method doesn't.)

---

## 6. The repo / Obsidian vault (documentation = the system's memory)

One repo. The vault lives inside it (one folder Obsidian opens), the `.claude/` machinery beside it. Markdown, YAML frontmatter, wikilinks, Dataview-friendly.

```
lockit-cartographer/
  CLAUDE.md                      # the cornerstone (auto-loaded; separate doc)
  .claude/
    settings.json                # deny-leaning permissions (§9)
    skills/
      lockit-<name>-toolkit/     # generated per-lockit capability (SKILL.md + scripts)
    commands/                    # /profile, /toolkit, /wake, /retro
    agents/                      # e.g. script-reviewer (least-privilege)
  vault/
    lockits/
      <lockit-name>/
        profile.md               # THE data dictionary: columns, types, conventions, examples
        structure.md             # sheets/columns/shapes/formats
        variables.md             # placeholder/variable conventions found, with examples
        open-questions.md        # ambiguities + the decisions that resolved them
        toolkit.md               # index of scripts/skill for this lockit
    library/                     # CROSS-LOCKIT brain (grows from the process loop)
      conventions/<id>.md        # recognised patterns (placeholder styles, key/type schemes)
      heuristics/<id>.md         # detection heuristics the inference step consults
      script-templates/<id>.py   # reusable extraction-script patterns
      glossary.md
    dev/
      STATE.md                   # "you are here"
      sessions/NNN-*.md          # session notes
    02_SYSTEM/schema.md          # note frontmatter schemas
  scripts/<name>/                # per-lockit scripts (also referenced by the skill)
  sources/<name>/                # a provided game repo/folder to search for loc files (GITIGNORED)
  data/<name>/                   # the acquired lockit file(s) + extraction outputs (GITIGNORED — client data)
  .gitignore                     # data/**, sources/**, .env*
```

**Zones, two lifecycles.** `sources/<name>/` holds a game repo/folder you brought in to be searched; `data/<name>/` holds the acquired lockit file(s) + outputs. Both are **gitignored — client/third-party data**. `vault/lockits/<name>/` *describes* the file; `vault/library/` is generalised, reusable, **client-free** knowledge — the thing that makes the next file faster because the system recognises conventions it has already seen.

---

## 7. The generated toolkit (scripts → skill)

Per lockit, generate and test deterministic scripts such as: `profile_lockit.py` (recon, codified), `extract_by_type.py`, `list_placeholders.py` (inventory + counts + which keys), `find_over_limit.py`, `gender_pairs.py`, `validate_placeholders.py` (cross-locale consistency), `export_subset.py`.

Validate on the actual lockit, then **package as a Claude Code skill** (`.claude/skills/lockit-<name>-toolkit/SKILL.md` + the scripts) with a description that tells Claude when to use it. Common queries can also become **`/lockit:*` slash commands**. Scripts that prove broadly useful get **promoted** to `vault/library/script-templates/`, so the next file starts from a template, not a blank page.

---

## 8. How the system learns (from you and from the processes)

Two loops, both writing to disk (vault + skills) and git-tracked, so learning persists and is traceable:

- **Human loop.** At GATE 1/2 you confirm or correct the inferred structure and the toolkit. Each correction lands in `open-questions.md` and, when it reflects a general truth, is distilled into a `library/heuristics/` or `library/conventions/` note — so the inference step (and `CLAUDE.md`) get it right next time without being told again.
- **Process loop.** Patterns recurring across files, and scripts that prove reusable, are **promoted**: conventions → `library/conventions/`; detection rules → `library/heuristics/`; working scripts → `library/script-templates/`. The inference step **consults the library first** — recognition before cold inference.

**Guardrail:** the system never silently rewrites its own `library/`, a skill, or `CLAUDE.md`. Promotions and rule changes are **proposed at reflection, approved by you, then applied** — each committed with the lockit/session id that produced it.

---

## 9. Security, privacy & compliance (day one)

Lockits are **client-confidential, usually NDA-bound**. Establish the baseline from commit one.

- **Deny-leaning permissions** in `.claude/settings.json`: allow `Read/Edit/Write` in-repo, `Bash(python:*)`, `Bash(pytest:*)`, `Bash(git status|diff|add|commit)`; **`ask`** on `git push`, `git clone`, `WebFetch`, `WebSearch`; **`deny`** reading `.env*`/secrets, `curl`/`wget`, `rm -rf`, and writes outside the repo. Per-agent tool limits via subagent frontmatter.
- **Intake safely.** Prefer pointing at a **local** game repo/folder (no egress). If you give a URL, cloning goes into gitignored `sources/<name>/` and is **`ask`**-gated. Read the source repo **read-only**; copy only the confirmed loc files into `data/<name>/`.
- **Client/third-party data stays put.** `data/**` and `sources/**` are **gitignored**; **never put lockit content into `library/` or any shared skill** — the library holds *generalised conventions*, not content.
- **No arbitrary egress.** Deterministic scripts read/write local files only; no network. Keep web/connectors out of this workflow unless explicitly needed.
- **Trusted skills only.** Only run skills you or Anthropic authored; our generated skills are trusted only after GATE 2 review.
- **HITL on consequential actions.** Gate any write that leaves the repo; approve pushes and clones.

---

## 10. Success criteria (PoC is "done" when)

1. Point Claude Code at a **provided** lockit and produce a complete `profile.md` (the anatomy of §5) in the vault, with ambiguities resolved at GATE 1 by your guidance.
2. Generate and **validate ≥ 4 deterministic extraction scripts** that run correctly on that lockit.
3. **Package** them as a working `lockit-<name>-toolkit` skill that a fresh session can invoke to query the lockit.
4. The **`library/` gains ≥ 1 reusable asset** (a convention, heuristic, or script template) — evidence the process loop works.
5. **No client content** in `library/` or any shared skill; `data/**` gitignored.
6. A **session note + next-session kickoff** are written, so the next session resumes cleanly — and a *second*, differently-structured file can be profiled faster by recognition.

---

## 11. Build plan (lean slices)

- **Phase 0 — Repo + cornerstone (no lockit needed).** Scaffold the repo/vault skeleton (§6), `CLAUDE.md`, `.claude/settings.json`, `schema.md`, the `/intake` `/profile` `/toolkit` `/wake` `/retro` commands, and a `.gitignore` (covering `data/**`, `sources/**`). Nothing to profile yet — the system is built first.
- **Phase 1 — Intake → GATE 0.** Bring the lockit in: either place a provided file under `data/<name>/`, or point at a game repo/folder in `sources/<name>/` and **locate** its loc files (by extension + heuristics), then confirm which are in scope.
- **Phase 2 — Recon → infer → GATE 1.** Profile the acquired lockit's structure, consult the (empty) library, infer semantics, flag ambiguities, confirm with you, write `profile.md` and friends.
- **Phase 3 — Toolkit generation → GATE 2.** Generate, run, and test the extraction scripts; review and refine.
- **Phase 4 — Packaging.** Wrap the scripts as the per-lockit skill (+ optional slash commands); index in `toolkit.md`.
- **Phase 5 — Reflect & seed the library.** Promote ≥ 1 reusable asset; write the session note + next kickoff.
- **Phase 6 — Second file (the real test).** Intake and profile a *different* lockit/dataset (or a different game repo) and measure whether the library made it faster. This is where "works on anything, guided, and improves" is proven.

---

## 12. Open decisions

1. **First intake** — will the first lockit arrive as a file, or as a game repo/folder we search? (Either works; the system figures out the reader regardless — no format decided up front.)
2. **Skill granularity** — one per-lockit toolkit skill vs. a shared `lockit-tools` skill parameterised by profile. Start per-lockit (concrete), generalise later.
3. **Versioning** — git the vault + library (client data gitignored) from the start? (Recommended — it's what makes learning traceable.)
4. **Slash commands now or later** — package common queries as `/lockit:*` in Phase 3, or defer.
5. **Profiling depth at GATE 1** — full anatomy vs. a fast first pass that deepens on demand.

---

## Appendix A — Example `profile.md`
```markdown
---
type: lockit-profile
lockit: aurora-rpg-v3
format: xlsx
sheets: [UI, Dialogue, Items, System]
locales: [en, fr, de, pl]
profiled_at: 2026-06-19
status: confirmed
---

## Shape
4 sheets; ~6,200 rows. Header row 1. Key in col A, source (en) in col C, locale
columns D–F, char-limit in col G, context in col H, speaker in col I (Dialogue only).

## String types
Marked by **key prefix**: UI_, BTN_, DLG_, SYS_, ITEM_, TUT_. (No type column.)

## Key conventions
`<TYPE>_<scene/screen>_<n>` ; gender variants as `..._m` / `..._f` (Dialogue, Items).

## Variables & placeholders
- `{playerName}` — player name insertion. DLG_, SYS_.
- `[ICON:x]` — inline icon token. UI_, ITEM_.
- `%d` — numeric count. SYS_, ITEM_.
- `\n` — line break. All.
See [[variables]] and [[library/conventions/icon-bracket-token]].

## Numbers
Char limits in col G (integers). Counts via `%d` in text. IDs embedded in keys.

## Limits
Col G char limit applies to UI_/BTN_ only (others blank = no limit).

## Open questions resolved
- Col J ("M") → confirmed: max display width (px). [[open-questions]]
```

## Appendix B — Example generated script
```python
# scripts/aurora-rpg-v3/list_placeholders.py
# source: profile aurora-rpg-v3 (GATE 1 confirmed) — regenerate via toolkit skill
"""Inventory every placeholder/variable: counts + which keys use each."""
import sys, re, collections
import pandas as pd

PATTERNS = {
    "curly_named": re.compile(r"\{[A-Za-z_]\w*\}"),
    "icon_token":  re.compile(r"\[ICON:[^\]]+\]"),
    "printf_num":  re.compile(r"%\d?\$?d"),
}

def main(path: str, source_col: str = "en", key_col: str = "key"):
    sheets = pd.read_excel(path, sheet_name=None)
    found = collections.defaultdict(lambda: collections.defaultdict(list))
    for sheet, frame in sheets.items():
        if source_col not in frame.columns:
            continue
        for _, row in frame.iterrows():
            text = str(row.get(source_col, ""))
            for name, pat in PATTERNS.items():
                for token in pat.findall(text):
                    found[name][token].append(f"{sheet}:{row.get(key_col, '?')}")
    for name, hits in found.items():
        print(f"\n## {name}")
        for token, keys in sorted(hits.items(), key=lambda kv: -len(kv[1])):
            print(f"  {token:20} {len(keys):5}  e.g. {keys[0]}")

if __name__ == "__main__":
    main(*sys.argv[1:])
```

## Appendix C — Example generated skill (`.claude/skills/lockit-aurora-rpg-v3-toolkit/SKILL.md`)
```markdown
---
name: lockit-aurora-rpg-v3-toolkit
description: >
  Use to extract, inventory, or validate data from the aurora-rpg-v3 lockit —
  e.g. "list all placeholders", "pull all DLG_ dialogue", "find over-limit strings",
  "check placeholder consistency across fr/de/pl". Wraps tested deterministic
  scripts; prefer these over ad-hoc parsing for this lockit.
---

# aurora-rpg-v3 toolkit
Structure is documented in vault/lockits/aurora-rpg-v3/profile.md — read it if unsure.

Run (lockit path is data/aurora-rpg-v3/<file>):
- `python scripts/aurora-rpg-v3/list_placeholders.py <path>` — placeholder inventory.
- `python scripts/aurora-rpg-v3/extract_by_type.py <path> <PREFIX>` — strings of a type.
- `python scripts/aurora-rpg-v3/find_over_limit.py <path>` — over-char-limit strings.
- `python scripts/aurora-rpg-v3/validate_placeholders.py <path>` — cross-locale consistency.

If the structure has changed, re-profile and update profile.md before trusting these,
and propose any convention change to the library.
```

## Appendix D — Example `.claude/settings.json` (deny-leaning)
```jsonc
{
  "permissions": {
    "allow": ["Read","Edit","Write","Grep","Glob","Bash(python:*)","Bash(pytest:*)",
              "Bash(git status)","Bash(git diff:*)","Bash(git add:*)","Bash(git commit:*)"],
    "ask":   ["Bash(git push:*)","WebFetch","WebSearch"],
    "deny":  ["Read(./.env)","Read(./.env.*)","Read(**/secrets/**)",
              "Bash(curl:*)","Bash(wget:*)","Bash(rm -rf:*)","Write(/**)","Edit(/**)"]
  }
}
```

## Appendix E — Example library asset (process-loop output)
```markdown
---
type: convention
id: icon-bracket-token
status: accepted
first_seen: aurora-rpg-v3
also_seen: []
---

# Inline icon token: `[ICON:<name>]`
Engine replaces it with a sprite at runtime. Treat as a **non-translatable variable**:
preserve verbatim, never localise the inner name.
**Detection:** `\[ICON:[^\]]+\]`. **Where:** UI and item strings.
When this style appears in a new file, recognise it here instead of re-inferring; add
the new lockit to `also_seen`.
```

---

*End. Simple on purpose: map one file well — guided by you — leave a chart and a toolkit, and let the library make the next one faster.*