#!/usr/bin/env python3
# vault/library/script-templates/byte_stable_jsonl.py
# TEMPLATE — the byte layer of a normalized bundle exporter, reusable for ANY lockit format.
# first_seen: veloren (session 007) · confirmed format-independent: wesnoth (session 008).
"""
PURPOSE: the parts of a bundle exporter that came out IDENTICAL across two exporters written
against two different consumers, two different formats and two different contracts — so the
third exporter starts from working code instead of from memory. Embodies convention
[[byte-stable-artifact]]; see also [[derived-identity-keys]], [[refusal-scope-discipline]],
[[producer-contract-ownership]].

WHY THIS EXISTS (rationale a less-capable agent can follow and reproduce):

Most output this system produces is a REPORT: a human reads it once and it is gone. A bundle is
an ARTIFACT: another system reads it, stores it, and joins against it later. A report describes;
an artifact PROMISES — the same input produces the same bytes, forever. Break the promise and
nothing crashes: a consumer's stored offsets now point at the wrong characters, or its joins
match nothing, and no schema complains. That is why the byte layer gets its own template and its
own tests, rather than being written from scratch each time and "looking fine".

What is deliberately NOT here: the row builder, the manifest's field list, and the source
reader. Those are the parts that legitimately differ per (format, contract) pair — see the
backlog's converter-generator item. Everything below is the part that did not differ at all.

HOW TO PARAMETERISE:
  1. Set ROW_KEYS / MANIFEST_KEYS to the contract's field lists, IN SCHEMA ORDER. They drive
     both key order and the additionalProperties:false check — one declaration, two jobs.
  2. Write build_rows(...) -> list[dict], each row built from ONE dict literal in ROW_KEYS
     order. Do not sort keys anywhere, ever.
  3. Fill in verify_rows() with the contract's per-row rules (enums, null discipline, id shape).
  4. Wire cmd_export / cmd_check to your reader.
Everything else is usable unchanged.

CLI shape both instances converged on:
    python3 <exporter>.py <source...> [<out-dir>] [--dry-run] [--force]
    python3 <exporter>.py --check <bundle-dir> [<source-dir>]
"""
import os, sys, json, hashlib, collections

# --- 1. the contract's field lists ------------------------------------------------
# In SCHEMA ORDER. Reordering these changes the payload hash without changing meaning,
# which is the worst kind of diff — so they are declared once and never sorted.
ROW_KEYS = ('id', 'seq', 'source_text')                    # <-- replace per contract
MANIFEST_KEYS = ('line_count', 'content_hash')             # <-- replace per contract


# --- 2. the byte contract ---------------------------------------------------------
def serialize(rows):
    """UTF-8, no BOM, LF, one JSON object per line, exactly one trailing newline.

    json.dumps escapes every C0 control (including '\\n') regardless of ensure_ascii, so
    "no embedded literal newline" holds by construction. NO sort_keys: key order is
    insertion order, which is why every row is built from one dict literal in schema order.

    This function came out character-for-character identical in both exporters. If you find
    yourself editing it for a third, stop and ask whether the contract really requires it —
    every edit here moves every hash ever emitted.
    """
    return ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode('utf-8')


def verify_payload_bytes(payload):
    """The bytes-level half of the contract — what a re-serialisation would hide.

    Format-independent: written for Fluent, reused unchanged for gettext. These are exactly
    the defects that survive a JSON-schema pass and break a consumer anyway.
    """
    p = []
    if payload[:3] == b'\xef\xbb\xbf':
        p.append('payload starts with a UTF-8 BOM')
    if b'\r' in payload:
        p.append('payload contains CR (must be LF-only)')
    if b'\x00' in payload:
        p.append('payload contains a NUL byte')
    if payload and not payload.endswith(b'\n'):
        p.append('payload does not end with a newline')
    if payload.endswith(b'\n\n'):
        p.append('payload ends with more than one newline')
    try:
        text = payload.decode('utf-8')
    except UnicodeDecodeError as ex:
        return p + [f'payload is not valid UTF-8: {ex}']
    for i, ln in enumerate(text.split('\n')[:-1], 1):
        if not ln.strip():
            p.append(f'payload line {i} is blank')
    return p


