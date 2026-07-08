#!/usr/bin/env python3
"""extract.py — pull a subset of the lockit as CSV/TSV/JSON, for translation or inspection.

WHY: the whole point of the system is to turn an unknown file into QUERYABLE data. This gives
deterministic, scriptable slices: by namespace, key substring, value shape, or locale — and,
per Marcin's GATE-1 decision (Q4), it EXCLUDES [DEPRECATED] rows by default (opt back in with
--include-deprecated) and reports how many it dropped, so a silent cap never happens. The
`description` context column is emitted as metadata but is never itself a "translation target".

    python3 extract.py [csv] --namespace ui_label
    python3 extract.py [csv] --key-contains offline --format json
    python3 extract.py [csv] --shape array
    python3 extract.py [csv] --namespace credit --locales en,pl --format tsv
    python3 extract.py [csv] --untranslated pl        # rows needing a Polish translation
"""
import sys, csv, io, json
import csv_parse as P


def parse_args(argv):
    a = {'csv': '../../data/a-dark-forest/localization.csv', 'namespace': None,
         'key_contains': None, 'shape': None, 'untranslated': None,
         'locales': None, 'format': 'csv', 'include_deprecated': False}
    i = 0
    while i < len(argv):
        t = argv[i]
        if t == '--namespace': a['namespace'] = argv[i + 1]; i += 2
        elif t == '--key-contains': a['key_contains'] = argv[i + 1]; i += 2
        elif t == '--shape': a['shape'] = argv[i + 1]; i += 2
        elif t == '--untranslated': a['untranslated'] = argv[i + 1]; i += 2
        elif t == '--locales': a['locales'] = argv[i + 1].split(','); i += 2
        elif t == '--format': a['format'] = argv[i + 1]; i += 2
        elif t == '--include-deprecated': a['include_deprecated'] = True; i += 1
        elif not t.startswith('--'): a['csv'] = t; i += 1
        else: raise SystemExit(f"unknown arg {t}")
    return a


def select(lk, a):
    dropped_dep = 0
    out = []
    for r in lk.records:
        if r.is_deprecated and not a['include_deprecated']:
            dropped_dep += 1; continue
        if a['namespace'] and r.namespace != a['namespace']: continue
        if a['key_contains'] and a['key_contains'] not in r.key: continue
        if a['shape'] and r.shape(P.SOURCE) != a['shape']: continue
        if a['untranslated'] and not r.is_untranslated(a['untranslated']): continue
        out.append(r)
    return out, dropped_dep


def emit(lk, rows, a):
    locales = a['locales'] or lk.locales
    cols = ['key', 'description'] + locales
    if a['format'] == 'json':
        data = [dict(key=r.key, description=r.description,
                     **{loc: r.values[loc] for loc in locales}) for r in rows]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        delim = '\t' if a['format'] == 'tsv' else ','
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=delim)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.key, r.description] + [r.values[loc] for loc in locales])
        sys.stdout.write(buf.getvalue())


def main(argv):
    a = parse_args(argv)
    lk = P.parse_file(a['csv'])
    rows, dropped = select(lk, a)
    emit(lk, rows, a)
    msg = f"# {len(rows)} rows"
    if dropped:
        msg += f"  ({dropped} [DEPRECATED] excluded; --include-deprecated to keep)"
    sys.stderr.write(msg + "\n")


if __name__ == '__main__':
    main(sys.argv[1:])
