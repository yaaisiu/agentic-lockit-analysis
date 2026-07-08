#!/usr/bin/env python3
"""validate.py — single-file STRUCTURAL check of the lockit (not translation quality).

WHY: catch the file-integrity defects that make downstream extraction wrong or that signal an
upstream data bug — BEFORE anyone translates. Each check maps to a GATE-1 fact:
  * rectangular table (parse_file already errors on ragged rows) — re-affirmed here.
  * duplicate keys (identity is not unique; ui_label:heart) → ERROR (report, don't fix).
  * every array cell is valid JSON (a broken '[...]' would silently become scalar) → ERROR.
  * [EMPTY]-marked rows really are blank in ALL locales → else the marker lies → WARN.
  * a blank cell that is NOT [EMPTY] and has a source value = untranslated → WARN (per locale).
  * description tag vocabulary is the known closed set → unknown tag = drift ERROR.
Severity: structural/identity problems are ERROR; completeness gaps are WARN (a partially
translated locale like `ua` is expected, not broken).

    python3 validate.py [csv] [--warn]     # --warn also prints untranslated-cell warnings
"""
import sys, collections
import csv_parse as P
import labels as L


def main(argv):
    path = '../../data/a-dark-forest/localization.csv'
    show_warn = False
    for t in argv:
        if t == '--warn': show_warn = True
        elif not t.startswith('--'): path = t
    lk = P.parse_file(path)        # raises on ragged/broken CSV
    errors, warns = [], []

    # duplicate keys
    for k, rs in lk.duplicate_keys().items():
        errors.append(f"duplicate key {k!r} at rows {[r.row for r in rs]} (upstream bug; report)")

    # array validity + [EMPTY] consistency + tag vocabulary
    for r in lk.records:
        for tag in r.tags:
            if L.label_desc_tag(tag)[1] == L.UNKNOWN:
                errors.append(f"row {r.row} {r.key}: unknown description tag [{tag}]")
        # an array-looking cell that failed to parse classifies as scalar → malformed JSON.
        # match on a leading '[' (not also a trailing ']') so we catch stray-comma corruption
        # like `["?"],` (a real upstream defect seen in the es column).
        for loc in lk.locales:
            v = r.values[loc].strip()
            if v.startswith('[') and r.shape(loc) != P.ARRAY:
                errors.append(f"row {r.row} {r.key}/{loc}: '[...]'-looking value is not valid JSON ({v[:30]!r})")
        if r.is_marked_empty:
            nonblank = [loc for loc in lk.locales if r.values[loc].strip() != '']
            if nonblank:
                warns.append(f"row {r.row} {r.key}: marked [EMPTY] but non-blank in {nonblank}")

    # untranslated cells (completeness) — WARN, grouped per locale
    untrans = collections.Counter()
    for r in lk.records:
        for loc in lk.locales:
            if r.is_untranslated(loc):
                untrans[loc] += 1

    print(f"# validate {path}")
    print(f"ERRORS: {len(errors)}")
    for e in errors: print(f"  ERROR {e}")
    print(f"WARNINGS (structural): {len(warns)}")
    for w in warns: print(f"  WARN  {w}")
    print("\n# untranslated cells per locale (completeness — expected, not a defect):")
    for loc in lk.locales:
        print(f"  {loc:<4} {untrans.get(loc, 0)}")
    if show_warn:
        print("\n# untranslated detail (--warn):")
        for r in lk.records:
            miss = [loc for loc in lk.locales if r.is_untranslated(loc)]
            if miss:
                print(f"  row {r.row} {r.key}: missing {miss}")

    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
