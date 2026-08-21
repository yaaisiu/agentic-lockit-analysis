#!/usr/bin/env python3
# scripts/wesnoth/export_bundle.py
# source: TASK-I1 — the BILINGUAL bundle exporter. Contract: contracts/bundle.schema.json.
"""export_bundle.py — emit a normalized BILINGUAL BUNDLE (manifest.json + lines.jsonl)
from a profiled gettext lockit, for a downstream consumer that scores machine translation.

=========================== WHY THIS EXISTS (read me) ===========================
A sibling project benchmarks machine translation. It never opens a .po file — it reads a
BUNDLE: one manifest describing the source, plus one JSON object per translatable unit,
each carrying BOTH sides of the pair. This script is the producer for the gettext format.

The contract it emits is published HERE, in `contracts/bundle.schema.json`, and that file
is normative: a consumer's copy is a validating mirror. This repository owns the *profile*
(the lockit anatomy, the segment_id function, what each field means) because it is the
single producer and every consumer keys to it. Each consumer owns its own *bundle contract*
— which is why this exporter and `scripts/veloren/export_bundle.py` deliberately DO NOT
converge: the Veloren one targets a span-oriented monolingual profile for a different
consumer. Two exporters, two contracts, one profile. Do not merge them.

Five rules the code exists to enforce:

 1. IDENTITY IS PINNED, AND IT IS *NOT* THE READER'S internal_id. `segment_id` is
      textdomain + ":" + sha1(((msgctxt or "") + "|" + msgid_raw).utf8).hexdigest()[:12]
    — 12 lowercase hex, a pure function of (textdomain, msgctxt, msgid_raw) and nothing
    else. po_parse.py mints an id of the SAME SHAPE and a DIFFERENT VALUE (10 chars, with
    the domain and the plural hashed in behind a 0x1f separator). Reusing it would produce
    a bundle that validates, looks correct, and joins to nothing downstream. Hence
    `_assert_id_shape` and hence the four pinned vectors in the test suite.

 2. TWO TEXT FORMS, ONE OF THEM NORMATIVE. `source_en` / `target_pl` are the RAW PO
    strings, escapes intact, exactly as the reader returns them — the id is computed over
    the raw msgid and any future character offset anchors there. `*_display` are the
    unescaped forms: derived, non-normative, and provided so a consumer can send natural
    prose to a model without us guessing which form it wants. ORDER MATTERS: placeholder
    and markup detection runs on the RAW string, because that is what po_tokens' regexes
    are written against. Display is derived afterwards and is never an input to detection.

 3. TWO KINDS OF ERROR, TWO DIFFERENT REACTIONS — conflating them makes this script
    produce nothing. A STRUCTURAL error (a .po that will not parse, a broken plural block)
    means the rows are untrustworthy: refuse to export, `--force` to override loudly. A
    CROSS-LOCALE CONTENT finding (the target dropped a $var) is a real upstream translation
    bug that has been in the locale for years: NEVER refuse — record it per row in
    `placeholder_check` and let the curation step decide whether to exclude the row or keep
    it deliberately labelled as a known-bad reference case.

 4. BYTE-STABLE PAYLOAD. Composed in memory as bytes, UTF-8, no BOM, LF only, one object
    per line, fixed key order, exactly one trailing newline, written with a single binary
    write. `content_hash` is the sha256 of those bytes. `--check` re-reads them from disk
    and, given a source directory, re-exports in memory and byte-compares.

 5. lines.jsonl IS WRITTEN BEFORE manifest.json. A torn run then leaves a bundle with no
    manifest (rejected on sight) rather than a manifest asserting a hash for bytes that are
    not there. The standing rule: WHOEVER REWRITES THE ROWS REWRITES THE MANIFEST.

Provenance is a STOP CONDITION, not a best effort. The manifest requires upstream
{remote, commit, branch}; if the checkout cannot supply all three this script exits without
writing anything. A plausible-looking bundle sitting beside a real one is the exact failure
the requirement exists to prevent, so there is no degraded output path and no alternate
directory for one.

Usage:
    python3 export_bundle.py <lockit> <locale> [<out-dir>] [--dry-run] [--force]
    python3 export_bundle.py --check <bundle-dir> [<source-po-root>]

    <lockit>   a profiled lockit name, e.g. `wesnoth` (reads sources/<lockit>/po/).
    <locale>   the target locale, e.g. `pl` (reads <domain>/<locale>.po).
    <out-dir>  defaults to data/bundles/<lockit>-<locale> — gitignored, like all output.
    --dry-run  compute + print the census and the payload hash, write nothing.
    --force    export over STRUCTURAL errors (content findings never block; see rule 3).
    --check    re-read a written bundle and verify it; give the source .po root too and it
               re-exports in memory and byte-compares, which turns "byte-stable" into a test.
"""
import os, sys, json, re, hashlib, datetime, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import po_parse as PO
import po_tokens as T
import completeness
import validate_markup
import validate_placeholders as VPH
from list_context_prefixes import family as caret_family

