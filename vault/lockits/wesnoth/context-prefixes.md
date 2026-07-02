---
type: lockit-context-prefixes
lockit: wesnoth
updated: 2026-07-02
generated_by: recon script (to be codified in toolkit)
---

# Wesnoth — `^` context-prefix registry

_The set of caret-context prefixes (token before the first `^`). These are **structural identifiers**, not lockit content. Grows as more domains/files are ingested (T4). See [[variables]] §2 for the mechanic; evidence = first `file:line` pointer into gitignored `data/wesnoth/`._

**Subset scope:** 4 textdomains · **105 distinct prefixes** · 350 prefixed entries.

## Families

- **other/UI** — 52 prefixes
- **SI number units** — 18 prefixes
- **add-ons** — 9 prefixes
- **list grammar** — 8 prefixes
- **files/storage** — 7 prefixes
- **system/env** — 5 prefixes
- **gender** — 3 prefixes
- **hotkeys** — 3 prefixes

## Full registry (evidenced)

| prefix | count | family | domains | first @ |
|---|---:|---|---|---|
| `female` | 80 | gender | core,httt,units | wesnoth:3735 |
| `wc_variation` | 24 | other/UI | units | wesnoth-units:6953 |
| `addon_state` | 19 | add-ons | lib | wesnoth-lib:7128 |
| `addons_of_type` | 14 | add-ons | lib | wesnoth-lib:6988 |
| `addon_type` | 13 | add-ons | core | wesnoth:5019 |
| `addon_tag` | 12 | add-ons | lib | wesnoth-lib:7072 |
| `campaign_landing` | 11 | other/UI | lib | wesnoth-lib:2879 |
| `timespan` | 8 | other/UI | core | wesnoth:5536 |
| `addons_order` | 7 | add-ons | lib | wesnoth-lib:7044 |
| `whiteboard` | 7 | other/UI | lib | wesnoth-lib:8717 |
| `controller` | 6 | other/UI | lib | wesnoth-lib:3827 |
| `Multiplayer_AI` | 5 | other/UI | lib | wesnoth-lib:33 |
| `addons_view` | 5 | add-ons | lib | wesnoth-lib:6968 |
| `log_level` | 5 | system/env | lib | wesnoth-lib:5088 |
| `vision` | 5 | other/UI | core,lib | wesnoth-lib:3849 |
| `feature` | 4 | other/UI | lib | wesnoth-lib:6804 |
| `filesystem_path_game` | 4 | files/storage | lib | wesnoth-lib:6828 |
| `stats dialog` | 4 | other/UI | lib | wesnoth-lib:6515 |
| `filesystem` | 3 | files/storage | lib | wesnoth-lib:3245 |
| `filesystem_path_system` | 3 | files/storage | lib | wesnoth-lib:6824 |
| `gender` | 3 | gender | lib | wesnoth-lib:3891 |
| `library` | 3 | other/UI | lib | wesnoth-lib:4598 |
| `multimenu` | 3 | other/UI | lib | wesnoth-lib:8288 |
| `page` | 3 | other/UI | lib | wesnoth-lib:2365 |
| `replay` | 3 | other/UI | core | wesnoth:3866 |
| `save_compression` | 3 | files/storage | core | wesnoth:43 |
| `save_compression_desc` | 3 | files/storage | core | wesnoth:48 |
| `waiting for` | 3 | other/UI | core | wesnoth:4720 |
| `Part of 'Units sighted! (...)' sentence` | 2 | other/UI | core | wesnoth:4787 |
| `cache` | 2 | files/storage | lib | wesnoth-lib:4257 |
| `date` | 2 | other/UI | lib | wesnoth-lib:2620 |
| `game` | 2 | other/UI | lib | wesnoth-lib:3164 |
| `game_version` | 2 | system/env | lib | wesnoth-lib:7595 |
| `holy water` | 2 | other/UI | core | wesnoth:1824 |
| `prompt` | 2 | other/UI | core | wesnoth:6987 |
| `range` | 2 | other/UI | lib | wesnoth-lib:3960 |
| `storm trident` | 2 | other/UI | core | wesnoth:1902 |
| `unit_byte` | 2 | other/UI | core,lib | wesnoth-lib:7556 |
| `SPECIAL_NOTE` | 1 | other/UI | units | wesnoth-units:4286 |
| `active_modifications` | 1 | other/UI | lib | wesnoth-lib:7312 |
| `addon_dependencies` | 1 | add-ons | lib | wesnoth-lib:2703 |
| `addons` | 1 | add-ons | lib | wesnoth-lib:7206 |
| `addons_server` | 1 | add-ons | lib | wesnoth-lib:2569 |
| `attack` | 1 | other/UI | core | wesnoth:4731 |
| `campaign_abbreviation` | 1 | other/UI | core | wesnoth:5829 |
| `clipboard` | 1 | other/UI | lib | wesnoth-lib:3216 |
| `color` | 1 | other/UI | core | wesnoth:3080 |
| `command` | 1 | other/UI | core | wesnoth:6471 |
| `command_idle` | 1 | other/UI | core | wesnoth:6623 |
| `conjunct end` | 1 | list grammar | lib | wesnoth-lib:6885 |
| `conjunct mid` | 1 | list grammar | lib | wesnoth-lib:6880 |
| `conjunct pair` | 1 | list grammar | lib | wesnoth-lib:6870 |
| `conjunct start` | 1 | list grammar | lib | wesnoth-lib:6875 |
| `cpu_architecture` | 1 | system/env | lib | wesnoth-lib:6820 |
| `dir_size` | 1 | files/storage | lib | wesnoth-lib:7552 |
| `disjunct end` | 1 | list grammar | lib | wesnoth-lib:6905 |
| `disjunct mid` | 1 | list grammar | lib | wesnoth-lib:6900 |
| `disjunct pair` | 1 | list grammar | lib | wesnoth-lib:6890 |
| `disjunct start` | 1 | list grammar | lib | wesnoth-lib:6895 |
| `dummy_unit` | 1 | other/UI | units | wesnoth-units:3519 |
| `editor` | 1 | other/UI | lib | wesnoth-lib:778 |
| `editor_hotkeys` | 1 | hotkeys | lib | wesnoth-lib:5993 |
| `era_or_mod` | 1 | other/UI | lib | wesnoth-lib:7836 |
| `game_hotkeys` | 1 | hotkeys | lib | wesnoth-lib:5980 |
| `infix_binary` | 1 | SI number units | core | wesnoth:7854 |
| `inspector tree item` | 1 | other/UI | lib | wesnoth-lib:4696 |
| `jamming` | 1 | other/UI | core | wesnoth:7389 |
| `language code for localized resources` | 1 | other/UI | lib | wesnoth-lib:6856 |
| `mainmenu_hotkeys` | 1 | hotkeys | lib | wesnoth-lib:6006 |
| `male` | 1 | gender | units | wesnoth-units:5667 |
| `maximum` | 1 | other/UI | core | wesnoth:7368 |
| `minimum` | 1 | other/UI | core | wesnoth:7372 |
| `mp_game_available_slots` | 1 | other/UI | core | wesnoth:5848 |
| `multiplayer` | 1 | other/UI | core | wesnoth:5755 |
| `number of players` | 1 | other/UI | lib | wesnoth-lib:7948 |
| `operating_system` | 1 | system/env | lib | wesnoth-lib:6852 |
| `pixel_scale_multiplier` | 1 | system/env | lib | wesnoth-lib:6061 |
| `prefix_atto` | 1 | SI number units | core | wesnoth:7805 |
| `prefix_exa` | 1 | SI number units | core | wesnoth:7842 |
| `prefix_femto` | 1 | SI number units | core | wesnoth:7801 |
| `prefix_giga` | 1 | SI number units | core | wesnoth:7830 |
| `prefix_kibi` | 1 | SI number units | core | wesnoth:7817 |
| `prefix_kilo` | 1 | SI number units | core | wesnoth:7822 |
| `prefix_mega` | 1 | SI number units | core | wesnoth:7826 |
| `prefix_micro` | 1 | SI number units | core | wesnoth:7789 |
| `prefix_milli` | 1 | SI number units | core | wesnoth:7785 |
| `prefix_nano` | 1 | SI number units | core | wesnoth:7793 |
| `prefix_peta` | 1 | SI number units | core | wesnoth:7838 |
| `prefix_pico` | 1 | SI number units | core | wesnoth:7797 |
| `prefix_tera` | 1 | SI number units | core | wesnoth:7834 |
| `prefix_yocto` | 1 | SI number units | core | wesnoth:7813 |
| `prefix_yotta` | 1 | SI number units | core | wesnoth:7850 |
| `prefix_zepto` | 1 | SI number units | core | wesnoth:7809 |
| `prefix_zetta` | 1 | SI number units | core | wesnoth:7846 |
| `race` | 1 | other/UI | core | wesnoth:6288 |
| `scenario name` | 1 | other/UI | httt | wesnoth-httt:518 |
| `scenario_abbreviation` | 1 | other/UI | core | wesnoth:5820 |
| `stats` | 1 | other/UI | lib | wesnoth-lib:8096 |
| `statuspanel` | 1 | other/UI | core | wesnoth:4031 |
| `theme` | 1 | other/UI | core | wesnoth:3986 |
| `time limit` | 1 | other/UI | core | wesnoth:5861 |
| `translations` | 1 | other/UI | lib | wesnoth-lib:2717 |
| `unit_variation` | 1 | other/UI | lib | wesnoth-lib:8172 |
| `url` | 1 | other/UI | lib | wesnoth-lib:7276 |
| `weapon` | 1 | other/UI | core | wesnoth:7482 |
