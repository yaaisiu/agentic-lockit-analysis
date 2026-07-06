---
type: lockit-context-prefixes
lockit: wesnoth
updated: 2026-07-02
generated_by: scripts/wesnoth/list_context_prefixes.py (corpus-wide, 32 domains)
---

# Wesnoth — `^` context-prefix registry

_The set of caret-context prefixes (token before the first `^`). These are **structural
identifiers**, not lockit content. Regenerate deterministically — never hand-maintain:_

```
python3 scripts/wesnoth/list_context_prefixes.py sources/wesnoth/po/*/*.pot
```

**Corpus scope:** all **32 textdomains** · **129 distinct prefixes** · **712 prefixed
entries** (was 105 / 350 on the 4-domain subset — the T4-tracked growth, now confirmed
corpus-wide). See [[variables]] §2 for the mechanic; evidence = regenerate the script and
read the `first@` pointer into gitignored `sources/wesnoth/`.

## Families (by the `family()` heuristic — session 001 B3)

| family | prefixes |
|---|---:|
| other/UI | 67 |
| SI number units | 18 |
| **gender/agreement** | **12** |
| add-ons | 9 |
| list grammar | 8 |
| files/storage | 7 |
| system/env | 5 |
| hotkeys | 3 |

> **Gender/agreement family — RESOLVED (was a heuristic gap).** `family()` now folds the
> gender **and** grammatical-agreement variants into one translation-critical family (12
> prefixes): `female`, `male`, `gender`, `female_speaker`, `female_addressed`, `self_female`,
> `race+female`, `friend_is_female`, `friend_is_male`, `addressed_plural`, `plural`,
> `race+plural`. Rationale (Marcin): a translator must be able to trace **all** gender/plural
> tags + mechanics — which forms exist and when the engine selects them. List them with
> `list_context_prefixes.py … --family gender/agreement`.

## Full registry (evidenced, script-generated 2026-07-02)

_Domains abbreviated (`wesnoth-` dropped, bare `wesnoth` → `core`). `n` = entry count.
Rows annotated `(gender)`/`(plural)` in the family column are now folded into the
**gender/agreement** family by `family()` (B3) — the table labels below are pre-B3 and kept
only for the domain evidence; regenerate the script for authoritative families._

| prefix | n | family | domains |
|---|---:|---|---|
| `female` | 245 | gender | core,did,dod,ei,h2tt,help,httt,… |
| `gender` | 3 | gender | lib |
| `male` | 2 | gender | h2tt,units |
| `race` | 50 | other/UI | core,help,utbs |
| `teamname` | 32 | other/UI | anl,did,multiplayer |
| `scenario name` | 29 | other/UI | h2tt,httt |
| `wc_variation` | 24 | other/UI | units |
| `race+female` | 20 | other/UI (gender) | help,utbs |
| `recruit` | 14 | other/UI | sota |
| `campaign_landing` | 11 | other/UI | lib |
| `editor` | 11 | other/UI | help,lib |
| `timespan` | 8 | other/UI | core |
| `whiteboard` | 7 | other/UI | lib |
| `controller` | 6 | other/UI | lib |
| `Multiplayer_AI` | 5 | other/UI | lib |
| `team_name` | 5 | other/UI | tutorial,utbs |
| `vision` | 5 | other/UI | core,lib |
| `whisper` | 5 | other/UI | low,nr |
| `SPECIAL_NOTE` | 4 | other/UI | units,utbs |
| `feature` | 4 | other/UI | lib |
| `race+plural` | 4 | other/UI (plural) | help |
| `stats dialog` | 4 | other/UI | lib |
| `library` | 3 | other/UI | lib |
| `multimenu` | 3 | other/UI | lib |
| `page` | 3 | other/UI | lib |
| `replay` | 3 | other/UI | core |
| `waiting for` | 3 | other/UI | core |
| `Part of 'Units sighted! (...)' sentence` | 2 | other/UI | core |
| `Sapphire of Ice` | 2 | other/UI | wof |
| `addressed_plural` | 2 | other/UI (plural) | sota |
| `date` | 2 | other/UI | lib |
| `female_speaker` | 2 | other/UI (gender) | utbs |
| `game` | 2 | other/UI | lib |
| `holy water` | 2 | other/UI | core |
| `plural` | 2 | other/UI (plural) | sota |
| `prompt` | 2 | other/UI | core |
| `range` | 2 | other/UI | lib |
| `rod of justice` | 2 | other/UI | nr |
| `self_female` | 2 | other/UI (gender) | sota |
| `storm trident` | 2 | other/UI | core |
| `theme` | 2 | other/UI | core,editor |
| `unit_byte` | 2 | other/UI | core,lib |
| `variation` | 2 | other/UI | sotbe |
| `active_modifications`,`attack`,`campaign_abbreviation`,`clipboard`,`color`,`command`,`command_idle` | 1 each | other/UI | core,lib |
| `dialog` | 1 | other/UI | multiplayer |
| `dummy_unit`,`era_or_mod`,`inspector tree item`,`jamming` | 1 each | other/UI | lib,units,core |
| `female_addressed` | 1 | other/UI (gender) | utbs |
| `friend_is_female`,`friend_is_male` | 1 each | other/UI (gender) | tsg |
| `language code for localized resources` | 1 | other/UI | lib |
| `made of`,`no undead`,`river`,`water` | 1 each | other/UI | wc |
| `maximum`,`minimum`,`mp_game_available_slots`,`multiplayer`,`scenario_abbreviation`,`statuspanel`,`time limit`,`weapon` | 1 each | other/UI | core |
| `number of players`,`stats`,`translations`,`unit_variation`,`url` | 1 each | other/UI | lib |
| `quietly` | 1 | other/UI | trow |
| `time of day` | 1 | other/UI | editor |
| `user_team_name` | 1 | other/UI | dw |
| `prefix_atto…zetta` + `infix_binary` | 1 each (18) | SI number units | core |
| `addon_state` | 19 | add-ons | lib |
| `addons_of_type` | 14 | add-ons | lib |
| `addon_type` | 13 | add-ons | core |
| `addon_tag` | 12 | add-ons | lib |
| `addons_order` | 7 | add-ons | lib |
| `addons_view` | 5 | add-ons | lib |
| `addon_dependencies`,`addons`,`addons_server` | 1 each | add-ons | lib |
| `filesystem_path_game` | 4 | files/storage | lib |
| `filesystem`,`filesystem_path_system`,`save_compression`,`save_compression_desc` | 3 each | files/storage | lib,core |
| `cache` | 2 | files/storage | lib |
| `dir_size` | 1 | files/storage | lib |
| `log_level` | 5 | system/env | lib |
| `game_version` | 2 | system/env | lib |
| `cpu_architecture`,`operating_system`,`pixel_scale_multiplier` | 1 each | system/env | lib |
| `conjunct {pair,start,mid,end}` · `disjunct {pair,start,mid,end}` | 1 each (8) | list grammar | lib |
| `editor_hotkeys`,`game_hotkeys`,`mainmenu_hotkeys` | 1 each | hotkeys | lib |

_(Low-count SI/add-on/files/system/list-grammar/hotkey rows collapsed for readability; the
script emits every prefix on its own line with a `first@` evidence pointer.)_
