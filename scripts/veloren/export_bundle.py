#!/usr/bin/env python3
"""export_bundle.py — emit a normalized BUNDLE (manifest.json + lines.jsonl) from the
Veloren Fluent lockit, conforming to the downstream consumer's DRAFT v0.2 contracts.

=========================== WHY THIS EXISTS (read me) ===========================
A sibling project annotates localisation strings. It does not read
.ftl files — it reads a BUNDLE: one manifest describing the source, plus one JSON object
per translatable unit. This script is the producer for the Fluent format.

The contract is unusual in one way that shapes every decision below: `source_text` is
NORMATIVE. Every annotation ever stored is a character offset into the string WE emit —
the consumer never opens the original file. So a bundle is not a dump, it is a promise:
the same input must produce byte-identical output forever, or every stored annotation
silently points at the wrong characters.

Three consequences, each of which is a rule in the code:

 1. IDENTITY IS A HASH OF THE NATURAL KEY, NEVER A LINE NUMBER. `line_id` is a pure
    function of (kind, id, attr) — the same three fields we publish as `native_ref`.
    Line numbers shift when someone adds a message above; ids do not. This is the house
    rule from scripts/wesnoth/po_parse.py ("line numbers are locators, not ids").
    We deliberately do NOT hash the bundle's source_id into it: the contract says
    renaming a bundle must not invalidate stored annotations.

 2. TEXT IS NORMALISED, AND THAT IS A DECLARED CHOICE. ftl_parse strips each line and
    joins multiline values with '\n' (see its docstring). The contract permits "a
    documented deterministic normalization" as an alternative to a verbatim slice, and
    normalised is the better string here: Fluent dedents block values anyway, so a raw
    slice would bake file indentation, trailing whitespace and any future '\r' into the
    text the consumer anchors to. It is deterministic (a pure function of the file
    bytes), and it is reversible on our side — reinsertion regenerates canonical Fluent
    indentation, which is exactly the indentation we dropped. The normalisation is
    versioned in `producer_version`, because the real risk is not nondeterminism but a
    future edit to the parser silently moving thousands of strings.

 3. THE PAYLOAD IS BYTES, NOT OBJECTS. `content_hash` is sha256 over lines.jsonl exactly
    as written on disk, so the file is composed in memory as bytes (UTF-8, no BOM, LF,
    one object per line, exactly one trailing newline), hashed, and written with
    write_bytes — never text mode, which would rewrite '\n' on Windows and invalidate
    the hash we just computed.

WHAT WE REFUSE TO DO: we do not export a corpus that validate.py reports structural
ERRORs on. Unbalanced braces make the placeable scanner drop a construct, so the row
would assert "no placeholder here" over a { $x } the engine will substitute — and
`placeholders: []` is defined by the contract as a POSITIVE assertion, not "didn't look".
--force overrides, loudly, and records the fact in the manifest.

SCOPE: Fluent only. The exporter guide forbids exporting clausewitz-yml and godot-csv
against v0.2 (array cells and dialect constructs are unrepresentable), so this script
globs *.ftl and refuses anything else — which is also what keeps it away from the
proprietary HoI4 and A Dark Forest data.

Usage:
    python3 export_bundle.py <source-dir> [<out-dir>] [--dry-run] [--stamp] [--force]
    python3 export_bundle.py --check <bundle-dir> [<source-dir>]

    <out-dir> defaults to ../../data/veloren/bundle (gitignored, like all extraction output).
    --dry-run  compute + print the census and the payload hash, write nothing.
    --stamp    add manifest.produced_at (omitted by default: it is the only field that
               would make two runs over identical input differ).
    --check    re-read a written bundle from disk and verify it against both schemas;
               give <source-dir> too and it re-exports in memory and byte-compares,
               which turns "byte-stable" from a claim into a test.
"""
import os, sys, json, hashlib, collections

import ftl_parse as F
import labels
import validate

