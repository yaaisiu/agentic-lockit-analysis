#!/usr/bin/env python3
"""clausewitz_parse_template.py — reusable dependency-free reader for a Paradox Clausewitz
pseudo-YAML lockit (EU4 / HoI4 / Stellaris / CK3 / Victoria 3 / EU5).

PURPOSE
    Read Paradox loc `.yml` (`l_<lang>:` header + `KEY:[VERSION] "VALUE"` lines) into typed
    entries, correctly and once, so every downstream tool shares one interpretation.

THE WHY (plain language, for a less-capable agent to follow and reproduce)
    It LOOKS like YAML but is NOT — a standard YAML parser (PyYAML/ruamel) cannot read it and
    must never be used. It is a LINE format with traps:
      * UTF-8 **with BOM** → open with `utf-8-sig` (a plain utf-8 open leaves a BOM on the first
        key and breaks header detection).
      * `KEY:0 "value"` (colon, optional integer, space, quoted string) is exactly what makes it
        invalid YAML → parse each line with ONE regex.
      * the VERSION integer is optional, deprecated metadata (a revision counter) — capture it,
        NEVER use it as identity or as a selector.
      * VALUES contain UNESCAPED inner double-quotes (dialogue). So extract with a GREEDY
        first-quote → LAST-quote match: strip the outer pair, keep inner quotes. A "first
        close-quote wins" parser TRUNCATES these — the single most important design choice here.
      * `#` is a comment ONLY outside quotes → never hand-split on `#` or `,`; the regex consumes
        the whole quoted value first.
      * a file begins with `l_<lang>:` and MAY switch language mid-stream → track the active
        header, not the filename.
      * malformed / apparently multi-line lines → LOG-AND-SKIP (collect warnings), never silently
        drop (the engine truncates from the first bad line; we'd rather SEE it).

    EMBODIES: convention [[clausewitz-pdx-yaml]] · detected by [[clausewitz-detection]] · label
    the dialect constructs via [[construct-origin-labeling]]. first_seen: hoi4 (session 004).

HOW TO PARAMETERISE (adapt per game/dialect)
    * The ENTRY/HEADER regexes below are game-independent (verified on HoI4). Keep them.
    * Dialect + project constructs (colour `§X`/`#key`, icons `£`/`@icon!`, `$VAR|fmt$`,
      `[scope.fn]`, key styles, colour-letter set) belong in a SEPARATE labels module per lockit,
      NOT here — keep this reader format-general.
    * For a full install, also enumerate `.yml` members inside `dlc/**/dlcNNN.zip` (zipfile) and
      apply `replace/`-folder overrides last if you want the effective in-game string set.
"""
import re, os, sys, glob, collections

ENTRY   = re.compile(r'^(\s*)([A-Za-z0-9_.\-]+):\s*(\d+)?\s*"(.*)"\s*(?:#.*)?$')
HEADER  = re.compile(r'^\s*l_([a-z_]+):\s*(?:#.*)?$')
BLANK   = re.compile(r'^\s*$')
COMMENT = re.compile(r'^\s*#')


class Entry:
    __slots__ = ('key', 'version', 'value', 'lang', 'source_file', 'line')

    def __init__(self, key, version, value, lang, source_file, line):
        self.key, self.version, self.value = key, version, value
        self.lang, self.source_file, self.line = lang, source_file, line

    @property
    def is_empty(self):
        return self.value == ''


class Lockit:
    def __init__(self, entries, warnings, files):
        self.entries, self.warnings, self.files = entries, warnings, files

    @property
    def langs(self):
        return sorted({e.lang for e in self.entries})

    def by_key(self):
        d = collections.OrderedDict()
        for e in self.entries:
            d.setdefault(e.key, []).append(e)
        return d

    def duplicate_keys(self):
        return {k: v for k, v in self.by_key().items() if len(v) > 1}


def parse_file(path):
    """Parse ONE .yml. Never raises on a bad line — log-and-skip into `warnings`."""
    entries, warnings, lang = [], [], None
    with open(path, encoding='utf-8-sig') as fh:
        for i, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            if BLANK.match(line):
                continue
            h = HEADER.match(line)
            if h:
                lang = h.group(1); continue
            if COMMENT.match(line):
                continue
            m = ENTRY.match(line)
            if not m:
                kind = 'multiline?' if line.count('"') % 2 == 1 else 'malformed'
                warnings.append((path, i, kind, line[:80])); continue
            _indent, key, ver, val = m.groups()
            entries.append(Entry(key, int(ver) if ver is not None else None,
                                 val, lang or '?', path, i))
    return entries, warnings


def load(arg):
    """path-or-dir → Lockit (dir = all *.yml within, for a whole-corpus run)."""
    paths = sorted(glob.glob(os.path.join(arg, '*.yml'))) if os.path.isdir(arg) else [arg]
    all_e, all_w, files = [], [], []
    for p in paths:
        e, w = parse_file(p)
        all_e.extend(e); all_w.extend(w); files.append(p)
    return Lockit(all_e, all_w, files)


if __name__ == '__main__':
    lk = load(sys.argv[1] if len(sys.argv) > 1 else '.')
    ver = collections.Counter(e.version for e in lk.entries if e.version is not None)
    print(f"files {len(lk.files)} · langs {lk.langs} · entries {len(lk.entries)} · "
          f"unique keys {len(lk.by_key())} · dups {len(lk.duplicate_keys())} · "
          f"version:N {dict(sorted(ver.items()))} · warnings {len(lk.warnings)}")
