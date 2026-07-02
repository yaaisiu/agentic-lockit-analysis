#!/usr/bin/env python3
# scripts/wesnoth/report.py
# source: profile wesnoth (GATE 1) — the "what we know / what we don't" coverage report.
"""
WHY (Marcin's request): once the lockit is queryable we want to REVIEW what we know, confirm
what's stored in the profile, and surface anything we might have missed. This produces a
single deterministic snapshot you read against vault/lockits/wesnoth/profile.md — same
numbers ⇒ profile still true; new numbers ⇒ something changed or a new file added signal.

It reports: totals & identity uniqueness, per-domain shape, token-class coverage, plural &
flag counts, comment composition, ^-prefix families, and a GAPS section (unknown angle
tokens, entries with neither ^ nor #.id, previous-msgid/fuzzy presence) — the "unknowns".

Usage:  python report.py <file...> [--json]
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from po_parse import parse_file, strings
import po_tokens
from list_context_prefixes import family


def build(paths):
    rep = {"files": paths, "per_domain": {}, "totals": {}, "tokens": {}, "prefix_families": {},
           "plural": 0, "flags": collections.Counter(), "comments": collections.Counter(),
           "gaps": {}}
    allids = collections.Counter()
    tokclass = collections.Counter()
    tokentries = collections.Counter()
    prefixes = collections.Counter()
    unknown_angle = collections.Counter()
    no_ctx_no_id = 0
    total = 0
    for p in paths:
        recs = parse_file(p); S = strings(recs)
        dom = S[0]["domain"] if S else os.path.basename(p)
        rep["per_domain"][dom] = {"strings": len(S), "header": len(recs) - len(S),
                                  "caret": sum(1 for r in S if r["context_prefix"]),
                                  "plural": sum(1 for r in S if r["msgid_plural"] is not None)}
        for r in S:
            total += 1
            allids[r["internal_id"]] += 1
            if r["msgid_plural"] is not None: rep["plural"] += 1
            for f in r["flags"]: rep["flags"][f] += 1
            if r["comments"]["extracted"]: rep["comments"]["with #."] += 1
            if r["comments"]["refs"]: rep["comments"]["with #:"] += 1
            if r["comments"]["previous"]: rep["comments"]["with #| (fuzzy prev)"] += 1
            if r["comments"]["translator"]: rep["comments"]["with # translator"] += 1
            if r["context_prefix"]: prefixes[r["context_prefix"]] += 1
            has_id = any("id=" in x for x in r["comments"]["extracted"])
            if not r["context_prefix"] and not has_id:
                no_ctx_no_id += 1
            found = po_tokens.find(r["msgid"])
            for name, matches in found.items():
                if matches:
                    tokclass[name] += len(matches); tokentries[name] += 1
            for raw, name, kind in po_tokens.angle_tokens(r["msgid"]):
                if name not in po_tokens.KNOWN_TAGS:
                    unknown_angle[name] += 1
    rep["totals"] = {"strings": total, "unique_internal_id": len(allids),
                     "id_collisions": total - len(allids)}
    rep["tokens"] = {name: {"occurrences": tokclass[name], "entries": tokentries[name]}
                     for name in po_tokens.PATTERNS if tokclass[name]}
    fams = collections.Counter()
    for pre, c in prefixes.items():
        fams[family(pre)] += 1
    rep["prefix_families"] = dict(fams.most_common())
    rep["prefix_distinct"] = len(prefixes)
    rep["gaps"] = {"unknown_angle_tokens": {"distinct": len(unknown_angle),
                                            "occurrences": sum(unknown_angle.values()),
                                            "examples": [n for n, _ in unknown_angle.most_common(8)]},
                   "strings_with_no_prefix_and_no_wmlid": no_ctx_no_id,
                   "flags_present": dict(rep["flags"])}
    return rep


def main(argv):
    as_json = "--json" in argv
    if as_json: argv.remove("--json")
    paths = argv
    if not paths:
        print(__doc__); return
    rep = build(paths)
    if as_json:
        print(json.dumps(rep, ensure_ascii=False, indent=2)); return
    t = rep["totals"]
    print(f"# Wesnoth lockit report — {len(paths)} file(s)\n")
    print(f"strings={t['strings']}  unique_id={t['unique_internal_id']}  "
          f"collisions={t['id_collisions']}  pluralizable={rep['plural']}  "
          f"prefixes={rep['prefix_distinct']}")
    print("\n## per domain")
    for d, v in rep["per_domain"].items():
        print(f"  {d:16} strings={v['strings']:5} header={v['header']} caret={v['caret']:4} plural={v['plural']}")
    print("\n## token coverage (occurrences / entries)")
    for name, v in rep["tokens"].items():
        print(f"  {name:12} {v['occurrences']:6} / {v['entries']:5}")
    print("\n## comments")
    for k, v in rep["comments"].items():
        print(f"  {k:24} {v}")
    print(f"\n## prefix families: {rep['prefix_families']}")
    print("\n## GAPS / unknowns (review these)")
    g = rep["gaps"]
    print(f"  unknown angle tokens: {g['unknown_angle_tokens']['occurrences']} occ, "
          f"{g['unknown_angle_tokens']['distinct']} distinct — e.g. {g['unknown_angle_tokens']['examples']}")
    print(f"  strings with neither ^-prefix nor #.id (identity relies on msgid text): "
          f"{g['strings_with_no_prefix_and_no_wmlid']}")
    print(f"  flags present: {g['flags_present'] or '(none — templates)'}")


if __name__ == "__main__":
    main(sys.argv[1:])