# ---- bundle identity (parameterise here for another Fluent lockit) ----------------
BUNDLE_VERSION   = '0.2.0'                # semver of the CONTRACT, not of the game
SOURCE_ID        = 'veloren'
SOURCE_NAME      = 'Veloren (en)'
SOURCE_FORMAT    = 'fluent-ftl'
SOURCE_LANGUAGE  = 'en'
PRODUCED_BY      = 'lockit-cartographer/veloren/export_bundle.py'
# The normalisation is part of the producer's identity: if it ever changes, source_text
# changes, and this is the field a consumer diffs to find out why the hash moved.
NORMALISATION_ID = 'strip-join-lf'
PRODUCER_VERSION = '0.1.0+norm=' + NORMALISATION_ID
EMPTY_REASON     = 'fluent {""} intentional blank'
# ----------------------------------------------------------------------------------

# The contract's closed vocabularies, hardcoded on purpose: if labels.py ever grows a
# fourth origin or ftl_parse a ninth kind, the export must FAIL rather than emit a value
# outside the enum. This is the tripwire on the boundary map below.
KINDS   = frozenset(['var', 'selector', 'term-ref', 'msg-ref', 'function',
                     'literal', 'markup', 'other'])
ORIGINS = frozenset(['spec', 'project', 'unknown'])

# Our registry says 'fluent' for spec-defined constructs; the contract's enum says 'spec'
# (it generalised the name across formats before ratification). Map at the boundary —
# labels.py is the single source of truth and is NOT renamed to chase another repo's
# vocabulary. 'unknown' passes through UNCHANGED: it is the drift signal that tells the
# consumer not to trust a mask and to escalate to a reviewer. Never collapse it.
ORIGIN_MAP = {'fluent': 'spec', 'project': 'project', 'unknown': 'unknown'}

ROW_REQUIRED = ('line_id', 'seq', 'native_ref', 'file', 'line_no', 'source_text', 'placeholders')
ROW_OPTIONAL = ('key', 'structural_role', 'empty', 'empty_reason', 'context', 'targets')
PH_REQUIRED  = ('start', 'end', 'token', 'kind', 'origin')
PH_OPTIONAL  = ('detail',)


def line_id(kind, ident, attr):
    """Opaque, stable, and a PURE FUNCTION OF native_ref — the same three fields, in a
    fixed order, and nothing else. Not the line number (units move), not the file (a
    message keeps its annotations when it moves between .ftl files), not source_id
    (renaming the bundle must not orphan stored annotations)."""
    return hashlib.sha256('\x1f'.join([kind, ident, attr or '']).encode('utf-8')).hexdigest()[:16]


