<!--
Provenance: authored for the Lockit Cartographer project as a content-free, cross-game reference.
It synthesises publicly-documented facts about the Paradox Clausewitz localisation format (folder
layout, encoding, pseudo-YAML dialect) from Paradox's own modding documentation and community wikis;
it contains NO proprietary game strings. Published as an adoption asset under CC-BY-4.0 (see
LICENSE-docs.md). If you extract loc files from a game you own, respect that game's User Agreement /
EULA — for Paradox titles, extraction for personal/portfolio analysis sits within their
modding-friendly, non-commercial stance.
-->

# Lockit Cartographer Field Guide: Extracting Localization Files from Paradox Clausewitz-Engine Games

## TL;DR
- Paradox loc files are loose plain-text `.yml` (UTF-8-BOM) under each game's `localisation/` folder (CK3 and Victoria 3 use American `localization/`); DLC loc is packed inside `dlcNNN.zip` archives in the `dlc/` folder, so any extractor must read both loose files and zip members.
- The format is a Paradox-specific pseudo-YAML (`l_english:` header, `key:VERSION "text"`) that standard YAML parsers cannot handle — use a purpose-built line-regex parser, not PyYAML.
- Language sets differ sharply per game (EU4 ships only 4 languages; Stellaris ships 10, HOI4 9, CK3 7, Victoria 3 11, all including CJK); build a per-game convention library keyed on language set, folder spelling, and formatting dialect.

## Key Findings

1. **On-disk format is loose plain text.** Base-game localisation ships as uncompressed `.yml` files. DLC localisation ships packed inside `dlcNNN.zip` archives — a critical extraction gotcha.
2. **Two YAML dialects across the franchise.** CK2 uses old-style semicolon-delimited CSV; every modern title (EU4, HOI4, Stellaris, CK3, Vic3, EU5) uses the `l_language:` pseudo-YAML.
3. **UTF-8-BOM is mandatory.** The engine rejects plain UTF-8 for some titles; BOM handling is the single most common encoding pitfall.
4. **Language sets vary widely.** EU4 = 4 languages; HOI4 = 9; Stellaris = 10; CK3 = 7; Victoria 3 = 11.
5. **Formatting dialects split into two camps.** EU4/HOI4/Stellaris use `§Y…§!` color codes and `£icon£`; CK3/Vic3 use `#key … #!` formatting and `@icon!` text icons.
6. **Extraction for personal/portfolio analysis sits comfortably within Paradox's modding-friendly stance,** subject to the non-commercial User Agreement.

## Details

### 1. File locations and installation layouts

