import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import atomic_json, capture, git, ReleaseError
from local_release.retention_notes import Notes, REF


class NotesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.repo, self.remote = root / 'owner', root / 'remote.git'
        self.repo.mkdir()
        git(self.repo, 'init', '-b', 'main')
        git(self.repo, 'config', 'user.name', 'Fixture')
        git(self.repo, 'config', 'user.email', 'fixture@example.invalid')
        (self.repo / 'source.txt').write_text('original')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-m', '[REV301] Fixture [skip ci]')
        self.sha = git(self.repo, 'rev-parse', 'HEAD')
        capture(['git', 'clone', '--bare', self.repo, self.remote])
        git(self.repo, 'remote', 'add', 'origin', str(self.remote))
        profile = root / 'profile.json'
        atomic_json(profile, {'project': 'fixture', 'repository': 'owner/fixture', 'retention_task_code': 'REV301'})
        self.project = {'repo': str(self.repo), 'profile': str(profile), 'catalogue': str(root / 'state'), 'project': 'fixture'}
        self.request = {'schema': 1, 'project': 'fixture', 'repository': 'owner/fixture', 'sha': self.sha,
            'request_id': 'a' * 32, 'version': '1.0.0', 'build': 1, 'hosts': ['windows', 'linux'],
            'release_tag': 'v1.0.0+1'}

    def store(self):
        return Notes(self.project, check_origin=False)

    def test_notes_roundtrip_preserves_main_index_dirty_files_and_reuses_unchanged_record(self):
        (self.repo / 'source.txt').write_text('owner dirty change')
        git(self.repo, 'add', 'source.txt')
        before = git(self.repo, 'write-tree')
        store = self.store()
        record = {'request': self.request, 'acks': {}}
        first = store.sync(record)
        self.assertEqual(store.sync(record)['commit'], first['commit'])
        record['acks']['windows'] = True
        second = self.store().sync(record)
        self.assertNotEqual(first['commit'], second['commit'])
        self.assertEqual(git(self.repo, 'rev-parse', 'HEAD'), self.sha)
        self.assertEqual(git(self.repo, 'write-tree'), before)
        self.assertEqual((self.repo / 'source.txt').read_text(), 'owner dirty change')
        self.assertEqual(json.loads(git(self.repo, 'notes', '--ref=' + REF, 'show', self.sha))['acks'], {'windows': True})
        messages = git(self.repo, 'log', '--format=%B', REF)
        self.assertEqual(messages.count('[skip ci]'), 2)

    def test_conflicting_request_and_wrong_origin_are_rejected(self):
        self.store().sync({'request': self.request})
        with self.assertRaisesRegex(ReleaseError, 'Conflicting'):
            self.store().sync({'request': {**self.request, 'request_id': 'b' * 32}})
        with self.assertRaisesRegex(ReleaseError, 'origin differs'):
            Notes(self.project)

    def test_concurrent_append_is_refetched_without_force_push_or_lost_tombstone(self):
        other = 'b' * 40
        record = {'request': self.request}
        second = self.store()
        original = second.git
        fired = False
        def raced(*args, **kwargs):
            nonlocal fired
            if args[0] == 'push' and not fired:
                fired = True
                # Separate catalogue lock models another OS/checkout.
                project = {**self.project, 'catalogue': str(self.repo / 'other-control')}
                Notes(project, check_origin=False).sync({'request': {**self.request,
                    'sha': other, 'request_id': 'b' * 32}})
            return original(*args, **kwargs)
        with patch.object(second, 'git', side_effect=raced):
            second.sync(record)
        self.assertEqual(set(self.store().read()), {self.sha, other})
        self.assertEqual(git(self.repo, 'rev-parse', 'HEAD'), self.sha)

    def test_unavailable_remote_never_confirms_delivery(self):
        git(self.repo, 'remote', 'set-url', 'origin', str(self.repo / 'missing.git'))
        with self.assertRaisesRegex(ReleaseError, 'not confirmed'):
            self.store().sync({'request': self.request})