def build_rows(target):
    """Parse the corpus and build one row per translatable unit, in reading order.

    Reading order = sorted file glob, then position in file, then value-row before its
    attributes. `seq` is assigned from that order, so it is stable as long as the sort is
    (ftl_parse.iter_files sorts explicitly — glob itself is filesystem-ordered).

    A message with NO VALUE AT ALL is not a translatable unit and is skipped: Fluent
    requires a message to have a value or attributes, and a container message's absent
    value is a syntactic artifact, not a blank string someone chose. A syntactic blank
    ({""}) IS a unit — it is a deliberate authoring decision — and ships with empty=true.
    """
    entries, root = F.parse_tree(target)
    # context is a CLASSIFICATION SIGNAL for the consumer, not translatable text. Two
    # sources: the `#` comment attached to an entry (rare — authors seldom write them) and
    # the enclosing `##`/`###` section marker, which is the finer-grained structural signal
    # the consumer's pre-pass wants (the file is coarse: 48 files over ~7k units).
    comments = {e.id: e.comment for e in entries if e.kind != 'junk' and e.comment}
    sections = {e.id: e.section for e in entries if e.kind != 'junk' and e.section}
    rows, problems = [], []
    per_file = collections.Counter()
    stats = collections.Counter()
    kinds, origins = collections.Counter(), collections.Counter()

    for u in F.iter_units(entries, include_empty=True):
        text = u['text']
        if text == '':                      # absent value — not a unit
            stats['skipped_absent_' + ('attr' if u['attr'] else 'value')] += 1
            continue
        rel = u['file'].replace(os.sep, '/')   # forward slashes, once, at the boundary

        placeholders = []
        prev_end = 0
        for start, end, inner in F.placeables(text):
            kind, origin, detail, _ = labels.label_placeable(inner, F.classify_placeable)
            origin = ORIGIN_MAP.get(origin, 'unknown')
            token = text[start:end]
            # Build-time integrity: the scanner returned BOTH offsets and text, so cross-
            # check them against each other. This is the assertion that fails if the two
            # ever come from different strings — the whole bug class this format fears.
            if token[1:-1].strip() != inner:
                problems.append(f"{u['id']}.{u['attr']}: span/inner disagree at {start}")
            if start < prev_end:
                problems.append(f"{u['id']}.{u['attr']}: overlapping placeables at {start}")
            prev_end = end
            ph = {'start': start, 'end': end, 'token': token, 'kind': kind, 'origin': origin}
            if detail:                      # omit rather than emit null/"" — no null in the schema
                ph['detail'] = detail
            placeholders.append(ph)
            kinds[kind] += 1; origins[origin] += 1

        row = {
            'line_id': line_id(u['kind'], u['id'], u['attr']),
            'seq': len(rows) + 1,
            'native_ref': {'kind': u['kind'], 'id': u['id'], 'attr': u['attr']},
            'file': rel,
            'line_no': u['line'],
            'key': u['id'],
            'source_text': text,
            'placeholders': placeholders,
            'structural_role': u['role'],
        }
        if u['empty']:
            row['empty'] = True
            row['empty_reason'] = EMPTY_REASON
            stats['empty'] += 1
        ctx = {}
        if u['id'] in comments:
            ctx['comment'] = comments[u['id']]
            stats['with_comment'] += 1
        if u['id'] in sections:
            ctx['section'] = sections[u['id']]
            stats['with_section'] += 1
        if ctx:
            row['context'] = ctx        # object form, always — never a bare string
            stats['with_context'] += 1
        # acceptance signal: a unit that is ENTIRELY one placeable has no annotatable text
        if len(placeholders) == 1 and placeholders[0]['start'] == 0 \
                and placeholders[0]['end'] == len(text):
            stats['fully_masked_empty' if u['empty'] else 'fully_masked_nonempty'] += 1
        if u['role'] == 'other':
            stats['role_other'] += 1
        rows.append(row)
        per_file[rel] += 1

    stats['rows'] = len(rows)
    stats['placeholders'] = sum(kinds.values())
    stats['unknown_origin'] = origins.get('unknown', 0)
    return rows, per_file, stats, kinds, origins, problems, root


def build_files_index(target, root, per_file):
    """Every .ftl found, not just the ones that produced units — the contract calls
    files[] an inventory, and a zero-unit file is legal (it must be counted and shown,
    not dropped). Paths come from the SAME normalisation as line.file so the contract's
    string-equality rule between them cannot drift."""
    out = []
    for p in F.iter_files(target):
        rel = os.path.relpath(p, root).replace(os.sep, '/')
        out.append({'path': rel, 'line_count': per_file.get(rel, 0), 'encoding': 'utf-8'})
    return out


def serialize(rows):
    """The byte contract: UTF-8, no BOM, LF, one JSON object per line, exactly one
    trailing newline. json.dumps escapes every C0 control (including '\\n') regardless of
    ensure_ascii, so "no embedded literal newlines" holds by construction. No sort_keys:
    key order is insertion order, which is why every row is built from one dict literal
    in schema order — reordering keys would change the hash without changing meaning."""
    return ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode('utf-8')