# ---- contract + producer identity ---------------------------------------------------
# BUNDLE_VERSION versions THE CONTRACT (contracts/bundle.schema.json, the bilingual gettext
# profile) — not the bundle instance and not the producer. It is pinned there with `const`,
# so a consumer holding a mirror of one version REJECTS a bundle written against another
# instead of validating it and meaning something else. That failure is not hypothetical: the
# Veloren exporter in this repo shipped 0.2.0 and 0.3.0 bundles that validated identically
# while a 'selector' span meant opposite things. Its numbering is a DIFFERENT consumer's
# contract and this series deliberately does not continue it.
# Bump rule: a change a conforming consumer can ignore is minor; any change to the field
# list, to a field's type, or to a field's meaning is major.
# CARTOGRAPHER_VERSION is the PRODUCER's version and is a different thing — one producer
# version can ship two contracts, and one contract can ship from two producer versions.
BUNDLE_VERSION       = '1.0.0'
CARTOGRAPHER_VERSION = '0.1.0'
SOURCE_FORMAT        = 'gettext-po'
SOURCE_LOCALE        = 'en'
GAME_SLUG            = {'wesnoth': 'battle-for-wesnoth'}

# Every first-party module whose bytes can change what a row says. Hashing the exporter
# alone would pin one file and leave the parser free to move underneath it.
HASHED_MODULES = ('completeness.py', 'export_bundle.py', 'list_context_prefixes.py',
                  'po_parse.py', 'po_tokens.py', 'validate_markup.py',
                  'validate_placeholders.py')

# ---- closed vocabularies (see contracts/bundle.schema.json) -------------------------
# The domain GROUP comes from the confirmed profile's string-type axis
# (vault/lockits/wesnoth/profile.md § String types). Anything not listed is a NEW domain:
# string_class becomes 'unknown', which is the drift signal — never guess a group.
DOMAIN_GROUPS = {
    'wesnoth-lib': 'ui',
    'wesnoth': 'core',
    'wesnoth-units': 'units',
    'wesnoth-help': 'help', 'wesnoth-manual': 'help',
    'wesnoth-manpages': 'manpages',
    'wesnoth-tutorial': 'tutorial',
    'wesnoth-multiplayer': 'mp_editor', 'wesnoth-editor': 'mp_editor',
    'wesnoth-tools': 'tools',
}
CAMPAIGN_DOMAINS = ('wesnoth-anl', 'wesnoth-did', 'wesnoth-dod', 'wesnoth-dw', 'wesnoth-ei',
                    'wesnoth-h2tt', 'wesnoth-httt', 'wesnoth-l', 'wesnoth-low', 'wesnoth-nr',
                    'wesnoth-pap', 'wesnoth-sof', 'wesnoth-sota', 'wesnoth-sotbe',
                    'wesnoth-tb', 'wesnoth-tdg', 'wesnoth-thot', 'wesnoth-trow',
                    'wesnoth-tsg', 'wesnoth-utbs', 'wesnoth-wc', 'wesnoth-wof')
DOMAIN_GROUPS.update({d: 'campaign' for d in CAMPAIGN_DOMAINS})

# list_context_prefixes.family() returns human labels; the contract needs slugs. Mapping at
# the boundary keeps that registry the single source of truth instead of renaming it here.
CARET_SLUG = {'gender/agreement': 'gender_agreement', 'add-ons': 'addons',
              'SI number units': 'si_units', 'list grammar': 'list_grammar',
              'hotkeys': 'hotkeys', 'files/storage': 'files_storage',
              'system/env': 'system_env', 'other/UI': 'other_ui'}
GROUPS = ('ui', 'core', 'units', 'campaign', 'help', 'manpages', 'tutorial',
          'mp_editor', 'tools')
FAMILIES = tuple(sorted(set(CARET_SLUG.values()))) + ('plain',)
STRING_CLASSES = frozenset(['unknown'] + [f'{g}/{f}' for g in GROUPS for f in FAMILIES])
MARKUP_FLAGS = frozenset(['pango', 'docbook', 'po4a', 'entity', 'metasyntax', 'newline'])
POOLS = frozenset(['eval', 'reference', 'untranslated'])
PH_CHECKS = frozenset(['ok', 'source_only', 'target_only', 'mismatch', 'not_applicable'])

ROW_KEYS = ('segment_id', 'seq', 'textdomain', 'file', 'msgctxt', 'source_en',
            'source_en_display', 'target_pl', 'target_pl_display', 'fuzzy', 'plural_forms',
            'placeholders', 'markup_flags', 'string_class', 'neighbours', 'char_limit',
            'last_changed', 'pool', 'placeholder_check', 'source_ref')
PLURAL_KEYS = ('source_plural', 'source_plural_display', 'target_forms',
               'target_forms_display', 'target_nplurals')
MANIFEST_KEYS = ('bundle_version', 'game', 'source_format', 'source_locale', 'target_locale',
                 'upstream', 'extraction_script_hash', 'content_hash', 'line_count',
                 'generated_at', 'cartographer_version', 'textdomains')

_ID_RE = re.compile(r'^[^:]+:[0-9a-f]{12}$')


# ================================ 1. IDENTITY ======================================
# Kept as its own tiny function on purpose: the curation step that follows has to
# recompute ids over a subset, and must not re-derive the rule.

def segment_id(textdomain: str, msgctxt, msgid_raw: str) -> str:
    """The bundle's join key. A pure function of exactly these three inputs.

    NOT the line number, NOT the file, NOT the plural, NOT the unescaped text. The
    separator is a literal '|', which is safe here ONLY because msgctxt is empty on every
    Wesnoth entry — '|' does occur inside Wesnoth text as the $var| terminator, so for a
    lockit that actually uses msgctxt this preimage is not injective and must be revisited.
    """
    pre = (msgctxt or '') + '|' + msgid_raw
    return f'{textdomain}:{hashlib.sha1(pre.encode("utf-8")).hexdigest()[:12]}'


def _assert_id_shape(sid: str):
    if not _ID_RE.match(sid):
        raise AssertionError(f'segment_id {sid!r} is not "<domain>:<12 lowercase hex>" — '
                             'this is what reusing po_parse.internal_id (10 chars) looks like')


