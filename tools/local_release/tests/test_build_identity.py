"""A skipped commit needs an explicit new number before a different SHA builds."""
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json, ensure_unique_build, prepare, capture, git


class BuildIdentityTests(unittest.TestCase):
    def test_real_prepare_rejects_second_commit_without_creating_duplicate_job(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / 'repo'
            capture(['git', 'init', repo])
            git(repo, 'config', 'user.name', 'Fixture')
            git(repo, 'config', 'user.email', 'fixture@example.invalid')
            git(repo, 'config', 'commit.gpgsign', 'false')
            git(repo, 'config', 'core.hooksPath', str(root / 'no-hooks'))
            (repo / 'source.txt').write_text('first')
            git(repo, 'add', '.')
            git(repo, 'commit', '-m', 'first [skip ci]')
            first = git(repo, 'rev-parse', 'HEAD')
            profile = root / 'profile.json'
            atomic_json(profile, {'project': 'fixture', 'repository': 'fixture/repo', 'adapter': 'fixture'})
            adapter = SimpleNamespace(metadata=lambda *args: {'version': '1.0.0', 'build': 12,
                'release_notes': 'Fixture', 'artifacts': [], 'required_steps': {}})
            with patch('local_release.core.importlib.import_module', return_value=adapter):
                prepared = prepare(repo, profile, root / 'catalogue')
                (repo / 'source.txt').write_text('second')
                git(repo, 'commit', '-am', 'second [skip ci]')
                with self.assertRaisesRegex(ReleaseError, 'already reserved'):
                    prepare(repo, profile, root / 'catalogue')
                self.assertEqual(prepare(repo, profile, root / 'catalogue', first), prepared)
                self.assertEqual(len(list((root / 'catalogue/releases/fixture').glob('*/*/job.json'))), 1)

    def test_another_sha_cannot_reuse_reserved_number_but_resume_and_new_number_work(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            atomic_json(root / 'releases/tapnibbles/1.0.0+12' / ('a' * 40) / 'job.json',
                        {'sha': 'a' * 40, 'build': 12})
            ensure_unique_build(root, 'tapnibbles', 12, 'a' * 40)
            ensure_unique_build(root, 'tapnibbles', 13, 'b' * 40)
            ensure_unique_build(root, 'other-project', 12, 'b' * 40)
            with self.assertRaisesRegex(ReleaseError, 'already reserved'):
                ensure_unique_build(root, 'tapnibbles', 12, 'b' * 40)

    def test_archive_and_deleted_build_numbers_cannot_be_reassigned(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            atomic_json(root / 'releases/tapnibbles/1.0.0+12' / ('a' * 40) / 'manifest.json',
                        {'sha': 'a' * 40, 'build': 12})
            with self.assertRaises(ReleaseError):
                ensure_unique_build(root, 'tapnibbles', 12, 'b' * 40)
            atomic_json(root / 'deletions/tapnibbles' / ('a' * 40 + '.json'),
                        {'request': {'sha': 'a' * 40, 'build': 11}})
            with self.assertRaises(ReleaseError):
                ensure_unique_build(root, 'tapnibbles', 11, 'b' * 40)


if __name__ == '__main__':
    unittest.main()