def build_manifest(rows, files, payload, stats, kinds, origins, stamp, forced, audit_unknown):
    notes = (
        f"source_text uses a documented deterministic normalisation ({NORMALISATION_ID}: strip each "
        "line, join multiline with LF, strip); it is NOT a verbatim file slice. There is no manifest "
        "field to declare this, so it is recorded here and in producer_version. "
        f"line_count counts message values that EXIST, term values and attributes: {stats['rows']} = "
        f"{stats['rows'] - stats['empty']} non-empty + {stats['empty']} intentionally blank; "
        f"{stats.get('skipped_absent_value', 0)} container messages with no value at all are not units "
        "and are not counted. The corpus has 771 {\"\"} plus 1 spaced { \"\" } = 772 syntactic blanks "
        "(contracts quoting 771 count one spelling, not the construct). key is NON-UNIQUE by design: "
        "a message value and its attributes share it — join on line_id. targets is withheld per v0.2 "
        "although translation locales exist and are already aligned by identity upstream. "
        "Coverage caveat: msg-ref has 0 occurrences here, and of the spec functions only project-"
        "defined TAIL occurs, so NUMBER/DATETIME -> spec is declared, not exercised. "
        "_manifest.ron (engine loader metadata, not translatable) is excluded from files[]. "
        f"Drift: {stats['unknown_origin']} placeholders with origin=unknown, {stats['role_other']} "
        f"units with structural_role=other, labels.audit={audit_unknown}."
    )
    if forced:
        notes += f" WRITTEN WITH --force OVER {forced} STRUCTURAL ERROR(S) FROM validate.py."
    m = {
        'bundle_version': BUNDLE_VERSION,
        'source_id': SOURCE_ID,
        'source_name': SOURCE_NAME,
        'source_format': SOURCE_FORMAT,
        'source_language': SOURCE_LANGUAGE,
        'produced_by': PRODUCED_BY,
        'producer_version': PRODUCER_VERSION,
    }
    if stamp:
        import datetime
        m['produced_at'] = datetime.datetime.now(datetime.timezone.utc).replace(
            microsecond=0).isoformat().replace('+00:00', 'Z')
    m['line_count'] = len(rows)
    m['content_hash'] = {'algorithm': 'sha256',
                         'value': hashlib.sha256(payload).hexdigest(),
                         'covers': 'lines.jsonl'}
    m['placeholder_style'] = (
        "Fluent placeables in { } braces: variables { $x }, inline selectors "
        "{ $x -> [key] ... *[other] ... } (one span covering their variant text), term refs "
        "{ -term }, message refs { msg.attr }, functions { TAIL($x) }, and string literals "
        '{ "" }. Human-readable only -- never parsed. All placeholder knowledge comes from '
        "lines[].placeholders spans.")
    m['files'] = files
    m['notes'] = notes
    return m


