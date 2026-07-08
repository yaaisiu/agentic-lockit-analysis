#!/usr/bin/env python3
"""csv_parse_template.py — reusable dependency-free reader for a tabular key+locale CSV lockit.

PURPOSE
    Read a "one row per string, one column per locale" localisation table (CSV/TSV) into typed
    records, correctly and once, so every downstream tool shares one interpretation of the file.

THE WHY (plain language, for a less-capable agent to follow and reproduce)
    A translation CSV looks trivial but has traps that naive `line.split(',')` corrupts:
      * cells contain commas and doubled-quotes → you MUST use Python's `csv` module (RFC-4180),
        never hand-split. A rectangular table (every row == header width) is an invariant; a
        ragged row means the column assumptions are wrong → fail loudly, don't guess.
      * some columns are METADATA (a context/description/comment column), NOT locales — separate
        them up front so a "text to translate" pass never leaks context into the output.
      * a cell value has one of three SHAPES: scalar string, a JSON-ARRAY literal (a multi-value
        cell like ["Yes","No"] — parse it, don't regex), or EMPTY. Classify once here so tools
        just branch on shape.
      * the key column is NOT guaranteed unique — keep EVERY row and expose duplicates (a dup is
        usually a dead upstream row to flag, not fix).

    EMBODIES: convention [[csv-tabular]] · detected by heuristic [[csv-detection]] · constructs
    get labeled via [[construct-origin-labeling]]. first_seen: a-dark-forest (session 003).

HOW TO PARAMETERISE (adapt per lockit)
    * META_COLS   — the non-locale column names (e.g. ('key','description') or ('id','comment')).
      Everything in the header not in META_COLS is treated as a locale.
    * KEY_COL     — the identity column name (default 'key').
    * SOURCE      — the source-locale column name (default 'en'); used by cross-locale checks.
    * DELIM       — ',' for CSV, '\t' for TSV (or sniff).
    * EMPTY_MARK  — if the lockit marks intentional blanks with a tag in a context column
      (e.g. '[EMPTY]'), set it so is_untranslated() can tell intentional from untranslated.
    Add project constructs (namespace split, context-column tag DSL, key templates) in a
    separate labels module, not here — keep this reader format-general.
"""
import csv, io, json, sys, collections

# ---- parameterise these per lockit ----
META_COLS = ('key', 'description')
KEY_COL = 'key'
CONTEXT_COL = 'description'      # or None if the lockit has no context column
SOURCE = 'en'
DELIM = ','
EMPTY_MARK = '[EMPTY]'          # marker (in the context col) for an intentional blank; or None
# ---------------------------------------

SCALAR, ARRAY, EMPTY = 'scalar', 'array', 'empty'


def value_shape(v):
    s = v.strip()
    if s == '':
        return EMPTY
    if s.startswith('[') and s.endswith(']'):
        try:
            if isinstance(json.loads(s), list):
                return ARRAY
        except ValueError:
            pass
    return SCALAR


def array_elements(v):
    return json.loads(v.strip()) if value_shape(v) == ARRAY else None


class Record:
    __slots__ = ('key', 'context', 'values', 'row')

    def __init__(self, key, context, values, row):
        self.key, self.context, self.values, self.row = key, context, values, row

    @property
    def namespace(self):        # project convention: prefix before first ':' (adapt as needed)
        return self.key.split(':', 1)[0] if ':' in self.key else ''

    def shape(self, locale):
        return value_shape(self.values.get(locale, ''))

    def elements(self, locale):
        return array_elements(self.values.get(locale, ''))

    @property
    def is_marked_empty(self):
        return EMPTY_MARK is not None and EMPTY_MARK in (self.context or '')

    def is_untranslated(self, locale):
        return (self.values.get(locale, '').strip() == ''
                and not self.is_marked_empty
                and self.values.get(SOURCE, '').strip() != '')


class Lockit:
    def __init__(self, header, records, path):
        self.header, self.records, self.path = header, records, path
        self.locales = [c for c in header if c not in META_COLS]

    def duplicate_keys(self):
        seen = collections.OrderedDict()
        for r in self.records:
            seen.setdefault(r.key, []).append(r)
        return {k: v for k, v in seen.items() if len(v) > 1}


def parse_file(path, delim=DELIM):
    raw = open(path, 'rb').read()
    if raw[:3] == b'\xef\xbb\xbf':
        raw = raw[3:]                      # tolerate a UTF-8 BOM
    rows = list(csv.reader(io.StringIO(raw.decode('utf-8')), delimiter=delim))
    if not rows:
        raise ValueError(f"{path}: empty file")
    header = rows[0]
    if KEY_COL not in header:
        raise ValueError(f"{path}: no '{KEY_COL}' column; header={header}")
    idx = {c: i for i, c in enumerate(header)}
    width = len(header)
    records = []
    for n, row in enumerate(rows[1:], start=2):
        if len(row) != width:
            raise ValueError(f"{path}:{n}: ragged row ({len(row)} != {width})")
        values = {c: row[idx[c]] for c in header if c not in META_COLS}
        ctx = row[idx[CONTEXT_COL]] if CONTEXT_COL in idx else ''
        records.append(Record(row[idx[KEY_COL]], ctx, values, n))
    return Lockit(header, records, path)


if __name__ == '__main__':
    lk = parse_file(sys.argv[1])
    shapes = collections.Counter(lk.__class__ and r.shape(loc)
                                 for r in lk.records for loc in lk.locales)
    print(f"records {len(lk.records)} · locales {lk.locales} · "
          f"unique keys {len(set(r.key for r in lk.records))} · "
          f"dups {list(lk.duplicate_keys())} · shapes {dict(shapes)}")