# ============================== 2. DERIVATIONS =====================================
# Separate functions, again on purpose: the curation step re-emits rows with a changed
# `pool` and should not have to re-derive the display rule or the classifier.

def display(raw):
    """The DERIVED, non-normative text form. null in -> null out, which the self-checks
    assert: a display field that is present while its raw counterpart is null would be a
    string this producer invented."""
    return None if raw is None else PO.unescape(raw)


def string_class(textdomain, context_prefix):
    """'<domain-group>/<caret-family>', or 'unknown'. NOT the bare textdomain: a consumer
    reading string_class 'wesnoth-lib' gets a value that validates and means nothing."""
    group = DOMAIN_GROUPS.get(textdomain)
    if group is None:
        return 'unknown'          # a domain the profile has not classified — drift signal
    fam = CARET_SLUG.get(caret_family(context_prefix), 'other_ui') if context_prefix else 'plain'
    return f'{group}/{fam}'


def markup_flags(raw):
    """Which markup systems the RAW string carries, via po_tokens' family detection."""
    flags = set()
    if '\\n' in raw:
        flags.add('newline')                     # embedded line break (RAW: backslash + n)
    if T.PATTERNS['entity'].search(raw):
        flags.add('entity')
    if T.markup_family(raw) == 'po4a':
        flags.add('po4a')
    else:
        for _tok, name, _kind in T.angle_tokens(raw):
            fam = T.tag_family(name)             # 'pango' | 'docbook' | None
            flags.add(fam if fam else 'metasyntax')   # bare <slot> CLI metasyntax
    return sorted(flags)


def placeholder_tokens(raw):
    """Plain string tokens, not spans. Reuses validate_placeholders.named() so there is one
    definition of "a placeholder" in this toolkit, plus printf specifiers."""
    return sorted(set(VPH.named(raw)) | set(T.PATTERNS['printf'].findall(raw)))


def placeholder_check(source_raw, target_forms):
    """Cross-locale agreement as a per-row VERDICT, never a refusal (see rule 3).

    The target side is the UNION over all non-empty forms: a singular plural form
    legitimately omits the count variable, and requiring every form to carry every token
    would report the whole plural family as broken. The cost is that a token dropped from
    exactly one form of a plural reads as ok — recorded, not fixed.
    """
    live = [f for f in target_forms if f]
    if not live:
        return 'not_applicable'                  # untranslated: nothing to compare
    src = set(placeholder_tokens(source_raw))
    tgt = set()
    for f in live:
        tgt |= set(placeholder_tokens(f))
    if not src and not tgt:
        return 'not_applicable'
    if src == tgt:
        return 'ok'
    if tgt < src:
        return 'source_only'                     # dropped, invented nothing
    if src < tgt:
        return 'target_only'                     # invented, dropped nothing
    return 'mismatch'                            # both


def nplurals_of(records):
    """nplurals from the .po header's Plural-Forms. The header is what the runtime uses, so
    it — not len(msgstr) — is the authority; a disagreement is reported, never fixed."""
    for r in records:
        if r.get('is_header'):
            hdr = r['msgstr'][0] if r['msgstr'] else ''
            m = re.search(r'nplurals\s*=\s*(\d+)', hdr)
            return int(m.group(1)) if m else None
    return None


def po_revision_date(records):
    for r in records:
        if r.get('is_header'):
            hdr = r['msgstr'][0] if r['msgstr'] else ''
            m = re.search(r'PO-Revision-Date:\s*([^\\]*)', hdr)
            return m.group(1).strip() if m else ''
    return ''


# ============================== 3. PROVENANCE ======================================

class ProvenanceError(Exception):
    """Raised when upstream {remote, commit, branch} cannot be established. A stop
    condition: the manifest requires all three and none of them may be invented."""


def read_upstream(checkout_root):
    """Read remote / commit / branch straight out of .git, with no git subprocess.

    Deliberately file-reads rather than shelling out: the repo's deny-leaning permissions
    allow only a handful of git verbs, `git -C` is not one of the allowed prefixes, and a
    provenance probe that needs a permission prompt is a provenance probe that fails in an
    unattended run. Everything needed is plain text on disk.
    """
    gitdir = os.path.join(checkout_root, '.git')
    if os.path.isfile(gitdir):                                  # worktree/submodule pointer
        with open(gitdir, encoding='utf-8') as fh:
            line = fh.read().strip()
        if line.startswith('gitdir:'):
            gitdir = os.path.normpath(os.path.join(checkout_root, line[7:].strip()))
    if not os.path.isdir(gitdir):
        raise ProvenanceError(f'{checkout_root} is not a git checkout — cannot establish '
                              'upstream {remote, commit, branch}')

    cfg = os.path.join(gitdir, 'config')
    remote = None
    if os.path.isfile(cfg):
        section = None
        with open(cfg, encoding='utf-8', errors='replace') as fh:
            for ln in fh:
                s = ln.strip()
                if s.startswith('[') and s.endswith(']'):
                    section = s[1:-1].strip()
                elif section == 'remote "origin"' and s.startswith('url'):
                    remote = s.split('=', 1)[1].strip()
    if not remote:
        raise ProvenanceError(f'no [remote "origin"] url in {cfg}')

    with open(os.path.join(gitdir, 'HEAD'), encoding='utf-8') as fh:
        head = fh.read().strip()
    if head.startswith('ref:'):
        ref = head[4:].strip()
        branch = ref.rsplit('/', 1)[-1]
        loose = os.path.join(gitdir, *ref.split('/'))
        commit = None
        if os.path.isfile(loose):
            with open(loose, encoding='utf-8') as fh:
                commit = fh.read().strip()
        else:
            packed = os.path.join(gitdir, 'packed-refs')
            if os.path.isfile(packed):
                with open(packed, encoding='utf-8') as fh:
                    for ln in fh:
                        parts = ln.split()
                        if len(parts) == 2 and parts[1] == ref:
                            commit = parts[0]
                            break
        if not commit:
            raise ProvenanceError(f'{ref} resolves to no commit (loose ref or packed-refs)')
    else:
        raise ProvenanceError('HEAD is detached — no branch to record')

    if not re.match(r'^[0-9a-f]{40}$', commit):
        raise ProvenanceError(f'commit {commit!r} is not a 40-hex sha')
    return {'remote': remote, 'commit': commit, 'branch': branch}