# ---- verification ----------------------------------------------------------------
def verify_rows(rows, files):
    """The importer's hard-reject rules, checked over rows we can see. Returns problems.

    Deliberately NOT vacuous: `source_text[start:end] == token` is trivially true if you
    set token from that slice, so the checks that earn their keep are the ordering,
    bounds, delimiter and no-extra-keys ones — plus the enum membership that catches a
    registry change leaking an out-of-contract value."""
    p = []
    paths = {f['path'] for f in files}
    counts = collections.Counter()
    seen_ids, seen_seq = set(), set()
    for r in rows:
        ref = r.get('line_id', '?')
        missing = [k for k in ROW_REQUIRED if k not in r]
        if missing:
            p.append(f"row {ref}: missing required {missing}")
        extra = [k for k in r if k not in ROW_REQUIRED + ROW_OPTIONAL]
        if extra:
            p.append(f"row {ref}: keys outside the schema (additionalProperties:false): {extra}")
        if r.get('line_id') in seen_ids:
            p.append(f"row {ref}: duplicate line_id")
        seen_ids.add(r.get('line_id'))
        if r.get('seq') in seen_seq:
            p.append(f"row {ref}: duplicate seq {r.get('seq')}")
        seen_seq.add(r.get('seq'))
        if r.get('file') not in paths:
            p.append(f"row {ref}: file {r.get('file')!r} is not in manifest files[]")
        counts[r.get('file')] += 1
        if not isinstance(r.get('native_ref'), dict) or not r['native_ref']:
            p.append(f"row {ref}: native_ref must be a non-empty object")
        if not isinstance(r.get('line_no'), int) or r.get('line_no', 0) < 1:
            p.append(f"row {ref}: line_no must be >= 1")
        if r.get('structural_role') == '':
            p.append(f"row {ref}: structural_role must not be empty")
        if 'empty_reason' in r and r.get('empty') is not True:
            p.append(f"row {ref}: empty_reason requires empty:true (schema allOf)")
        text = r.get('source_text', '')
        if text == '' and r.get('empty') is not True:
            p.append(f"row {ref}: empty source_text without empty:true")
        prev_end = 0
        for ph in r.get('placeholders', []):
            miss = [k for k in PH_REQUIRED if k not in ph]
            if miss:
                p.append(f"row {ref}: placeholder missing {miss}"); continue
            ex = [k for k in ph if k not in PH_REQUIRED + PH_OPTIONAL]
            if ex:
                p.append(f"row {ref}: placeholder has extra keys {ex}")
            s, e, tok = ph['start'], ph['end'], ph['token']
            if not (0 <= s < e <= len(text)):
                p.append(f"row {ref}: span ({s},{e}) out of bounds for len {len(text)}")
            elif text[s:e] != tok:
                p.append(f"row {ref}: source_text[{s}:{e}] != token")
            if s < prev_end:
                p.append(f"row {ref}: placeholders overlap or are unsorted at {s}")
            prev_end = e
            if tok[:1] != '{' or tok[-1:] != '}':
                p.append(f"row {ref}: token is not brace-delimited")
            if ph['kind'] not in KINDS:
                p.append(f"row {ref}: kind {ph['kind']!r} outside the contract enum")
            if ph['origin'] not in ORIGINS:
                p.append(f"row {ref}: origin {ph['origin']!r} outside the contract enum")
    for f in files:
        if counts[f['path']] != f['line_count']:
            p.append(f"files[] count mismatch for {f['path']}: "
                     f"manifest {f['line_count']} vs {counts[f['path']]} rows")
    return p


def verify_manifest(m, rows, payload):
    p = []
    for k in ('bundle_version', 'source_id', 'source_format', 'source_language',
              'line_count', 'content_hash', 'files'):
        if k not in m:
            p.append(f"manifest: missing required {k}")
    if m.get('bundle_version') != BUNDLE_VERSION:
        p.append(f"manifest: bundle_version {m.get('bundle_version')!r} != {BUNDLE_VERSION!r}")
    sid = m.get('source_id', '')
    if not sid or not sid[0].isalnum() or not all(c.isalnum() or c == '-' for c in sid) \
            or sid != sid.lower():
        p.append(f"manifest: source_id {sid!r} fails ^[a-z0-9][a-z0-9-]*$")
    if m.get('line_count') != len(rows):
        p.append(f"manifest: line_count {m.get('line_count')} != {len(rows)} rows")
    if sum(f['line_count'] for f in m.get('files', [])) != len(rows):
        p.append("manifest: sum(files[].line_count) != row count")
    ch = m.get('content_hash', {})
    if ch.get('algorithm') != 'sha256':
        p.append("manifest: content_hash.algorithm must be sha256")
    if ch.get('covers') != 'lines.jsonl':
        p.append("manifest: content_hash.covers must be lines.jsonl")
    digest = hashlib.sha256(payload).hexdigest()
    if ch.get('value') != digest:
        p.append(f"manifest: content_hash.value != sha256(lines.jsonl) ({digest})")
    if len(ch.get('value', '')) != 64 or any(c not in '0123456789abcdef' for c in ch.get('value', '')):
        p.append("manifest: content_hash.value must be 64 lowercase hex chars, no prefix")
    return p