def script_hash(module_paths):
    """sha256 over the concatenated bytes of the exporter AND every first-party module it
    imports, in ascending byte order of their repo-relative POSIX paths.

    Hashing the exporter alone would pin one file and leave the PARSER free to move underneath
    it — which is the change most likely to alter what a row says while the exporter's own
    bytes stay put. Report the file list with every export; write the definition into the
    schema so a consumer knows what the number covers.
    """
    files = sorted(p.replace(os.sep, '/') for p in module_paths)
    h = hashlib.sha256()
    for rel in files:
        with open(rel, 'rb') as fh:
            h.update(fh.read())
    return h.hexdigest(), files


def content_hash(payload, covers='lines.jsonl'):
    """Over the payload bytes EXACTLY AS WRITTEN — never over a re-serialisation of the parsed
    rows, which would hide a text-mode write, a BOM, or CRLF."""
    return {'algorithm': 'sha256', 'value': hashlib.sha256(payload).hexdigest(), 'covers': covers}


# --- 3. self-checks: accumulate, then refuse ONCE ---------------------------------
def verify_rows(rows):
    """Per-row contract rules. Fill in the contract-specific ones; the generic skeleton below
    (required keys, no extra keys, unique id, dense 0-based seq) is what both instances share.

    Scope every check per [[refusal-scope-discipline]]: a rule here REFUSES THE WHOLE EXPORT,
    so it must be keyed to something a row's correctness actually depends on — never to
    well-formed-but-absent metadata. If you cannot name the output field that would be wrong,
    it belongs in the census or in a per-row verdict field, not here.
    """
    p = []
    seen_ids, seen_seq = set(), set()
    for r in rows:
        ref = r.get(ROW_KEYS[0], '?')
        missing = [k for k in ROW_KEYS if k not in r]
        if missing:
            p.append(f'row {ref}: missing required {missing}')
        extra = [k for k in r if k not in ROW_KEYS]
        if extra:
            p.append(f'row {ref}: keys outside the schema (additionalProperties:false): {extra}')
        if r.get(ROW_KEYS[0]) in seen_ids:
            p.append(f'row {ref}: duplicate id')
        seen_ids.add(r.get(ROW_KEYS[0]))
        if r.get('seq') in seen_seq:
            p.append(f'row {ref}: duplicate seq {r.get("seq")}')
        seen_seq.add(r.get('seq'))
        # ---- contract-specific rules go here (enums, null discipline, id shape) ----
    if sorted(x for x in seen_seq if isinstance(x, int)) != list(range(len(rows))):
        p.append(f'seq is not dense and 0-based over {len(rows)} rows')
    return p


def verify_manifest(m, rows, payload):
    p = []
    missing = [k for k in MANIFEST_KEYS if k not in m]
    if missing:
        p.append(f'manifest: missing required {missing}')
    extra = [k for k in m if k not in MANIFEST_KEYS]
    if extra:
        p.append(f'manifest: keys outside the schema (additionalProperties:false): {extra}')
    if m.get('line_count') != len(rows):
        p.append(f'manifest: line_count {m.get("line_count")} != {len(rows)} rows')
    digest = hashlib.sha256(payload).hexdigest()
    if (m.get('content_hash') or {}).get('value') != digest:
        p.append(f'manifest: content_hash.value != sha256(payload) ({digest})')
    return p