def last_changed_for(checkout_root, rel_path):
    """When the .po last changed upstream — or null, honestly.

    A shallow / grafted checkout reports the SAME commit date for every file, so `git log`
    there answers a different question than the one asked. null is the correct answer and a
    fabricated date is not; the producer reports which case it hit.
    """
    gitdir = os.path.join(checkout_root, '.git')
    if os.path.isfile(os.path.join(gitdir, 'shallow')):
        return None, 'shallow checkout: per-file history is not available'
    return None, 'not computed (see contracts/bundle.schema.json: null is an answer)'


# ============================== 4. THE CORPUS ======================================

def domain_dirs(po_root):
    return sorted(d for d in os.listdir(po_root) if os.path.isdir(os.path.join(po_root, d)))


def corpus_inventory(po_root, locale):
    """(textdomains from the .pot corpus, domains missing a target .po).

    textdomains[] is the union of the SOURCE corpus, byte-sorted. A domain present upstream
    and absent on the target side is NAMED, never silently dropped and never counted zero.
    """
    doms, missing = [], []
    for d in domain_dirs(po_root):
        if not os.path.isfile(os.path.join(po_root, d, d + '.pot')):
            continue
        doms.append(d)
        if not os.path.isfile(os.path.join(po_root, d, locale + '.po')):
            missing.append(d)
    return doms, missing


def structural_problems(po_root, locale, textdomains):
    """STRUCTURAL errors only — the kind that make the rows untrustworthy. Cross-locale
    content findings are NOT here by design; they are per-row verdicts (see rule 3)."""
    problems = []
    for d in textdomains:
        path = os.path.join(po_root, d, locale + '.po')
        if not os.path.isfile(path):
            continue
        try:
            recs = PO.parse_file(path, d)
        except Exception as ex:                                   # pragma: no cover
            problems.append(f'{d}: .po will not parse: {ex}')
            continue
        if not any(r.get('is_header') for r in recs):
            problems.append(f'{d}: .po has no header entry (no Plural-Forms, no revision date)')
        entries = PO.strings(recs)
        has_plural = any(r['msgid_plural'] is not None for r in entries)
        # A missing Plural-Forms header is structural ONLY when the domain actually carries a
        # plural entry — then target_nplurals cannot be filled and the schema requires an
        # integer. Two Wesnoth pl domains ship without the header and without any plural; a
        # rule that blocked on the header alone would refuse the whole corpus over metadata
        # that no row in the bundle depends on.
        if has_plural and nplurals_of(recs) is None:
            problems.append(f'{d}: .po header carries no Plural-Forms nplurals=N, '
                            'but the domain has plural entries')
        for r in entries:
            if r['msgid_plural'] is not None and not r['msgstr']:
                problems.append(f'{d}@L{r["lineno"]}: plural entry with no msgstr[N] block')
            if r['msgid'] == '' and r['msgctxt'] is None:         # pragma: no cover
                problems.append(f'{d}@L{r["lineno"]}: non-header entry with empty msgid')
    return problems


