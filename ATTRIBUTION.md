# Attribution & upstream notices

Lockit Cartographer is a method for analysing localisation files, demonstrated on four
real games as worked examples. **No third-party game content is redistributed here** —
real lockit files live under the gitignored `data/` and `sources/` directories and are
never committed. The analysis notes under `vault/lockits/` describe file *structure* using
synthetic examples and bare identifiers (keys, namespaces, filenames), not source strings.

We nonetheless credit every upstream whose files we studied, and record their licences so
anyone reproducing this work knows the terms that apply to the underlying data.

## Worked-example upstreams

| Example | Upstream | Code licence | Localisation-content licence |
|---|---|---|---|
| Wesnoth (gettext `.po`/`.pot`) | [wesnoth/wesnoth](https://github.com/wesnoth/wesnoth) | GPL-2.0 | GPL-2.0 (content shareable **with attribution**) |
| Veloren (Fluent `.ftl`) | [veloren/veloren](https://gitlab.com/veloren/dev/veloren) | GPL-3.0 | GPL-3.0 (content shareable **with attribution**) |
| A Dark Forest (Godot CSV) | [TinyTakinTeller/GodotProjectZero](https://github.com/TinyTakinTeller/GodotProjectZero) | MIT (`*.gd` code) | **CC-BY-NC-SA 4.0** (all locale strings + English narrative) |
| Hearts of Iron IV (Clausewitz pseudo-YAML) | Paradox Interactive | Proprietary | **Proprietary / NDA-class — not included, not attributed with content** |

Notes:

- **A Dark Forest** — only the `*.gd` code is MIT; every localisation string (including the
  Polish and the English narrative) is **CC-BY-NC-SA 4.0**. It was used as gitignored,
  non-commercial, test-only data. No strings are committed; the vault notes contain only
  identifiers and synthetic examples.
- **Hearts of Iron IV** — proprietary Paradox content, treated as NDA-class. It is the reason
  this project's proprietary-vault discipline exists: real strings never leave the gitignored
  `data/`, committed notes are synthetic, and nothing HoI4 ships here. No HoI4 content is
  redistributed, so no content licence is granted or implied.

## This repository's own licences

- Code (`scripts/`, `.claude/`, `*.py`): **Apache-2.0** — [`LICENSE`](LICENSE).
- Docs & vault (`vault/`, `docs/`, `README.md`, `CLAUDE.md`): **CC-BY-4.0** —
  [`LICENSE-docs.md`](LICENSE-docs.md).

Copyright 2026 Lockit Cartographer contributors.