def verify_payload_bytes(payload):
    """The bytes-level half of the contract — what a re-serialisation would hide."""
    p = []
    if payload[:3] == b'\xef\xbb\xbf':
        p.append("lines.jsonl starts with a UTF-8 BOM")
    if b'\r' in payload:
        p.append("lines.jsonl contains CR (must be LF-only)")
    if b'\x00' in payload:
        p.append("lines.jsonl contains a NUL byte")
    if not payload.endswith(b'\n'):
        p.append("lines.jsonl does not end with a newline")
    if payload.endswith(b'\n\n'):
        p.append("lines.jsonl ends with more than one newline")
    try:
        text = payload.decode('utf-8')
    except UnicodeDecodeError as ex:
        return p + [f"lines.jsonl is not valid UTF-8: {ex}"]
    for i, ln in enumerate(text.split('\n')[:-1], 1):
        if not ln.strip():
            p.append(f"lines.jsonl line {i} is blank")
    return p


# ---- commands --------------------------------------------------------------------
def census(stats, kinds, origins, files):
    print(f"rows (line_count):        {stats['rows']}")
    print(f"  non-empty units:        {stats['rows'] - stats['empty']}")
    print(f"  intentionally blank:    {stats['empty']}  (empty:true)")
    print(f"skipped, no value at all: {stats.get('skipped_absent_value', 0)} message value(s), "
          f"{stats.get('skipped_absent_attr', 0)} attribute(s)")
    print(f"files in inventory:       {len(files)}  "
          f"({sum(1 for f in files if f['line_count'] == 0)} contributed 0 units)")
    print(f"placeholders:             {stats['placeholders']}")
    print(f"  by kind:                {dict(sorted(kinds.items()))}")
    print(f"  by origin:              {dict(sorted(origins.items()))}")
    print(f"entirely one placeable:   {stats.get('fully_masked_empty', 0)} empty:true + "
          f"{stats.get('fully_masked_nonempty', 0)} NOT empty")
    print(f"rows with context:        {stats.get('with_context', 0)}  "
          f"({stats.get('with_section', 0)} section, {stats.get('with_comment', 0)} comment)")
    print(f"DRIFT — origin=unknown:   {stats['unknown_origin']}"
          + ("   <-- REVIEWER ESCALATION" if stats['unknown_origin'] else ""))
    print(f"DRIFT — role=other:       {stats['role_other']}"
          + ("   <-- REVIEWER ESCALATION" if stats['role_other'] else ""))