def build_rows(po_root, locale, textdomains, checkout_root=None):
    """One row per gettext entry, in export order: textdomains BYTE-sorted, then entry order
    within the file. `seq` is 0-based and global; neighbours are filled per file afterwards.
    """
    rows = []
    stats = collections.Counter()
    per_domain = collections.defaultdict(collections.Counter)
    classes, flags_c, checks, pools = (collections.Counter() for _ in range(4))
    revision_dates, nplurals_seen, plural_arity = {}, {}, []
    flagged = collections.defaultdict(list)
    lc_reason = None

    for dom in sorted(textdomains):                       # byte-sorted, not locale-sorted
        path = os.path.join(po_root, dom, locale + '.po')
        if not os.path.isfile(path):
            continue
        rel = os.path.relpath(path, po_root).replace(os.sep, '/')
        recs = PO.parse_file(path, dom)
        revision_dates[dom] = po_revision_date(recs)
        npl = nplurals_of(recs)
        nplurals_seen[dom] = npl
        last_changed, lc_reason = (last_changed_for(checkout_root, rel)
                                   if checkout_root else (None, 'no checkout given'))
        first = len(rows)

        for r in PO.strings(recs):
            raw_src = r['msgid']
            forms = list(r['msgstr'])
            raw_tgt = forms[0] if forms and forms[0] != '' else None
            state = completeness.entry_state(r)           # the toolkit's state vocabulary
            is_fuzzy = 'fuzzy' in r.get('flags', [])
            # pool is owned by the EXPORT. fuzzy is not done (gettext skips it at runtime),
            # so it collapses into untranslated — while `fuzzy` survives as its own boolean.
            pool = 'untranslated' if (raw_tgt is None or is_fuzzy) else 'eval'

            plural = None
            if r['msgid_plural'] is not None:
                plural = {
                    'source_plural': r['msgid_plural'],
                    'source_plural_display': display(r['msgid_plural']),
                    'target_forms': forms,
                    'target_forms_display': [display(f) for f in forms],
                    'target_nplurals': npl,
                }
                stats['plural'] += 1
                if npl is not None and len(forms) != npl:
                    plural_arity.append(f'{dom}@L{r["lineno"]}: {len(forms)} msgstr form(s) '
                                        f'vs header nplurals={npl}')

            # DERIVED msgctxt: Wesnoth disambiguates with a ^-prefix, not with msgctxt.
            ctx = r['msgctxt'] if r['msgctxt'] else r['context_prefix']
            sid = segment_id(dom, r['msgctxt'], raw_src)   # the RAW msgctxt, never the caret
            _assert_id_shape(sid)
            chk = placeholder_check(raw_src, forms)
            mf = markup_flags(raw_src)
            cls = string_class(dom, r['context_prefix'])

            row = {
                'segment_id': sid,
                'seq': len(rows),
                'textdomain': dom,
                'file': rel,
                'msgctxt': ctx,
                'source_en': raw_src,
                'source_en_display': display(raw_src),
                'target_pl': raw_tgt,
                'target_pl_display': display(raw_tgt),
                'fuzzy': is_fuzzy,
                'plural_forms': plural,
                'placeholders': placeholder_tokens(raw_src),
                'markup_flags': mf,
                'string_class': cls,
                'neighbours': {'prev': None, 'next': None},   # filled below, per file
                'char_limit': None,          # gettext declares none; field kept for lockits that do
                'last_changed': last_changed,
                'pool': pool,
                'placeholder_check': chk,
                'source_ref': list(r['comments']['refs']) or None,
            }
            rows.append(row)
            per_domain[dom][state] += 1
            per_domain[dom]['total'] += 1
            classes[cls] += 1
            checks[chk] += 1
            pools[pool] += 1
            for f in mf:
                flags_c[f] += 1
            if ctx:
                stats['derived_msgctxt'] += 1
            if row['source_en_display'] != raw_src or (
                    raw_tgt is not None and row['target_pl_display'] != raw_tgt):
                stats['escaping_differs'] += 1
            if chk not in ('ok', 'not_applicable'):
                flagged[chk].append(sid)

        # neighbours: previous/next segment_id WITHIN THIS FILE. null at both boundaries —
        # adjacency across two unrelated textdomains is not context.
        block = rows[first:]
        for i, row in enumerate(block):
            row['neighbours']['prev'] = block[i - 1]['segment_id'] if i else None
            row['neighbours']['next'] = block[i + 1]['segment_id'] if i + 1 < len(block) else None

    stats['rows'] = len(rows)
    census = {'per_domain': {d: dict(c) for d, c in per_domain.items()},
              'string_class': dict(classes), 'markup_flags': dict(flags_c),
              'placeholder_check': dict(checks), 'pool': dict(pools),
              'flagged_segment_ids': {k: v for k, v in flagged.items()},
              'nplurals': nplurals_seen, 'plural_arity_disagreements': plural_arity,
              'last_changed_reason': lc_reason}
    return rows, stats, census, revision_dates


# =============================== 5. THE BYTES ======================================

def serialize(rows):
    """The byte contract: UTF-8, no BOM, LF, one JSON object per line, exactly one trailing
    newline. json.dumps escapes every C0 control regardless of ensure_ascii, so "no embedded
    literal newline" holds by construction. No sort_keys — key order is insertion order,
    which is why every row is built from one dict literal in schema order."""
    return ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode('utf-8')


def extraction_script_hash():
    """sha256 over the concatenated bytes of this script and every first-party module it
    imports, in ascending byte order of their repo-relative POSIX paths. Returns (hex, files)."""
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(here))
    files = sorted(os.path.relpath(os.path.join(here, m), repo).replace(os.sep, '/')
                   for m in HASHED_MODULES)
    h = hashlib.sha256()
    for rel in files:
        with open(os.path.join(repo, rel), 'rb') as fh:
            h.update(fh.read())
    return h.hexdigest(), files