**Steam on Windows.** Games install under `\steamapps\common\<Game>\`. Localisation folders:
- **Stellaris:** `...\steamapps\common\Stellaris\localisation\` with per-language subfolders (`english/`, `french/`, etc.). British spelling with an `s`.
- **HOI4:** `...\Hearts of Iron IV\localisation\<language>\` (per-language subfolders, e.g. `localisation/english/`). British spelling.
- **EU4:** `...\Europa Universalis IV\localisation\` (loose files; historically flat but subfolders now used). British spelling — per the EU4 Wiki Localisation page, "Localisation must be placed in the 'localisation' folder ('localization' doesn't work)."
- **CK3:** `...\Crusader Kings III\game\localization\<language>\` — American spelling with a `z`, and note the extra `game\` level. The CK3 wiki states: "You must use the US spelling of 'localization'. The Commonwealth spelling of 'localisation' will not work."
- **Victoria 3:** `...\Victoria 3\game\localization\<language>\` — American spelling, `game\` level, plus a `languages.yml` manifest in `game\localization\`.

**Per-game folder differences.** EU4 places files loose (or in `localisation/replace/`); Stellaris/HOI4/CK3/Vic3 use per-language subfolders. All support a `replace/` folder that loads last (LIOS — Last In, Only Served) to override individual keys. Per the Stellaris Wiki, files in the "replace" folder "will load after all other localisation files, and overwrite any duplicate keys ... LIOS (Last in, only served)." CK3 accepts both `localization/replace/english/` and `localization/english/replace/`, with the former taking precedence.

**Linux/macOS (Steam).**
- macOS: `~/Library/Application Support/Steam/steamapps/common/<Game>/` (the `Library` folder is hidden; reach it via Finder → Go → `~/Library/`).
- Linux: `~/.steam/steam/steamapps/common/<Game>/` (also `~/.local/share/Steam/...`).
- User/mod files live under `~/Documents/Paradox Interactive/<Game>/` (Windows) or the equivalent Documents path.

**Xbox / Microsoft Store (Game Pass).** Games install to `C:\Program Files\WindowsApps\` (or an `XboxGames` folder on chosen drives). This folder is the most locked-down location in Windows: attempting to enter it prompts "you'll need permission from SYSTEM/TrustedInstaller." Paradox's own helpdesk advises, for launch issues, to "Go to your Windows Apps folder (typically located in C:\Program Files\WindowsApps)… right click the folder, go to the security tab, click 'Advanced', then change the PRINCIPAL at the top (put in your windows username)." Users widely report that even after taking ownership, child-folder permissions revert to read-only, making reliable file access difficult. Microsoft explicitly recommends against changing WindowsApps permissions ("many users have corrupted their Windows operating system by doing that"). **Practical recommendation for Lockit Cartographer: do not target Game Pass installs.** Acquire the Steam copy for extraction; the loc content is identical and Steam files are loose and readable. If Game Pass is the only option, the files are still plain text (not additionally packed beyond the standard DLC zips), but access requires elevated ownership changes that are fragile and out of scope for an automated pipeline.

**Plain text vs archives (the DLC gotcha).** Base-game loc is loose plain text. DLC content — including its loc `.yml` — is packed inside `.zip` archives:
- Stellaris: `...\Stellaris\dlc\dlc0XX_name\dlcNNN.zip` (plus a `dlcNNN.dlc` text descriptor). Paradox staff (AndrewT) documented: "The .zip file contains the actual data, images or songs; the .dlc file is a simple text file… contains the title of the DLC."
- EU4: `...\Europa Universalis IV\dlc\dlcNNN.zip` (+ `.dlc`).
- CK3: `...\Crusader Kings III\game\dlc\dlcNNN.zip` (+ `dlc_metadata`).
- HOI4: `...\Hearts of Iron IV\dlc\dlcNNN...` — same pattern, **but** with a caveat: much HOI4 DLC script content is shipped loose in base folders and merely ownership-gated at runtime, so some DLC loc strings may sit in the loose base `localisation/` folder rather than inside the zip.

The zip contents are read directly by the engine and are NOT expanded into the base directories: "The contents of the .zip file are not expanded into the vanilla directories… the game must read it right out of the .zip file." **An extractor must therefore enumerate both loose `.yml` files and `.yml` members inside each `dlcNNN.zip`.** Python's `zipfile` handles this natively.

### 2. File format specifics

**The pseudo-YAML dialect.** A modern Paradox loc file looks like:
```
l_english:
 KEY_ONE:0 "Text string one"
 KEY_TWO:1 "Text string two with a \"quote\" inside"
 # this is a comment
```
- First line is the language database header: `l_english:` (lowercase L). Everything below is assigned to that language until another `l_<language>:` header or EOF. A single file may contain multiple language blocks, but the filename must then contain each language.
- Each entry: `key` + `:` + optional integer version + whitespace + double-quoted value.
- **Why standard YAML parsers fail:** the `key:0 "value"` construct (colon immediately followed by a number then a space-separated quoted string, with no YAML-legal mapping syntax) is invalid YAML 1.1/1.2. The version integer, the unquoted-then-quoted structure, and the `§`/`#`/`£`/`@`/`$`/`[]` inline codes all break PyYAML. Do not use PyYAML/ruamel — write a line parser.

