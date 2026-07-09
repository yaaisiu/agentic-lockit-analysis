#!/usr/bin/env python3
"""completeness.py — translation completeness report for Wesnoth gettext .po files.

======================== WHY THIS EXISTS ========================
Profiling mapped the English SOURCE (the `.pot` templates). But the question a loc manager asks is
"how DONE is each language?" — which needs the translations (`.po`), where each entry carries a
`msgstr`. This reports, per domain and per language, the honest split:

  * translated   — every msgstr form is non-empty AND the entry is not fuzzy
  * untranslated — the msgstr is empty (translator hasn't reached it)
  * fuzzy        — flagged `#, fuzzy` (a machine/heuristic guess awaiting human confirmation;
                   gettext does NOT use fuzzy strings in-game, so fuzzy ≠ done)

Why the fuzzy split matters: counting fuzzy as "translated" overstates completeness — fuzzy
entries are exactly the ones a reviewer must revisit. A plural entry counts as translated only if
ALL its plural forms are filled (a half-filled plural renders empty for some counts).

Uses the shared reader po_parse.py (identity + msgstr/flags). No deps. Point it at a .po file, or
a directory of them (e.g. one language's domains). first_seen: wesnoth (session 004).

    python3 completeness.py ../../data/wesnoth/po/pl            # all domains for Polish
    python3 completeness.py ../../data/wesnoth/po/pl/wesnoth.po # one domain
"""
import sys, os, glob, collections
import po_parse as PO


def entry_state(rec):
    """'fuzzy' | 'untranslated' | 'translated' for one non-header entry."""
    if 'fuzzy' in rec.get('flags', []):
        return 'fuzzy'
    forms = rec['msgstr'] or ['']
    # untranslated iff every form is empty; translated iff every form is non-empty
    if all(f == '' for f in forms):
        return 'untranslated'
    if any(f == '' for f in forms):
        return 'untranslated'          # a partially-filled plural is not usable → not done
    return 'translated'


def report_file(path):
    recs = PO.strings(PO.parse_file(path))
    c = collections.Counter(entry_state(r) for r in recs)
    total = sum(c.values())
    return total, c


def report(arg):
    paths = sorted(glob.glob(os.path.join(arg, '*.po'))) if os.path.isdir(arg) else [arg]
    print(f"TRANSLATION COMPLETENESS — {arg}\n")
    print(f"{'domain':<20} {'total':>7} {'transl':>7} {'fuzzy':>6} {'untrans':>8} {'% done':>7}")
    gt = collections.Counter(); grand = 0
    for p in paths:
        total, c = report_file(p)
        grand += total; gt.update(c)
        pct = 100.0 * c['translated'] / total if total else 0.0
        print(f"{os.path.basename(p):<20} {total:>7} {c['translated']:>7} {c['fuzzy']:>6} "
              f"{c['untranslated']:>8} {pct:>6.1f}%")
    if len(paths) > 1:
        pct = 100.0 * gt['translated'] / grand if grand else 0.0
        print(f"{'— ALL —':<20} {grand:>7} {gt['translated']:>7} {gt['fuzzy']:>6} "
              f"{gt['untranslated']:>8} {pct:>6.1f}%")
    print("\n(fuzzy = machine/heuristic guess, NOT in-game — counts as NOT done; a plural is done"
          " only when every form is filled. surface, don't fix — upstream GPL data.)")


if __name__ == '__main__':
    report(sys.argv[1] if len(sys.argv) > 1 else '../../data/wesnoth/po/pl')