def cmd_export(target, out_dir, dry_run, stamp, force):
    if not os.path.isdir(target) and not target.endswith('.ftl'):
        sys.exit(f"ERROR: {target} is not a directory or .ftl file")
    ftl = F.iter_files(target)
    if not ftl:
        sys.exit(f"ERROR: no .ftl files under {target}. This exporter is Fluent-only — the "
                 "consumer's v0.2 contracts cannot represent clausewitz-yml or godot-csv.")

    findings = validate.validate(target)
    errors = [f for f in findings if f[0] == 'ERROR']
    if errors:
        print(f"validate.py reports {len(errors)} structural ERROR(s):", file=sys.stderr)
        for sev, ctx, msg in errors[:10]:
            print(f"  {sev} {ctx}: {msg}", file=sys.stderr)
        if not force:
            sys.exit("REFUSING TO EXPORT: a structural error makes placeholder spans unreliable, "
                     "and `placeholders: []` is a positive assertion in this contract. "
                     "Fix the source or re-run with --force.")
        print("!!! --force: exporting over structural errors; recorded in manifest.notes",
              file=sys.stderr)

    audit_unknown = labels.audit(target)
    print()
    rows, per_file, stats, kinds, origins, problems, root = build_rows(target)
    files = build_files_index(target, root, per_file)
    payload = serialize(rows)
    manifest = build_manifest(rows, files, payload, stats, kinds, origins, stamp,
                              len(errors) if force else 0, audit_unknown)

    census(stats, kinds, origins, files)
    print(f"payload:                  {len(payload)} bytes, "
          f"sha256 {manifest['content_hash']['value']}")

    problems += verify_rows(rows, files)
    problems += verify_manifest(manifest, rows, payload)
    problems += verify_payload_bytes(payload)
    for f in files:
        if f['line_count'] == 0:
            print(f"WARNING: {f['path']} contributed 0 units", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} SELF-CHECK PROBLEM(S):", file=sys.stderr)
        for x in problems[:25]:
            print(f"  {x}", file=sys.stderr)
        sys.exit("refusing to write an out-of-contract bundle")
    print("\nself-check: 0 problems")

    if dry_run:
        print("--dry-run: nothing written")
        return 0
    os.makedirs(out_dir, exist_ok=True)
    # lines.jsonl FIRST: a torn run then leaves a bundle with no manifest (rejected on
    # sight) rather than a manifest asserting a hash for a file that isn't there.
    with open(os.path.join(out_dir, 'lines.jsonl'), 'wb') as fh:
        fh.write(payload)
    with open(os.path.join(out_dir, 'manifest.json'), 'wb') as fh:
        fh.write((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f"wrote {out_dir}/lines.jsonl + manifest.json")
    return 0


def cmd_check(bundle_dir, source_dir=None):
    mpath = os.path.join(bundle_dir, 'manifest.json')
    lpath = os.path.join(bundle_dir, 'lines.jsonl')
    if not os.path.isfile(mpath) or not os.path.isfile(lpath):
        sys.exit(f"ERROR: {bundle_dir} is missing manifest.json and/or lines.jsonl")
    payload = open(lpath, 'rb').read()          # BYTES — re-reading is the point
    manifest = json.loads(open(mpath, 'rb').read().decode('utf-8'))

    problems = verify_payload_bytes(payload)
    rows = []
    for i, ln in enumerate(payload.decode('utf-8').split('\n')[:-1], 1):
        try:
            rows.append(json.loads(ln))
        except ValueError as ex:
            problems.append(f"lines.jsonl line {i}: not valid JSON ({ex})")
    problems += verify_rows(rows, manifest.get('files', []))
    problems += verify_manifest(manifest, rows, payload)

    print(f"bundle:   {bundle_dir}")
    print(f"rows:     {len(rows)}   payload: {len(payload)} bytes")
    print(f"sha256:   {hashlib.sha256(payload).hexdigest()}")

    if source_dir:
        # The check only we can do: re-export in memory and compare BYTES. This is what
        # catches a text-mode write, a locale-dependent sort, or a parser change that
        # moved source_text — none of which the schemas can see.
        fresh, _, _, _, _, _, _ = build_rows(source_dir)
        fresh_payload = serialize(fresh)
        if fresh_payload == payload:
            print("re-export: REPRODUCIBLE (byte-identical)")
        else:
            first = next((i for i, (a, b) in enumerate(
                zip(fresh_payload.split(b'\n'), payload.split(b'\n')), 1) if a != b), '?')
            problems.append(f"re-export DRIFT: payload differs, first at line {first} "
                            f"({len(fresh_payload)} vs {len(payload)} bytes)")

    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for x in problems[:40]:
            print(f"  {x}")
        return 1
    print("\ncheck: 0 problems")
    return 0


def main(argv):
    if '--check' in argv:
        rest = [a for a in argv if a != '--check']
        if not rest:
            sys.exit("usage: export_bundle.py --check <bundle-dir> [<source-dir>]")
        return cmd_check(rest[0], rest[1] if len(rest) > 1 else None)
    flags = {'--dry-run', '--stamp', '--force'}
    pos = [a for a in argv if a not in flags]
    bad = [a for a in argv if a.startswith('--') and a not in flags]
    if bad:
        sys.exit(f"unknown flag(s): {bad}\n{__doc__}")
    if not pos:
        sys.exit(__doc__)
    out = pos[1] if len(pos) > 1 else os.path.join('..', '..', 'data', 'veloren', 'bundle')
    return cmd_export(pos[0], out, '--dry-run' in argv, '--stamp' in argv, '--force' in argv)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
