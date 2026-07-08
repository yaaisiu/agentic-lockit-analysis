#!/usr/bin/env python3
"""csv_parse.py — core reader for the A Dark Forest Godot-CSV lockit.

======================== WHY THIS EXISTS ========================
This is the SINGLE SHARED READER every other script imports, so the file is opened and
interpreted exactly one way. A Godot translation CSV looks trivial ("just a table"), but
this one carries several traps that ad-hoc `line.split(',')` would silently corrupt:

  * cells contain commas and doubled-quotes (631 comma-cells / 287 quote-cells) → you MUST
    use the real `csv` module, which handles RFC-4180 quoting. We never hand-split.
  * column 1 `description` is NOT a locale — it's translator context (excluded from any
    "text to translate" output). We separate meta columns from locale columns up front.
  * a value can be one of three SHAPES: a scalar string, a JSON-array literal (a multi-value
    cell like ["Yes","No"] — 30 keys / 207 cells), or intentionally EMPTY. Downstream tools
    must branch on shape, so we classify it here once.
  * `key` is `namespace:name` and is NOT guaranteed unique (`ui_label:heart` is duplicated).
    We keep EVERY row (never dedupe silently) and expose duplicates so a tool can flag them.

Anatomy is documented in vault/lockits/a-dark-forest/{profile,variables,structure}.md and was
confirmed with Marcin at GATE 1 (2026-07-07). This docstring is the human explanation a weaker
model can follow to reproduce the reader.

Run standalone for a census self-check:
    python3 csv_parse.py ../../data/a-dark-forest/localization.csv
"""
import csv, io, json, sys, collections

META_COLS = ('key', 'description')     # everything else in the header is a locale
SOURCE = 'en'                          # source locale (English); the rest are translations

# value shapes
SCALAR, ARRAY, EMPTY = 'scalar', 'array', 'empty'

# the closed description-tag vocabulary (see labels.py; drift audit flags anything else)
DESC_TAGS = ('EMPTY', 'noun', 'verb', 'DEPRECATED')


def value_shape(v):
    """Classify a raw cell value into SCALAR | ARRAY | EMPTY (see WHY above)."""
    s = v.strip()
    if s == '':
        return EMPTY
    if s.startswith('[') and s.endswith(']'):
        try:
            if isinstance(json.loads(s), list):
                return ARRAY
        except (ValueError, json.JSONDecodeError):
            pass   # a stray '[...]' that isn't JSON is treated as scalar prose
    return SCALAR


def array_elements(v):
    """Return the list of elements for an ARRAY cell, else None. Parse — never regex."""
    if value_shape(v) != ARRAY:
        return None
    return json.loads(v.strip())


def desc_tags(description):
    """The [TAG] tokens present in a description cell, as a list (order preserved)."""
    out = []
    i = 0
    d = description
    # tags appear as leading [TAG] tokens; scan all bracket tokens and keep known/unknown alike
    import re
    for m in re.findall(r'\[([^\]]+)\]', d):
        out.append(m)
    return out


class Record:
    """One CSV row. `values` maps locale -> raw string. Meta (key/description) split out."""
    __slots__ = ('key', 'description', 'values', 'row')

    def __init__(self, key, description, values, row):
        self.key = key
        self.description = description
        self.values = values          # dict: locale -> raw string
        self.row = row                # 1-based row number in the file (header = row 1)

    # --- key structure ---
    @property
    def namespace(self):
        return self.key.split(':', 1)[0] if ':' in self.key else ''

    @property
    def name(self):
        return self.key.split(':', 1)[1] if ':' in self.key else self.key

    # --- description / status ---
    @property
    def tags(self):
        return desc_tags(self.description)

    @property
    def is_deprecated(self):
        return 'DEPRECATED' in self.tags

    @property
    def is_marked_empty(self):
        return 'EMPTY' in self.tags

    # --- values ---
    def shape(self, locale):
        return value_shape(self.values.get(locale, ''))

    def elements(self, locale):
        return array_elements(self.values.get(locale, ''))

    def is_untranslated(self, locale):
        """Blank in this locale but present in source and not intentionally empty."""
        return (self.values.get(locale, '').strip() == ''
                and not self.is_marked_empty
                and self.values.get(SOURCE, '').strip() != '')


class Lockit:
    """The parsed CSV: header, records, locale list, and duplicate-key info."""
    def __init__(self, header, records, path):
        self.header = header
        self.records = records
        self.path = path
        self.locales = [c for c in header if c not in META_COLS]

    def by_namespace(self):
        d = collections.OrderedDict()
        for r in self.records:
            d.setdefault(r.namespace, []).append(r)
        return d

    def duplicate_keys(self):
        """-> {key: [records]} for keys that occur more than once (identity is not unique)."""
        seen = collections.OrderedDict()
        for r in self.records:
            seen.setdefault(r.key, []).append(r)
        return {k: v for k, v in seen.items() if len(v) > 1}


def parse_file(path):
    """Read a Godot translation CSV into a Lockit. Fails loudly on a ragged (non-rectangular)
    table — that would mean our column assumptions are wrong and every downstream index is off.
    """
    raw = open(path, 'rb').read()
    if raw[:3] == b'\xef\xbb\xbf':
        raw = raw[3:]                 # tolerate a UTF-8 BOM (this file has none, but be safe)
    text = raw.decode('utf-8')
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        raise ValueError(f"{path}: empty file")
    header = rows[0]
    for name in META_COLS:
        if name not in header:
            raise ValueError(f"{path}: expected a '{name}' column; header={header}")
    idx = {c: i for i, c in enumerate(header)}
    width = len(header)
    records = []
    for n, row in enumerate(rows[1:], start=2):    # row 2 = first data row
        if len(row) != width:
            raise ValueError(f"{path}:{n}: ragged row ({len(row)} fields, expected {width})")
        values = {c: row[idx[c]] for c in header if c not in META_COLS}
        records.append(Record(row[idx['key']], row[idx['description']], values, n))
    return Lockit(header, records, path)


def _census(path):
    lk = parse_file(path)
    shapes = collections.Counter()
    for r in lk.records:
        for loc in lk.locales:
            shapes[r.shape(loc)] += 1
    dups = lk.duplicate_keys()
    print(f"file           {path}")
    print(f"locales        {lk.locales}  (source={SOURCE})")
    print(f"records        {len(lk.records)}")
    print(f"unique keys    {len(set(r.key for r in lk.records))}")
    print(f"duplicate keys {len(dups)}  {list(dups)}")
    print(f"namespaces     {len(lk.by_namespace())}")
    print(f"value shapes   {dict(shapes)}  (over records×locales)")
    print(f"deprecated     {sum(1 for r in lk.records if r.is_deprecated)}")
    print(f"marked [EMPTY] {sum(1 for r in lk.records if r.is_marked_empty)}")


if __name__ == '__main__':
    _census(sys.argv[1] if len(sys.argv) > 1
            else '../../data/a-dark-forest/localization.csv')
