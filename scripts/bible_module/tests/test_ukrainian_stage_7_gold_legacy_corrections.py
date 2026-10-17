"""CC0 regression for historical class accounting and strict isolation."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.bible_module import ukrainian_stage_7_gold as gold
from scripts.bible_module import ukrainian_stage_7_gold_compare as qc
from scripts.bible_module import ukrainian_stage_7_gold_legacy_corrections as legacy


def fixture(book):
    base = {}
    for key in ('a', 'b', 'c'):
        base['original:' + key] = {
            'record_type': 'original_decision', 'decision_id': key,
            'original_token_id': 'raw:' + key, 'group_original_token_ids': ['raw:' + key],
            'target_token_ids': [], 'relation': 'original_omitted',
            'null_reason': 'translation_omission', 'target_ref': book + '.1.1',
            'decision_status': 'decided', 'severity': 'normal', 'phenomena': ['omission'],
        }
    errors = {'original:a'} if book == 'Isa' else set()
    agreed = {'original:b'}
    changed = errors | agreed
    proposal = {'target_ref': book + '.1.1', 'proposal_only_no_mutation_performed': True,
                'rows_requiring_semantic_change': sorted(changed),
                'recommended_semantics_by_stable_key': {k: copy.deepcopy(base[k]) for k in changed}}
    if book == 'Isa':
        proposal.update(unchanged_reciprocal_row_to_revalidate='original:c',
                        verse_local_rows_to_revalidate=sorted(changed | {'original:c'}))
    reported = changed if book == 'Dan' else errors
    manifest = {'reviewer_id': 'independent', 'error_stable_keys': sorted(reported),
                'error_count': len(reported), 'uncertain_count': 0,
                'agreed_link_audit': {'error_stable_keys': sorted(agreed), 'error_count': 1,
                    'checked_count': 2, 'by_verse': {book + '.1.1': 2}},
                'correction_proposals': [proposal]}
    rows = [{'record_type': 'qc_adjudication_result', 'stable_key': 'original:a',
             'verdict': 'error' if errors else 'accepted', 'reviewer_id': 'independent',
             'adjudication_semantics': gold._semantic_for_key(base['original:a'])}]
    return manifest, rows, base, {'original:a'}


class LegacyCorrectionContractTest(unittest.TestCase):
    def test_distinct_historical_error_classes_prove_exact_union(self):
        for book in ('Dan', 'Isa'):
            with self.subTest(book=book):
                scope = legacy._error_scope(book, *fixture(book))
                self.assertEqual(scope[0], {'original:b'} if book == 'Dan' else {'original:a', 'original:b'})
                self.assertEqual(scope[2], {'original:a', 'original:c'} if book == 'Dan' else {'original:c'})

    def test_missing_or_duplicate_qc_observation_is_not_accounted(self):
        m, rows, base, keys = fixture('Isa')
        for bad in ([], rows + rows):
            with self.subTest(rows=len(bad)), self.assertRaisesRegex(ValueError, 'accounting|scope'):
                legacy._error_scope('Isa', m, bad, base, keys)

    def test_error_classes_cannot_hide_wrong_semantics_or_reviewer(self):
        for field, value in [('reviewer_id', 'author'), ('adjudication_semantics', {})]:
            m, rows, base, keys = fixture('Isa')
            rows[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'scope/semantics'):
                legacy._error_scope('Isa', m, rows, base, keys)

    def test_wrong_agreed_scope_or_proposal_union_rejected(self):
        for field in ('agreed', 'proposal', 'classes', 'revalidate'):
            m, rows, base, keys = fixture('Isa')
            if field == 'agreed': m['agreed_link_audit']['error_stable_keys'] = ['original:a']
            if field == 'proposal': m['correction_proposals'][0]['rows_requiring_semantic_change'] = ['original:a']
            if field == 'classes': m['error_count'] = 3
            if field == 'revalidate': m['correction_proposals'][0]['unchanged_reciprocal_row_to_revalidate'] = 'original:a'
            with self.subTest(field=field), self.assertRaises(ValueError):
                legacy._error_scope('Isa', m, rows, base, keys)

    def test_exact_pins_required_and_unknown_book_fails(self):
        for book in ('Gen', 'Dan', 'Isa'):
            with self.subTest(book=book), self.assertRaisesRegex(ValueError, 'Unknown|exact SHA'):
                legacy.validated_legacy_corrected_book(book, {})

    def test_public_strict_validator_keeps_original_refusal_before_payload(self):
        args = {name + '_path': Path(name) for name in
                ('pass1', 'pass2', 'comparison', 'adjudication', 'blocking_qc', 'correction', 'final_qc')}
        with patch.object(qc, 'validate_consensus_correction_shard', side_effect=ValueError('strict original refusal')):
            with patch.object(qc, '_validate_post_consensus_qc_payload') as payload:
                with self.assertRaisesRegex(ValueError, 'strict original refusal'):
                    qc.validate_post_consensus_correction_qc(**args)
                payload.assert_not_called()


if __name__ == '__main__':
    unittest.main()
