#!/usr/bin/env python3
"""clausewitz_parse.py — the SINGLE SHARED READER for the HoI4 Clausewitz pseudo-YAML lockit.

======================== WHY THIS EXISTS ========================
Every other script imports this so a `.yml` is opened and interpreted EXACTLY one way.
Paradox loc looks like YAML but is NOT — a standard YAML parser (PyYAML/ruamel) CANNOT read
it and must never be used. It is a LINE format with several traps a naive parser corrupts:

  * Encoding is UTF-8 **with BOM** (EF BB BF). Open with `utf-8-sig` to strip it transparently;
    a plain utf-8 open leaves a stray BOM on the first key and breaks header detection.
  * Each entry is `KEY:[VERSION] "VALUE"`. The `:0 "text"` shape (colon, optional integer,
    space, quoted string) is exactly what makes it invalid YAML — parse it with ONE regex.
  * The VERSION integer is optional, deprecated metadata (a revision counter, values {0..4};
    GATE 1 proved no key ever carries two different values → it is NOT a variant selector).
    Capture it but NEVER use it as identity.
  * VALUES contain UNESCAPED inner double-quotes (dialogue: ""A Somber Duty""). HoI4 does NOT
    use \\" here. So we extract with a GREEDY first-quote → LAST-quote match: the outer pair is
    stripped, inner quotes are preserved losslessly. A "first close-quote wins" parser would
    TRUNCATE these — that is the single most important design choice in this file.
  * `#` is a comment ONLY outside quotes. Never hand-split a line on `#` or `,`; the regex
    consumes the whole quoted value first, so a trailing `# comment` after the value is ignored.
    (Assumption, true on this corpus: a trailing comment does not itself contain a `"`. Verified
    0 malformed on the slice; the `--audit`/validate tools re-check at scale.)
  * A file begins with an `l_<lang>:` header and every entry belongs to the current language;
    a single file MAY switch language mid-stream, so we track the active header, not the filename.
  * Malformed / apparently multi-line lines are LOG-AND-SKIPPED (collected as warnings), never
    silently dropped — the engine truncates from the first bad line, but we want to SEE them.

Anatomy: vault/lockits/hoi4/{profile,variables,structure}.md — confirmed with Marcin at GATE 1
(2026-07-09). This docstring is the plain-language explanation a weaker model can reproduce from.

Run standalone for a per-file census self-check:
    python3 clausewitz_parse.py ../../data/hoi4/en/events_l_english.yml
    python3 clausewitz_parse.py ../../data/hoi4/en          # a directory = all *.yml in it
"""
import re, os, sys, glob, collections

# The one entry regex (field guide; verified 100% match on the GATE-0 slice).
ENTRY  = re.compile(r'^(\s*)([A-Za-z0-9_.\-]+):\s*(\d+)?\s*"(.*)"\s*(?:#.*)?$')
HEADER = re.compile(r'^\s*l_([a-z_]+):\s*(?:#.*)?$')
BLANK  = re.compile(r'^\s*$')
COMMENT = re.compile(r'^\s*#')


class Entry:
    """One loc entry. `value` keeps inner quotes raw; `version` is int or None."""
    __slots__ = ('key', 'version', 'value', 'lang', 'source_file', 'line')

    def __init__(self, key, version, value, lang, source_file, line):
        self.key = key
        self.version = version          # int or None (optional deprecated revision counter)
        self.value = value              # raw string, outer quotes already stripped
        self.lang = lang                # e.g. 'english' (from the active l_<lang>: header)
        self.source_file = source_file
        self.line = line                # 1-based line number in its file

    # --- key style (GATE 1: two styles) -----------------------------------------
    @property
    def is_dotted(self):
        """Dotted event key namespace.id.part (has a '.' and a numeric id segment)."""
        return '.' in self.key and any(seg.isdigit() for seg in self.key.split('.'))

    @property
    def namespace(self):
        """For dotted event keys: the leading namespace before the first numeric id."""
        if '.' not in self.key:
            return ''
        segs = self.key.split('.')
        head = []
        for s in segs:
            if s.isdigit():
                break
            head.append(s)
        return '.'.join(head)

    @property
    def event_id(self):
        """For dotted event keys: the numeric id segment (str) or ''."""
        for s in self.key.split('.'):
            if s.isdigit():
                return s
        return ''

    @property
    def part(self):
        """For dotted event keys: the trailing part after the numeric id (t/d/desc/a/...)."""
        segs = self.key.split('.')
        for i, s in enumerate(segs):
            if s.isdigit():
                return '.'.join(segs[i + 1:])
        return ''

    @property
    def tag(self):
        """For underscore keys: a leading 3-letter UPPER country tag if present, else ''."""
        m = re.match(r'^([A-Z]{3})(?:_|$)', self.key)
        return m.group(1) if m else ''

    @property
    def is_empty(self):
        return self.value == ''


