import json
import hashlib
import sqlite3
import struct
import tempfile
from pathlib import Path
import unittest
from contextlib import closing
from scripts.bible_module.allusion_weight_policy import POLICY_FILE, compact_policy, expand_policy, read_policy
from scripts.bible_module.build_allusion_index import compile_index
from scripts.bible_module.build_allusion_weights import ROOT, build, read_legacy, semantic_weight


class AllusionWeightTests(unittest.TestCase):
    def test_bundled_postings_reproduce_the_active_policy_canon_and_corpus(self):
        path = ROOT / 'web/db/bible_lxx_tr.sqlite'
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as database:
            database.execute('BEGIN')
            self.assertEqual(
                compile_index(database),
                (ROOT / 'assets/data/allusion_index.bin').read_bytes(),
            )

    def test_index_generator_rejects_unclassified_terms_and_noncanonical_or_duplicate_keys(self):
        with closing(sqlite3.connect(':memory:')) as database:
            database.execute('CREATE TABLE verses(verse_key TEXT, text TEXT)')
            for rows, message in [
                ([('001', 'G6000')], 'Unclassified'),
                ([('01', 'G32')], 'Invalid verse key'),
                ([('00A', 'G32'), ('00a', 'G33')], 'duplicate'),
            ]:
                with self.subTest(rows=rows):
                    database.execute('DELETE FROM verses')
                    database.executemany('INSERT INTO verses VALUES (?,?)', rows)
                    with self.assertRaisesRegex(ValueError, message):
                        compile_index(database)

    def test_grammar_negation_and_content_have_distinct_decisions(self):
        self.assertEqual(semantic_weight(2532, 'καί', '@conj', {2532})[0], 0)
        self.assertEqual(semantic_weight(3756, 'οὐ', '@particleNeg', set())[0], 0.35)
        self.assertEqual(semantic_weight(846, 'αὐτός', '@pronPers', set())[0], 0.15)
        self.assertEqual(semantic_weight(2316, 'θεός', '@noun', set())[0], 1)
        self.assertEqual(semantic_weight(3203, '', '', set())[0], 0)
        with self.assertRaises(ValueError):
            semantic_weight(10, 'unclassified lemma', '', set())

    def test_every_stored_number_reproduces_from_current_inputs(self):
        actual, _ = build(None)
        version, weights = read_policy()
        self.assertEqual(len(weights) - 1, 5624)
        entries = actual['entries']
        self.assertEqual([entries[f'G{n}']['weight'] for n in range(1, len(weights))], weights[1:])
        self.assertEqual(compact_policy(entries, version), json.loads(POLICY_FILE.read_bytes()))
        # Fingerprint of all G1-G5624 values (including sentinel 0) in the former detailed table.
        self.assertEqual(hashlib.sha256(struct.pack(f'<{len(weights)}d', *weights)).hexdigest(),
                         'db94eb0a21aa7b8618a559ca0a2f4575afe99624ff54dae8e5becdb171c70f51')
        self.assertEqual(entries['G2316']['reason'], 'lexical_word')
        self.assertGreater(entries['G2316']['verses_nt'], 1)
        self.assertNotIn('legacy_weight', entries['G2316'])
        self.assertFalse((ROOT / 'assets/data/greek_strong_weights.json').exists())

    def test_compact_policy_rejects_duplicate_and_invalid_exceptions(self):
        for groups in [{'0': [1], '0.35': [1]}, {'1.1': [2]}, {'0': [0]}, {'0': [4]}]:
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                expand_policy({'last_strong_number': 3, 'default_weight': 1, 'exceptions_by_weight': groups})

    def test_original_js_and_archived_audit_restore_the_same_manual_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input'
            for raw in ['const d={"words":[{"id":"G1","weight":0.2},]};',
                        '{"entries":{"G1":{"weight":1.0,"legacy_weight":0.2}}}']:
                path.write_text(raw, encoding='utf-8')
                self.assertEqual(read_legacy(path), {1: 0.2})


if __name__ == '__main__':
    unittest.main()