**UTF-8 with BOM requirement.** Every modern title requires UTF-8-BOM (the `EF BB BF` byte-order mark). The Stellaris wiki warns "even UTF-8 will fail to be parsed by Stellaris." The HOI4 Wiki warns: "If a language has never been assigned in the file and the file is encoded with UTF-8-BOM and contains a localization key, it might cause a crash with error 0xC0000005(3221225477)." For reading, open files with Python's `encoding="utf-8-sig"` to transparently strip the BOM.

**Filename suffix conventions.** `<name>_l_<language>.yml`. Language codes shipped:

| Internal code | Language | File suffix |
|---|---|---|
| english | English | `_l_english.yml` |
| french | French | `_l_french.yml` |
| german | German | `_l_german.yml` |
| spanish | Spanish (Spain) | `_l_spanish.yml` |
| polish | Polish | `_l_polish.yml` |
| russian | Russian | `_l_russian.yml` |
| braz_por | Brazilian Portuguese | `_l_braz_por.yml` |
| simp_chinese | Simplified Chinese | `_l_simp_chinese.yml` |
| japanese | Japanese | `_l_japanese.yml` |
| korean | Korean | `_l_korean.yml` |
| turkish | Turkish | `_l_turkish.yml` |

**Which languages ship with which game (base game, vanilla):**
- **EU4:** english, german, french, spanish (Spanish-Spain) — 4 only. Per the EU4 Wiki Localisation page, "Vanilla supports the following four languages," and the Steam store confirms these are English, German, French and Spanish.
- **HOI4:** english, french, german, spanish, braz_por, polish, russian, japanese, simp_chinese (9). (Japanese and Simplified Chinese were added after launch.)
- **Stellaris:** 10 languages. Per the Stellaris Wiki "Localisation modding" page: "Supported languages currently include Portuguese (braz_por), English (english), French (french), German (german), Polish (polish), Russian (russian), Spanish (spanish), simplified Chinese (simp_chinese), Japanese (japanese) and Korean (korean)."
- **CK3:** english, french, german, spanish, russian, simp_chinese, korean (7). Confirmed by the official @CrusaderKings account (Aug 10, 2020): "#CK3 will launch with the following languages: English, French, German, Spanish-Spain, Russian, Simplified Chinese & Korean."
- **Victoria 3:** 11 languages. Per the Victoria 3 Steam store listing: "English, French, German, Spanish - Spain, Japanese, Korean, Polish, Portuguese - Brazil, Russian, Simplified Chinese, Turkish."
- **CK2 (legacy):** uses CSV, not YAML (see below).

**Version numbers.** The integer after the colon (`key:0`, `key:1`) is a legacy translation-tracking version used internally by Paradox's translation teams. Per the HOI4 Wiki, "0 is the version number, used for Paradox's internal translation tracking. This is never read in-game, and it can be omitted entirely with no difference in interpretation." The CK3 wiki adds: "This is now completely deprecated." **For extraction, capture it as an optional metadata column but never rely on it.**

**Inline formatting codes — two dialects:**

*Old-style (EU4, HOI4, Stellaris):*
- Color: `§Y…§!` — section sign `§` + single color letter, terminated by `§!`. (Known letters include B, G, H, L, M, P, R, S, T, W, Y.)
- Variables/commands: `$VARIABLE$` (references another key or a game value; color via `$VAL|Y$`), and scope commands in square brackets `[Root.GetName]`, `[GetDateText]`.
- Icons: `£icon£` (Stellaris/EU4 currency/resource icons); HOI4 also uses `@TAG` for flags.
- Escapes: `\"` for a literal quote, `\n` for newline, `\\` for backslash.

*New-style (CK3, Victoria 3):*
- Formatting: `#key … #!` — begins with `#` + a style keyword (e.g. `#bold`, `#N`, `#high`, `#italic`), a mandatory space, then text, terminated by `#!`. Styles can stack (`#darker_white #italic … #!#!`) and combine with semicolons (`#high;bold`).
- Concepts: `[concept_key|E]`, `[Concept('faith','religion')|E]` — game-concept tooltips, typically formatted `|E`.
- Data functions: `[Character.GetName]`, `[SCOPE.GetLocalVariable('x').GetValue]`, with `|` formatting modifiers before the closing bracket (e.g. `|V`, `|LV`, `|=+0`).
- Icons: `@icon!` text icons (defined in `gui/texticons.gui`).
- Nested keys: `$other_key$` still works for key reuse.