def build_manifest(lockit, locale, rows, payload, textdomains, upstream, revision_dates,
                   generated_at=None):
    upstream = dict(upstream)
    # Every textdomain of the bundle appears in the map — a domain whose header carries no
    # PO-Revision-Date is present with an empty string, never absent.
    upstream['po_revision_dates'] = {d: revision_dates.get(d, '') for d in textdomains}
    esh, _files = extraction_script_hash()
    return {
        'bundle_version': BUNDLE_VERSION,
        'game': GAME_SLUG.get(lockit, lockit),
        'source_format': SOURCE_FORMAT,
        'source_locale': SOURCE_LOCALE,
        'target_locale': locale,
        'upstream': upstream,
        'extraction_script_hash': esh,
        'content_hash': {'algorithm': 'sha256',
                         'value': hashlib.sha256(payload).hexdigest(),
                         'covers': 'lines.jsonl'},
        'line_count': len(rows),
        'generated_at': generated_at or datetime.datetime.now(
            datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'cartographer_version': CARTOGRAPHER_VERSION,
        'textdomains': list(textdomains),
    }


# ============================== 6. SELF-CHECKS =====================================
# Each of these REFUSES TO WRITE rather than warning. A warning on an identity or a
# null-discipline violation is a warning nobody reads until the join fails downstream.

def verify_rows(rows):
    p = []
    seen_ids, seen_seq = set(), set()
    by_file = collections.defaultdict(list)
    for r in rows:
        ref = r.get('segment_id', '?')
        missing = [k for k in ROW_KEYS if k not in r]
        if missing:
            p.append(f'row {ref}: missing required {missing}')
        extra = [k for k in r if k not in ROW_KEYS]
        if extra:
            p.append(f'row {ref}: keys outside the schema (additionalProperties:false): {extra}')
        sid = r.get('segment_id')
        if not isinstance(sid, str) or not _ID_RE.match(sid):
            p.append(f'row {ref}: segment_id is not "<domain>:<12 lowercase hex>"')
        elif sid.split(':', 1)[0] != r.get('textdomain'):
            p.append(f'row {ref}: segment_id domain != textdomain {r.get("textdomain")!r}')
        if sid in seen_ids:
            p.append(f'row {ref}: duplicate segment_id')
        seen_ids.add(sid)
        if r.get('seq') in seen_seq:
            p.append(f'row {ref}: duplicate seq {r.get("seq")}')
        seen_seq.add(r.get('seq'))
        # recompute identity from the row's own normative fields — catches a builder that
        # hashed the display form, the caret prefix, or the plural.
        if isinstance(r.get('source_en'), str) and isinstance(r.get('textdomain'), str):
            want = segment_id(r['textdomain'], None, r['source_en'])
            if sid != want:
                p.append(f'row {ref}: segment_id is not sha1(msgctxt|msgid_raw) — got {sid}, '
                         f'raw msgid hashes to {want}')
        # display discipline: null exactly when the raw counterpart is null
        for raw_k, dis_k in (('source_en', 'source_en_display'), ('target_pl', 'target_pl_display')):
            if (r.get(raw_k) is None) != (r.get(dis_k) is None):
                p.append(f'row {ref}: {dis_k} is null but {raw_k} is not (or vice versa)')
            if r.get(raw_k) is not None and r.get(dis_k) != PO.unescape(r[raw_k]):
                p.append(f'row {ref}: {dis_k} != unescape({raw_k})')
        if r.get('target_pl') == '':
            p.append(f'row {ref}: target_pl is "" — must be null when untranslated')
        if r.get('pool') not in POOLS:
            p.append(f'row {ref}: pool {r.get("pool")!r} outside the enum')
        if r.get('pool') == 'reference':
            p.append(f'row {ref}: pool=reference is never written by an export')
        if r.get('pool') == 'eval' and (not r.get('target_pl') or r.get('fuzzy')):
            p.append(f'row {ref}: pool=eval requires a non-empty target_pl and fuzzy=false')
        if r.get('placeholder_check') not in PH_CHECKS:
            p.append(f'row {ref}: placeholder_check {r.get("placeholder_check")!r} outside the enum')
        if r.get('string_class') not in STRING_CLASSES:
            p.append(f'row {ref}: string_class {r.get("string_class")!r} outside the vocabulary')
        for f in r.get('markup_flags') or []:
            if f not in MARKUP_FLAGS:
                p.append(f'row {ref}: markup_flag {f!r} outside the vocabulary')
        if r.get('char_limit') is not None and not isinstance(r['char_limit'], int):
            p.append(f'row {ref}: char_limit must be an integer or null')
        nb = r.get('neighbours')
        if not isinstance(nb, dict) or set(nb) != {'prev', 'next'}:
            p.append(f'row {ref}: neighbours must be an object with exactly prev and next')
        pf = r.get('plural_forms')
        if pf is not None:
            if not isinstance(pf, dict) or set(pf) != set(PLURAL_KEYS):
                p.append(f'row {ref}: plural_forms must be null or a complete object {PLURAL_KEYS}')
            else:
                if len(pf['target_forms']) != len(pf['target_forms_display']):
                    p.append(f'row {ref}: target_forms / target_forms_display length differ')
                for a, b in zip(pf['target_forms'], pf['target_forms_display']):
                    if b != PO.unescape(a):
                        p.append(f'row {ref}: target_forms_display != unescape(target_forms)')
                        break
                if not isinstance(pf['target_nplurals'], int) or pf['target_nplurals'] < 1:
                    p.append(f'row {ref}: target_nplurals must be a positive integer')
        if r.get('source_ref') is not None and not isinstance(r['source_ref'], list):
            p.append(f'row {ref}: source_ref must be an array of strings or null')
        by_file[r.get('file')].append(r)

    expect = list(range(len(rows)))
    if sorted(x for x in seen_seq if isinstance(x, int)) != expect:
        p.append(f'seq is not dense and 0-based over {len(rows)} rows')
    for path, block in by_file.items():
        for i, r in enumerate(block):
            want_prev = block[i - 1]['segment_id'] if i else None
            want_next = block[i + 1]['segment_id'] if i + 1 < len(block) else None
            if r['neighbours'].get('prev') != want_prev or r['neighbours'].get('next') != want_next:
                p.append(f'row {r.get("segment_id")}: neighbours do not match export order in {path}')
                break
    return p


def verify_manifest(m, rows, payload):
    p = []
    missing = [k for k in MANIFEST_KEYS if k not in m]
    if missing:
        p.append(f'manifest: missing required {missing}')
    extra = [k for k in m if k not in MANIFEST_KEYS]
    if extra:
        p.append(f'manifest: keys outside the schema (additionalProperties:false): {extra}')
    if m.get('bundle_version') != BUNDLE_VERSION:
        p.append(f'manifest: bundle_version {m.get("bundle_version")!r} != {BUNDLE_VERSION!r} '
                 '(the schema pins it with const — a bundle written against another version '
                 'of the contract must fail loudly, not validate and mean something else)')
    if m.get('source_format') != SOURCE_FORMAT:
        p.append(f'manifest: source_format must be {SOURCE_FORMAT!r}')
    up = m.get('upstream') or {}
    if set(up) != {'remote', 'commit', 'branch', 'po_revision_dates'}:
        p.append(f'manifest: upstream keys {sorted(up)} != remote/commit/branch/po_revision_dates')
    if not re.match(r'^[0-9a-f]{40}$', str(up.get('commit', ''))):
        p.append('manifest: upstream.commit is not a 40-hex sha')
    if not up.get('remote') or not up.get('branch'):
        p.append('manifest: upstream.remote / upstream.branch must be non-empty')
    prd = up.get('po_revision_dates')
    if not isinstance(prd, dict):
        p.append('manifest: upstream.po_revision_dates must be a map, not a record')
    elif sorted(prd) != sorted(m.get('textdomains') or []):
        p.append('manifest: po_revision_dates keys != textdomains')
    if not re.match(r'^[0-9a-f]{64}$', str(m.get('extraction_script_hash', ''))):
        p.append('manifest: extraction_script_hash must be 64 lowercase hex chars')
    ch = m.get('content_hash') or {}
    if ch.get('algorithm') != 'sha256' or ch.get('covers') != 'lines.jsonl':
        p.append('manifest: content_hash must be {sha256, <hex>, lines.jsonl}')
    digest = hashlib.sha256(payload).hexdigest()
    if ch.get('value') != digest:
        p.append(f'manifest: content_hash.value != sha256(lines.jsonl) ({digest})')
    if m.get('line_count') != len(rows):
        p.append(f'manifest: line_count {m.get("line_count")} != {len(rows)} rows')
    td = m.get('textdomains') or []
    if list(td) != sorted(td):
        p.append('manifest: textdomains must be byte-sorted')
    unknown = sorted({r.get('textdomain') for r in rows} - set(td))
    if unknown:
        p.append(f'manifest: rows carry textdomains absent from textdomains[]: {unknown}')
    return p


def verify_payload_bytes(payload):
    """The bytes-level half of the contract — what a re-serialisation would hide."""
    p = []
    if payload[:3] == b'\xef\xbb\xbf':
        p.append('lines.jsonl starts with a UTF-8 BOM')
    if b'\r' in payload:
        p.append('lines.jsonl contains CR (must be LF-only)')
    if b'\x00' in payload:
        p.append('lines.jsonl contains a NUL byte')
    if payload and not payload.endswith(b'\n'):
        p.append('lines.jsonl does not end with a newline')
    if payload.endswith(b'\n\n'):
        p.append('lines.jsonl ends with more than one newline')
    try:
        text = payload.decode('utf-8')
    except UnicodeDecodeError as ex:                              # pragma: no cover
        return p + [f'lines.jsonl is not valid UTF-8: {ex}']
    for i, ln in enumerate(text.split('\n')[:-1], 1):
        if not ln.strip():
            p.append(f'lines.jsonl line {i} is blank')
    return p


# ================================ 7. COMMANDS ======================================

def print_census(stats, census, textdomains, missing):
    print(f'rows (line_count):        {stats["rows"]}')
    print(f'textdomains (.pot union): {len(textdomains)}   missing a target .po: '
          f'{missing if missing else "none"}')
    print(f'plural entries:           {stats.get("plural", 0)}')
    print(f'rows with derived msgctxt:{stats.get("derived_msgctxt", 0)}')
    print(f'rows where raw != display:{stats.get("escaping_differs", 0)}')
    print(f'pool:                     {dict(sorted(census["pool"].items()))}')
    print(f'placeholder_check:        {dict(sorted(census["placeholder_check"].items()))}')
    print(f'markup_flags:             {dict(sorted(census["markup_flags"].items()))}')
    print(f'string_class:             {dict(sorted(census["string_class"].items()))}')
    if census['plural_arity_disagreements']:
        print(f'PLURAL ARITY DISAGREEMENTS ({len(census["plural_arity_disagreements"])}) — '
              'reported, NOT fixed:')
        for x in census['plural_arity_disagreements'][:20]:
            print(f'  {x}')
    for kind, ids in sorted(census['flagged_segment_ids'].items()):
        print(f'placeholder_check={kind}: {len(ids)} row(s)')
        for sid in ids[:40]:
            print(f'  {sid}')
    print('\nper-domain translated / fuzzy / untranslated:')
    for d in sorted(census['per_domain']):
        c = census['per_domain'][d]
        print(f'  {d:<22} {c.get("total", 0):>6}  {c.get("translated", 0):>6} '
              f'{c.get("fuzzy", 0):>5} {c.get("untranslated", 0):>7}')


def cmd_export(lockit, locale, out_dir, dry_run, force, po_root=None, checkout_root=None):
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    checkout_root = checkout_root or os.path.join(repo, 'sources', lockit)
    po_root = po_root or os.path.join(checkout_root, 'po')
    if not os.path.isdir(po_root):
        sys.exit(f'ERROR: {po_root} is not a directory. This exporter is gettext-only.')

    # PROVENANCE FIRST, and it is a stop condition: no degraded output path exists.
    try:
        upstream = read_upstream(checkout_root)
    except ProvenanceError as ex:
        sys.exit(f'REFUSING TO EXPORT — upstream provenance unavailable: {ex}\n'
                 'The manifest requires upstream {remote, commit, branch}. A bundle with a '
                 'fabricated or omitted upstream is invalid, and a plausible-looking one '
                 'beside a real one is the failure this check exists to prevent.')

    textdomains, missing = corpus_inventory(po_root, locale)
    if not textdomains:
        sys.exit(f'ERROR: no <domain>/<domain>.pot under {po_root}')

    errors = structural_problems(po_root, locale, textdomains)
    if errors:
        print(f'{len(errors)} STRUCTURAL error(s):', file=sys.stderr)
        for e in errors[:10]:
            print(f'  {e}', file=sys.stderr)
        if not force:
            sys.exit('REFUSING TO EXPORT: a structural error makes the rows untrustworthy. '
                     'Fix the source or re-run with --force. (Cross-locale CONTENT findings '
                     'never block — they are recorded per row in placeholder_check.)')
        print('!!! --force: exporting over structural errors', file=sys.stderr)

    rows, stats, census, revision_dates = build_rows(po_root, locale, textdomains, checkout_root)
    payload = serialize(rows)
    manifest = build_manifest(lockit, locale, rows, payload, textdomains, upstream,
                              revision_dates)

    print_census(stats, census, textdomains, missing)
    esh, files = extraction_script_hash()
    print(f'\npayload:                  {len(payload)} bytes, '
          f'sha256 {manifest["content_hash"]["value"]}')
    print(f'extraction_script_hash:   {esh}')
    print(f'  covers: {" ".join(files)}')
    print(f'upstream:                 {upstream["remote"]} @ {upstream["commit"]} '
          f'({upstream["branch"]})')
    print(f'last_changed:             null — {census["last_changed_reason"]}')

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
    os.makedirs(out_dir, exist_ok=True)
    # lines.jsonl FIRST — a torn run then leaves a bundle with no manifest (rejected on
    # sight) rather than a manifest asserting a hash for bytes that are not there.
    with open(os.path.join(out_dir, 'lines.jsonl'), 'wb') as fh:
        fh.write(payload)
    with open(os.path.join(out_dir, 'manifest.json'), 'wb') as fh:
        fh.write((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    census_path = os.path.join(os.path.dirname(out_dir.rstrip(os.sep)),
                               f'census-{lockit}-{locale}.json')
    with open(census_path, 'wb') as fh:
        fh.write((json.dumps({'stats': dict(stats), 'missing_target_domains': missing,
                              **census}, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f'wrote {out_dir}/lines.jsonl + manifest.json  (census: {census_path})')
    return 0


def cmd_check(bundle_dir, po_root=None):
    mpath = os.path.join(bundle_dir, 'manifest.json')
    lpath = os.path.join(bundle_dir, 'lines.jsonl')
    if not os.path.isfile(mpath) or not os.path.isfile(lpath):
        sys.exit(f'ERROR: {bundle_dir} is missing manifest.json and/or lines.jsonl')
    with open(lpath, 'rb') as fh:
        payload = fh.read()                      # BYTES — re-reading them is the point
    with open(mpath, 'rb') as fh:
        manifest = json.loads(fh.read().decode('utf-8'))

    problems = verify_payload_bytes(payload)
    rows = []
    for i, ln in enumerate(payload.decode('utf-8').split('\n')[:-1], 1):
        try:
            rows.append(json.loads(ln))
        except ValueError as ex:                                  # pragma: no cover
            problems.append(f'lines.jsonl line {i}: not valid JSON ({ex})')
    problems += verify_rows(rows) + verify_manifest(manifest, rows, payload)

    print(f'bundle:   {bundle_dir}')
    print(f'rows:     {len(rows)}   payload: {len(payload)} bytes')
    print(f'sha256:   {hashlib.sha256(payload).hexdigest()}  '
          f'(manifest: {manifest.get("content_hash", {}).get("value")})')

    if po_root:
        # The check only the producer can do: re-export in memory and compare BYTES. This
        # catches a text-mode write, a locale-dependent sort, or a parser change that moved
        # a string — none of which a schema can see.
        checkout_root = os.path.dirname(po_root.rstrip(os.sep))
        td = manifest.get('textdomains') or []
        fresh, _s, _c, _r = build_rows(po_root, manifest.get('target_locale'), td, checkout_root)
        fresh_payload = serialize(fresh)
        if fresh_payload == payload:
            print('re-export: REPRODUCIBLE (byte-identical)')
        else:
            a, b = fresh_payload.split(b'\n'), payload.split(b'\n')
            first = next((i for i, (x, y) in enumerate(zip(a, b), 1) if x != y), len(b) + 1)
            problems.append(f're-export DRIFT: payload differs, first differing line {first} '
                            f'({len(fresh_payload)} vs {len(payload)} bytes)')

    if problems:
        print(f'\n{len(problems)} PROBLEM(S):')
        for x in problems[:40]:
            print(f'  {x}')
        return 1
    print('\ncheck: 0 problems')
    return 0


def main(argv):
    if '--check' in argv:
        rest = [a for a in argv if a != '--check']
        if not rest:
            sys.exit('usage: export_bundle.py --check <bundle-dir> [<source-po-root>]')
        return cmd_check(rest[0], rest[1] if len(rest) > 1 else None)
    flags = {'--dry-run', '--force'}
    bad = [a for a in argv if a.startswith('--') and a not in flags]
    if bad:
        sys.exit(f'unknown flag(s): {bad}\n{__doc__}')
    pos = [a for a in argv if a not in flags]
    if len(pos) < 2:
        sys.exit(__doc__)
    lockit, locale = pos[0], pos[1]
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = pos[2] if len(pos) > 2 else os.path.join(repo, 'data', 'bundles', f'{lockit}-{locale}')
    return cmd_export(lockit, locale, out, '--dry-run' in argv, '--force' in argv)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
