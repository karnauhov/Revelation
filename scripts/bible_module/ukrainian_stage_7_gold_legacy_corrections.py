"""Exact frozen Dan/Isa correction contracts; strict public validators unchanged.

These two accepted 2026-09-12 chains distinguish agreed-row errors from
adjudication errors differently from the later strict schema. No artifact is
rewritten. Only the six exact accepted correction/QC digests per book are
eligible for this adapter, followed by full independent final-QC validation.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.bible_module import ukrainian_stage_7_gold_compare as qc
from scripts.bible_module import ukrainian_stage_7_gold as gold
from scripts.bible_module.ukrainian_stage_7_model import sha256_text, stable_json

_NAMES = ('blocking_qc', 'blocking_qc_manifest', 'consensus_correction',
          'consensus_correction_manifest', 'final_qc', 'final_qc_manifest')
_PINS = {
    'Dan': dict(zip(_NAMES, (
        '383c1b10ecca8ece71f223c6d7595b568abb7bae6009bc4a2976cab4f0f46d6d',
        'f63c1879f2a055ce71496bccf3a2a380d2e31e290911971bf4e120e1bfe787dd',
        '0f8dbcdf36ad9673a7d39b77200a86a16a65e390e70e61697b5ecb723a11759b',
        'c5a9e82ebad3241d6f0ab3995a444e98667565da9bc389c16b2e3abcf6ac6887',
        'f0fd43937176dd5e6f206e68adcebd761cd33be9cbaf25829ab1dd4781480574',
        'ceb8b61fc55850759f0a3a5e5b2866181b091f7c04280dbf7b414142d048360f'))),
    'Isa': dict(zip(_NAMES, (
        'f4890fdb6afa16b0755ac3d0c764bbac80249e443a334b2901eb59ed43664b18',
        '0031caca33fe30d2979cd8b998b12ed9e6b20ea7f7ce4362f73a5ac39779f701',
        '929320462dc00f8fbada2c407e91708d19e9e16ac2dc9d63106806e075aa57ba',
        '000b4591d7177712c203e3d4b3216ebec50fcca792c12711618f329d3a3264f3',
        '31879520ca4548dbaf8191e7e471d42a73df6d831b46ae5fdb670ca2563a9676',
        'e4c292e968baf722c6d52ca2682022b2f7362fd031124b4b00153c8038b35c0e'))),
}


def _error_scope(book: str, manifest: Mapping[str, Any], observations: Sequence[Mapping[str, Any]],
                 base: Mapping[str, Any], adjudicated: set[str]):
    """Prove the historical error classes and proposal union without mutation."""
    if book not in _PINS:
        raise ValueError('Unknown historical correction contract')
    seen = set()
    errors = set()
    for row in observations:
        key = row.get('stable_key')
        if (key in seen or key not in adjudicated or row.get('record_type') != 'qc_adjudication_result'
                or row.get('verdict') not in {'accepted', 'error'}
                or row.get('adjudication_semantics') != gold._semantic_for_key(base[key])
                or row.get('reviewer_id') != manifest.get('reviewer_id')):
            raise ValueError('Historical blocking QC observation scope/semantics differs')
        seen.add(key)
        if row['verdict'] == 'error': errors.add(key)
    if seen != adjudicated:
        raise ValueError('Historical blocking QC adjudication accounting incomplete')
    audit = manifest['agreed_link_audit']
    agreed = set(audit['error_stable_keys'])
    if (len(agreed) != len(audit['error_stable_keys']) or not agreed
            or not agreed <= set(base) - adjudicated or audit['error_count'] != len(agreed)
            or audit['checked_count'] != len(base) - len(adjudicated)):
        raise ValueError('Historical agreed-row error accounting differs')
    expected_verses = Counter(base[k]['target_ref'] for k in set(base) - adjudicated)
    if dict(expected_verses) != audit['by_verse']:
        raise ValueError('Historical agreement verse accounting differs')
    # Dan reports the aggregate five agreed errors, Isaiah the two
    # adjudication errors separately from its one agreed target error.
    reported = errors | agreed if book == 'Dan' else errors
    if (set(manifest['error_stable_keys']) != reported
            or set(manifest.get('verdict_stable_keys', {}).get('error', manifest['error_stable_keys'])) != reported
            or manifest['error_count'] != len(reported)
            or manifest.get('uncertain_count') != 0
            or manifest.get('verdict_stable_keys', {}).get('uncertain', []) != []):
        raise ValueError('Historical blocking QC error classes differ')
    proposals = manifest['correction_proposals']
    if len(proposals) != 1:
        raise ValueError('Historical correction proposal count differs')
    proposal = proposals[0]
    changed_list = proposal['rows_requiring_semantic_change']
    changed = set(changed_list)
    if (len(changed) != len(changed_list) or changed != errors | agreed
            or proposal.get('proposal_only_no_mutation_performed') is not True
            or set(proposal['recommended_semantics_by_stable_key']) != changed
            or {base[k]['target_ref'] for k in changed} != {proposal['target_ref']}):
        raise ValueError('Historical correction proposal scope differs')
    if book == 'Dan':
        revalidate = {k for k, v in base.items() if v['target_ref'] == proposal['target_ref']} - changed
        # This exact old Dan proposal derives the remaining full verse from
        # the frozen grid; its post-correction QC enumerates all 23 rows.
        if ('unchanged_reciprocal_revalidation' in proposal
                and set(proposal['unchanged_reciprocal_revalidation']) != revalidate):
            raise ValueError('Historical full-locus revalidation scope differs')
    else:
        revalidate = {proposal['unchanged_reciprocal_row_to_revalidate']}
        if (not revalidate <= set(base) - changed
                or set(proposal['verse_local_rows_to_revalidate']) != changed | revalidate
                or any(base[k]['target_ref'] != proposal['target_ref'] for k in revalidate)):
            raise ValueError('Historical reciprocal revalidation scope differs')
    return changed, {proposal['target_ref']}, revalidate


def validated_legacy_corrected_book(book: str, chain: Mapping[str, Path]):
    if book not in _PINS:
        raise ValueError('Unknown historical correction contract')
    for name, digest in _PINS[book].items():
        if name not in chain or not chain[name].is_file() or gold._sha256_file(chain[name]) != digest:
            raise ValueError('Historical correction exact SHA differs: ' + name)
    for name in ('blocking_qc', 'consensus_correction', 'final_qc'):
        if Path(str(chain[name]) + '.manifest.json').resolve() != chain[name + '_manifest'].resolve():
            raise ValueError('Historical correction exact sidecar pair differs')
    args = {name + '_path': chain[name] for name in ('pass1', 'pass2', 'comparison', 'adjudication')}
    values = list(qc._validated_post_adjudication_values(**args))
    metadata1, metadata2, first, second, base, adjudicator = values
    if {r['target_ref'].split('.')[0] for r in base.values()} != {book}:
        raise ValueError('Historical corrected book scope differs')
    blocking = list(gold._read_jsonl(chain['blocking_qc']))
    headers = [r for r in blocking if r.get('record_type') == 'qc_metadata']
    manifest = gold._read_json(chain['blocking_qc_manifest'])
    if len(headers) != 1:
        raise ValueError('Historical blocking QC metadata scope differs')
    header = headers[0]
    for field, expected in [('status', 'complete_qc_errors_found'), ('overall_verdict', 'error'), ('shard_blocked', True)]:
        if header.get(field) != expected or manifest.get(field) != expected:
            raise ValueError('Historical blocking QC verdict differs')
    if (header['reviewer_id'] != manifest['reviewer_id'] or header['input_sha256'] != manifest['input_sha256']
            or manifest['output_sha256'].get(chain['blocking_qc'].name) != gold._sha256_file(chain['blocking_qc'])):
        raise ValueError('Historical blocking QC header/sidecar differs')
    for name in ('pass1', 'pass2', 'comparison', 'adjudication'):
        for suffix in ('', '_manifest'):
            if gold._sha256_file(chain[name + suffix]) not in manifest['input_sha256'].values():
                raise ValueError('Historical blocking QC source lock differs')
    adj_rows = [r for r in gold._read_jsonl(chain['adjudication']) if r.get('record_type') != 'adjudication_shard_metadata']
    adjudicated = {qc._key(r) for r in adj_rows}
    scope = _error_scope(book, manifest, [r for r in blocking if r.get('record_type') != 'qc_metadata'], base, adjudicated)
    changed, _, revalidate = scope
    if (len(changed), len(revalidate), len(base)) != ((5, 23, 1565) if book == 'Dan' else (3, 1, 1365)):
        raise ValueError('Historical fixed correction dimensions differ')
    correction = list(gold._read_jsonl(chain['consensus_correction']))
    correction_headers = [r for r in correction if r.get('record_type') == 'consensus_correction_metadata']
    if len(correction_headers) != 1:
        raise ValueError('Historical correction metadata scope differs')
    ch = correction_headers[0]
    author = ch.get('correction_reviewer_id')
    frozen_authors = {r['reviewer_id'] for r in (*first.values(), *second.values())} | {adjudicator}
    prior_authors = frozen_authors | {manifest['reviewer_id']}
    if not author or author in prior_authors or manifest['reviewer_id'] in frozen_authors:
        raise ValueError('Historical correction reviewer independence differs')
    if (ch.get('status') != 'complete_manual_consensus_correction_pending_independent_qc'
            or ch.get('correction_version') != qc.CONSENSUS_CORRECTION_VERSION
            or ch.get('expected_changed_stable_keys') != sorted(changed)
            or ch.get('expected_changed_stable_keys_sha256') != sha256_text(stable_json(sorted(changed)))):
        raise ValueError('Historical correction header/scope differs')
    for name in ('pass1', 'pass2', 'comparison', 'adjudication', 'blocking_qc'):
        label = {'pass1':'pass_1', 'pass2':'pass_2'}.get(name, name)
        for suffix in ('', '_manifest'):
            if ch.get(label + suffix + '_sha256') != gold._sha256_file(chain[name + suffix]):
                raise ValueError('Historical correction source digest differs')
    corrections = [r for r in correction if r.get('record_type') != 'consensus_correction_metadata']
    if [qc._key(r) for r in corrections] != sorted(changed):
        raise ValueError('Historical correction exact-once scope differs')
    for row in corrections:
        key = qc._key(row)
        if (row.get('reviewer_id') != author or not gold._evidence_ok(row.get('evidence'))
                or not str(row.get('rationale', '')).strip()
                or row.get('supersedes_alignment_sha256') != sha256_text(stable_json(gold._alignment_for_key(base[key])))
                or gold._alignment_for_key(row) == gold._alignment_for_key(base[key])
                # Proposals establish link/null topology. The distinct final
                # QC below verifies the corrector's complete metadata too.
                or gold._alignment_for_key(row) != gold._alignment_for_key(manifest['correction_proposals'][0]['recommended_semantics_by_stable_key'][key])):
            raise ValueError('Historical correction semantics/evidence/supersedes differs')
    corrected = {**base, **{qc._key(r): r for r in corrections}}
    gold._validate_final_grid(corrected, first)
    gold._validate_semantic_accounting(
        {k.removeprefix('original:'):v for k,v in corrected.items() if k.startswith('original:')},
        {k.removeprefix('target:'):v for k,v in corrected.items() if k.startswith('target:')})
    qc._validate_post_consensus_qc_payload(**args, blocking_qc_path=chain['blocking_qc'],
        correction_path=chain['consensus_correction'], final_qc_path=chain['final_qc'],
        correction_scope=scope,
        correction_result={'status':'valid_exact_historical_consensus_correction_pending_independent_qc'})
    values[4] = corrected
    return tuple(values)