EU5 (newest) uses the CK3/Vic3 `#key … #!` style and calls customizable loc only via `Custom('name')`.

**The replace folder and load order.** Files in `localisation/replace/` (or `localisation/<lang>/replace/`) load after all others and override duplicate keys individually (LIOS). Outside `replace/`, load order is generally reverse-alphabetical (Z→A) and base-game files often win on collisions — behavior is inconsistent, so `replace/` is the reliable override. **For extraction, if you want the effective in-game string set, process non-replace files first, then apply `replace/` overrides last.**

### 3. Parsing and extraction tooling

**Existing open-source parsers (assessment for a Python pipeline):**
- **`pyradox` / `pyradox-txt-parser` (Python, PyPI):** the most directly relevant — a Python parser for Paradox `.txt` and `.yml` files with its own YAML parser (not PyYAML) and cp1252 handling. Best off-the-shelf Python starting point, though maintenance is intermittent.
- **`Paradox_localization_utils` (NicolasGrosjean, Python/GitHub):** a mature, actively used toolkit specifically for Paradox loc files (diffing, missing-line detection, duplicate-key detection, Paratranz sync). Excellent reference for edge-case handling and the `get_duplicates_key.py` / `add_missing_lines.py` logic you'll want to replicate.
- **`jomini` (Rust, rakaly/nickbabcock) and its JS/WASM port:** the gold standard for the Clausewitz *save/game* format (EU4/CK3/HOI4/Vic3/EU5/Imperator). Powers Rakaly and pdxu. Overkill for loc `.yml` (loc is a much simpler line format) but authoritative on the broader syntax; the accompanying "A Tour of PDS Clausewitz Syntax" write-up is essential reading for edge cases.
- **`cwtools` (F#):** the engine behind the VSCode/CWTools modding extensions — validation, not extraction; not a fit for a Python data pipeline.
- **`pdxu` / PDX Tools (crschnick):** save-game analysis; not loc-focused.
- **Note:** the PyPI package literally named `paradox` and `pypxlib` are unrelated (they concern the Borland/Corel "Paradox" database format), as is `pxlib`. Do not confuse them.

**Recommendation:** For a Lockit Cartographer Python pipeline, write a small dedicated line-regex parser (loc is line-oriented and trivially parsed) and lean on `Paradox_localization_utils` for cross-language alignment patterns. Reserve `jomini` for any future save-file/game-data work.

**Robust custom Python parser — recipe.** The core regex for a single entry line:
```python
import re
ENTRY = re.compile(
    r'^\s*'                     # optional leading whitespace
    r'([A-Za-z0-9_.\-]+)'       # key (letters, digits, _ . -)
    r':\s*(\d+)?'               # colon + optional version number
    r'\s*"(.*)"\s*'             # space + quoted value (greedy to last quote)
    r'(?:#.*)?$'                # optional trailing comment
)
HEADER = re.compile(r'^\uFEFF?\s*l_([a-z_]+):\s*(?:#.*)?$')
```
Parsing rules to bake in:
- Open with `encoding="utf-8-sig"` to strip the BOM automatically; if that fails, fall back to `cp1252` (older EU4 files / some non-loc text files).
- Track the current language from the most recent `l_<lang>:` header; a file can switch language mid-stream.
- Treat a `#` as a comment **only outside quotes** — do not naïvely split on `#`, because `#` appears inside CK3/Vic3 formatting and inside strings. Prefer matching the full quoted value with the regex above (which consumes everything up to the last quote on the line) rather than hand-splitting.
- Use a greedy `"(.*)"` so escaped inner quotes (`\"`) are retained; then post-process escapes (`\"` → `"`, `\\` → `\`, keep `\n` literal or convert as needed for your downstream use).
- Tolerate malformed lines: log-and-skip rather than abort (real files contain stray lines; the engine itself silently drops from the first bad line — you may want to *warn* rather than replicate that truncation).
- Skip blank lines and full-line comments.
- Optionally strip/normalize inline codes into a separate "clean text" column while preserving the raw value.

**Aligning keys across languages into a table.** Build one dict per language `{key: value}`, then union all keys:
```
key | english | french | german | ... | version | source_file | dlc
```
Handle missing keys as null/empty (common: non-English files lag English). Because Paradox has no fallback, a key present only in English is normal and meaningful — flag it as a translation gap. Emit to CSV/XLSX/Parquet (Parquet recommended for large multi-language sets; preserve UTF-8).

**DLC and patch handling.** Enumerate loose base files first, then iterate `dlc/**/dlcNNN.zip` and read `.yml` members via `zipfile`. Tag each row with its `source_file` and `dlc` origin. Because patches occasionally change formats (e.g., version-number deprecation, new formatting styles, added languages), version-stamp every extraction run with the game build number and keep the parser's regex tolerant of both "with version" and "without version" entries.

### 4. Practical extraction workflow

1. **Locate install.** Resolve the Steam library (parse `libraryfolders.vdf` if automating) → `steamapps\common\<Game>\`. Confirm the loc root: `localisation\` (EU4/HOI4/Stellaris) or `game\localization\` (CK3/Vic3).
2. **Enumerate loc files.** Glob `**/*_l_*.yml` under the loc root (loose) AND `.yml` members inside every `dlc\**\dlcNNN.zip`.
3. **Detect language set.** Parse each filename suffix and each in-file `l_<lang>:` header; reconcile against the expected per-game set (flag surprises).
4. **Parse** each file with the line-regex parser (BOM-aware, comment-safe, malformed-tolerant).
5. **Align** into the tabular key×language dataset; apply `replace/` overrides last if you want effective in-game strings.
6. **Export** to CSV/XLSX/Parquet with metadata columns (version, source_file, dlc, game_build).

**Gotchas checklist:**
- **Duplicate keys:** the same key may appear in multiple files/languages; decide a precedence (replace-folder wins; otherwise last-wins or base-wins — document your choice). Mirror `get_duplicates_key.py` to report collisions.
- **Keys only in some languages:** expected; represent as nulls and count as gaps.
- **Escaped quotes inside strings:** handled by greedy quote matching + escape post-processing.
- **Multi-line edge cases:** modern loc values must be single-line; a value that appears to span lines is almost always a malformed file — log it.
- **Mixed-language files:** a single file can contain several `l_<lang>:` blocks — do not assume one language per file; trust the headers.
- **Mod vs base game:** Workshop mods live under `steamapps\workshop\content\<appid>\<modid>\`; keep them separate from base extraction unless intentionally profiling a mod.
- **CK2 is different:** its loc is semicolon-delimited CSV (`#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x`), one row per key with fixed language columns — needs a separate CSV parser, not the YAML parser.

**Legal / ToS.** Paradox is famously modding-friendly. Its User Agreement grants a license to install and use the games "strictly for non-commercial purposes," and modding is expressly permitted (the former standalone Mod Policy was folded into the User Agreement). Extracting loc files for **personal analysis or a portfolio** is consistent with this: it is non-commercial, does not redistribute the copyrighted text, and does not circumvent DRM (the files are openly readable). **Do not** redistribute the extracted strings as a dataset, bundle them into a commercial product, or ship copyrighted DLC text — the text remains Paradox's IP ("licensed to you, not sold"). For a portfolio, describe the methodology and show aggregate statistics or small illustrative snippets rather than publishing full loc dumps.

### 5. Cross-game convention comparison

| Convention | EU4 | HOI4 | Stellaris | CK3 | Victoria 3 |
|---|---|---|---|---|---|
| Loc folder spelling | `localisation` (s) | `localisation` (s) | `localisation` (s) | `localization` (z) | `localization` (z) |
| Extra `game\` level | No | No | No | Yes | Yes |
| Per-language subfolders | Loose (subfolders now used) | Yes | Yes | Yes | Yes |
| Format | pseudo-YAML | pseudo-YAML | pseudo-YAML | pseudo-YAML | pseudo-YAML |
| Encoding | UTF-8-BOM | UTF-8-BOM | UTF-8-BOM | UTF-8-BOM | UTF-8-BOM |
| Base languages | 4 | 9 | 10 | 7 | 11 |
| CJK shipped | No | Ja, Zh | Ja, Zh, Ko | Zh, Ko | Ja, Zh, Ko |
| Color/format dialect | `§Y…§!` | `§Y…§!` | `§Y…§!` | `#key … #!` | `#key … #!` |
| Icons | `£icon£` | `£icon£`, `@TAG` | `£icon£` | `@icon!` | `@icon!` |
| Concepts | n/a | n/a | n/a | `[concept|E]` | `[concept|E]` |
| Version integer | Yes (deprecated) | Yes (deprecated) | Yes (deprecated) | Yes (deprecated) | Yes (deprecated) |
| Replace folder | Yes | Yes | Yes | Yes | Yes |
| DLC loc storage | `dlcNNN.zip` | `dlcNNN.zip` (+ some loose, gated) | `dlcNNN.zip` | `dlcNNN.zip` | `dlcNNN.zip` |

These are exactly the fields the Lockit Cartographer convention library should record per game+build: folder spelling/path, language set, encoding, formatting dialect, icon syntax, version-integer presence, replace-folder behavior, and DLC packaging.

## Recommendations

1. **Target Steam installs only for extraction.** Loose plain-text files, no permission friction. De-scope Game Pass/WindowsApps (fragile ownership hacks); if a title is Game Pass-only, buy the Steam copy for identical content.
2. **Write one shared line-regex parser** (BOM-aware via `utf-8-sig`, comment-safe, malformed-tolerant) plus a **separate CK2 CSV parser**. Do not attempt PyYAML.
3. **Always enumerate DLC zips** alongside loose files; tag rows with `source_file`, `dlc`, and `game_build`.
4. **Encode conventions as data,** not code: a per-game+build profile (the comparison table fields) that drives the extractor, so new patches/titles are onboarded by adding a profile row.
5. **Version-stamp every run** and diff against the prior build to catch format/language-set changes (new languages, formatting-dialect shifts, version-integer removal).
6. **Stay non-commercial:** analyze and describe; never redistribute full loc dumps.

**Thresholds that change the approach:**
- If a future title ships loc packed in a new archive format (not `.zip`) or binary, add an unpacker stage before parsing.
- If a title drops the version integer entirely or adopts a new formatting dialect, branch the regex/profile rather than mutating the shared parser.
- If profiling mods at scale, add the Workshop path and treat mod `replace/` semantics explicitly.

## Caveats
- **HOI4 DLC storage is partially ambiguous:** some DLC content ships loose in base folders and is ownership-gated at runtime rather than sealed in the DLC zip; the exact loc split was not confirmed from an authoritative Paradox source. Verify empirically per build.
- **Language counts are base-game, launch-era figures** and shift with patches (e.g., HOI4 added Japanese/Simplified Chinese post-launch); always re-detect the language set per build rather than trusting a static list.
- **Color-code letter meanings** (`§H`, `§S`, `§T`, `§W`, etc.) are partly community-reverse-engineered and not fully documented by Paradox; treat any color-letter→RGB mapping as approximate.
- **Load-order/override behavior outside `replace/`** is documented as inconsistent (FIOS vs LIOS varies by content type); rely on `replace/` for deterministic overrides.
- **The `pyradox` package** is intermittently maintained; validate it against current game builds before depending on it, or vendor the parsing logic.
- **EU5** is treated here from its published localization documentation (CK3/Vic3-style `#key … #!` dialect, `Custom()` calls); confirm folder layout and language set against a live install before profiling.