# --- 4. write: rows BEFORE manifest -----------------------------------------------
def write_bundle(out_dir, payload, manifest, rows_name='lines.jsonl', manifest_name='manifest.json'):
    """The rows go first, always.

    A torn run then leaves a bundle with NO MANIFEST — rejected on sight — rather than a
    manifest asserting a hash for bytes that are not there. State the corollary in the schema:
    WHOEVER REWRITES THE ROWS REWRITES THE MANIFEST. A row file that has moved while the
    manifest has not is the one corruption nothing else in the chain can detect.
    """
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, rows_name), 'wb') as fh:
        fh.write(payload)
    with open(os.path.join(out_dir, manifest_name), 'wb') as fh:
        fh.write((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


# --- 5. --check: turn "byte-stable" from a claim into a test ----------------------
def cmd_check(bundle_dir, rebuild=None, rows_name='lines.jsonl', manifest_name='manifest.json'):
    """Re-read the written bundle from disk and verify it. Pass `rebuild` — a zero-arg callable
    returning a fresh `rows` list — and it re-exports in memory and BYTE-COMPARES.

    That comparison is the check only the producer can do, and it catches what no schema can
    see: a text-mode write, a locale-dependent sort, or a parser change that silently moved
    every string.
    """
    mpath, lpath = os.path.join(bundle_dir, manifest_name), os.path.join(bundle_dir, rows_name)
    if not os.path.isfile(mpath) or not os.path.isfile(lpath):
        sys.exit(f'ERROR: {bundle_dir} is missing {manifest_name} and/or {rows_name}')
    with open(lpath, 'rb') as fh:
        payload = fh.read()                       # BYTES — re-reading them is the point
    with open(mpath, 'rb') as fh:
        manifest = json.loads(fh.read().decode('utf-8'))

    problems = verify_payload_bytes(payload)
    rows = []
    for i, ln in enumerate(payload.decode('utf-8').split('\n')[:-1], 1):
        try:
            rows.append(json.loads(ln))
        except ValueError as ex:
            problems.append(f'{rows_name} line {i}: not valid JSON ({ex})')
    problems += verify_rows(rows) + verify_manifest(manifest, rows, payload)

    print(f'bundle:   {bundle_dir}')
    print(f'rows:     {len(rows)}   payload: {len(payload)} bytes')
    print(f'sha256:   {hashlib.sha256(payload).hexdigest()}')

    if rebuild is not None:
        fresh = serialize(rebuild())
        if fresh == payload:
            print('re-export: REPRODUCIBLE (byte-identical)')
        else:
            a, b = fresh.split(b'\n'), payload.split(b'\n')
            first = next((i for i, (x, y) in enumerate(zip(a, b), 1) if x != y), len(b) + 1)
            problems.append(f're-export DRIFT: payload differs, first differing line {first} '
                            f'({len(fresh)} vs {len(payload)} bytes)')

    if problems:
        print(f'\n{len(problems)} PROBLEM(S):')
        for x in problems[:40]:
            print(f'  {x}')
        return 1
    print('\ncheck: 0 problems')
    return 0


# --- 6. the export command: census -> self-check -> refuse or write ---------------
def cmd_export(build_rows, build_manifest, out_dir, dry_run=False, census=None):
    """The order both instances converged on, and each step earns its place:

      census BEFORE the self-checks  — so a run that refuses still tells you what it saw;
      accumulate ALL problems        — failing on the first hides the other twenty-four;
      refuse ONCE, print the first 25;
      --dry-run writes nothing       — the cheap way to see the hash before committing to it.
    """
    rows = build_rows()
    payload = serialize(rows)
    manifest = build_manifest(rows, payload)
    if census:
        census(rows)
    print(f'payload: {len(payload)} bytes, sha256 {hashlib.sha256(payload).hexdigest()}')

    problems = verify_rows(rows) + verify_manifest(manifest, rows, payload) \
        + verify_payload_bytes(payload)
    if problems:
        print(f'\n{len(problems)} SELF-CHECK PROBLEM(S):', file=sys.stderr)
        for x in problems[:25]:
            print(f'  {x}', file=sys.stderr)
        sys.exit('refusing to write an out-of-contract bundle')
    print('\nself-check: 0 problems')

    if dry_run:
        print('--dry-run: nothing written')
        return 0
    write_bundle(out_dir, payload, manifest)
    print(f'wrote {out_dir}')
    return 0


# --- 7. the tests you must not skip ------------------------------------------------
# Pin the payload sha256 TWICE:
#   * over a SYNTHETIC corpus — runs on a fresh clone, licence-clean, no client data;
#   * over the REAL corpus — skipped when the gitignored data is absent.
# The real risk was never nondeterminism. It is a future parser edit silently moving every
# string, and only a pinned hash notices that.
if __name__ == '__main__':
    print(__doc__)