class Lockit:
    """Parsed entries from one or many files, plus the warnings collected while parsing."""
    def __init__(self, entries, warnings, files):
        self.entries = entries
        self.warnings = warnings        # list of (file, line, kind, text) for malformed/multi-line
        self.files = files

    @property
    def langs(self):
        return sorted({e.lang for e in self.entries})

    def by_key(self):
        d = collections.OrderedDict()
        for e in self.entries:
            d.setdefault(e.key, []).append(e)
        return d

    def duplicate_keys(self):
        """{key: [entries]} for keys occurring >1x (within/across files — override candidates)."""
        return {k: v for k, v in self.by_key().items() if len(v) > 1}


def parse_file(path):
    """Parse ONE .yml. Returns (entries, warnings). Never raises on a bad line — log-and-skip."""
    entries, warnings = [], []
    lang = None
    with open(path, encoding='utf-8-sig') as fh:
        for i, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            if BLANK.match(line):
                continue
            h = HEADER.match(line)
            if h:
                lang = h.group(1)
                continue
            if COMMENT.match(line):
                continue
            m = ENTRY.match(line)
            if not m:
                # odd number of quotes ⇒ likely an unterminated/multi-line value; else malformed
                kind = 'multiline?' if line.count('"') % 2 == 1 else 'malformed'
                warnings.append((path, i, kind, line[:80]))
                continue
            _indent, key, ver, val = m.groups()
            entries.append(Entry(key, int(ver) if ver is not None else None,
                                 val, lang or '?', path, i))
    return entries, warnings


def parse_files(paths):
    """Parse many .yml into one Lockit (used for the 206-file scale-up)."""
    all_entries, all_warn, files = [], [], []
    for p in paths:
        e, w = parse_file(p)
        all_entries.extend(e); all_warn.extend(w); files.append(p)
    return Lockit(all_entries, all_warn, files)


def resolve_paths(arg):
    """A file → [file]; a directory → sorted *.yml within it."""
    if os.path.isdir(arg):
        return sorted(glob.glob(os.path.join(arg, '*.yml')))
    return [arg]


def load(arg):
    """Convenience: path-or-dir → Lockit."""
    return parse_files(resolve_paths(arg))


def _census(arg):
    lk = load(arg)
    dups = lk.duplicate_keys()
    ver = collections.Counter(e.version for e in lk.entries if e.version is not None)
    dotted = sum(1 for e in lk.entries if e.is_dotted)
    print(f"path         {arg}")
    print(f"files        {len(lk.files)}")
    print(f"langs        {lk.langs}")
    print(f"entries      {len(lk.entries)}")
    print(f"unique keys  {len(lk.by_key())}   duplicate keys {len(dups)}")
    print(f"key styles   dotted-event={dotted}  underscore={len(lk.entries) - dotted}")
    print(f"version :N   {dict(sorted(ver.items()))}  (optional revision counter)")
    print(f"empty values {sum(1 for e in lk.entries if e.is_empty)}")
    print(f"warnings     {len(lk.warnings)} (malformed/multiline — see validate.py)")


if __name__ == '__main__':
    _census(sys.argv[1] if len(sys.argv) > 1 else '../../data/hoi4/en')
