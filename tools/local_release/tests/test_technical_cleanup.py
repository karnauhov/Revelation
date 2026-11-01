import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import host_reports, technical_cleanup
from local_release.core import ReleaseError, atomic_json, read_json
from test_host_reports import ReportsAPI


class TechnicalCleanupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = {'project': 'fixture', 'catalogue': str(self.root),
            'profile': str(self.root / 'profile.json'), 'config': str(self.root / 'config.json')}
        atomic_json(Path(self.project['profile']), {'project': 'fixture', 'repository': 'owner/fixture'})
        atomic_json(Path(self.project['config']), {'environment': {'SECRET_TOKEN': 'private-build-secret'}})
        self.api = ReportsAPI()
        self.api.token = 'private-gh-token'
        for target, value in [('local_release.host_reports.GitHub', self.api),
                              ('local_release.host_reports.credential', self.api.token)]:
            p = patch(target, return_value=value)
            p.start()
            self.addCleanup(p.stop)
        self.directory = self.root / 'releases/fixture/1.0.0+1' / self.api.sha
        job = {'project': 'fixture', 'version': '1.0.0', 'build': 1, 'sha': self.api.sha,
            'run_id': 'fixture-' + self.api.sha, 'tag': 'v1.0.0+1', 'required_steps': {'linux': ['verify-linux']}}
        atomic_json(self.directory / 'job.json', job)
        atomic_json(self.directory / 'results/linux.json', {'sha': self.api.sha, 'run_id': job['run_id'],
            'status': 'built', 'steps': {'verify-linux': {'status': 'passed'}}})
        atomic_json(self.directory / 'publication.json', {'published': True, 'release_id': 1})
        atomic_json(self.directory / 'results/exchange-closed.json', {'closed': True})
        log = self.directory / 'logs/linux/verify-linux.log'
        log.parent.mkdir(parents=True)
        log.write_text('PASS private-build-secret private-gh-token', encoding='utf-8')
        host_reports.publish(self.project, {'sha': self.api.sha, 'status': 'built', 'phase': 'cleaned'})
        self.draft_id = next(r['id'] for r in self.api.releases.values() if r['draft'])

    def test_verified_redacted_archive_precedes_draft_delete_and_no_local_zip_remains(self):
        self.assertTrue(technical_cleanup.finish(self.project, api=self.api))
        self.assertNotIn(self.draft_id, self.api.releases)
        self.assertIn(1, self.api.releases)
        asset = self.api.assets[1][0]
        with zipfile.ZipFile(io.BytesIO(asset['bytes'])) as archive:
            self.assertIn('logs/linux/verify-linux.log', archive.namelist())
            self.assertIn('host-reports/latest-linux.json', archive.namelist())
            self.assertIn('results/linux.json', archive.namelist())
            payload = b' '.join(archive.read(n) for n in archive.namelist())
        self.assertNotIn(b'private-build-secret', payload)
        self.assertNotIn(b'private-gh-token', payload)
        receipt = read_json(self.directory / 'results/build-logs.json')
        self.assertTrue(receipt['closed'])
        self.assertFalse(list(self.root.rglob('*.zip')))
        self.assertTrue((self.root / 'host-reports/linux.json').exists())
        upload = self.api.events.index(('UPLOAD', asset['name']))
        deletion = self.api.events.index(('DELETE', '/releases/' + str(self.draft_id)))
        self.assertLess(upload, deletion)
        count = len(self.api.events)
        self.assertTrue(technical_cleanup.finish(self.project, api=self.api))
        self.assertFalse(any(e[0] == 'UPLOAD' for e in self.api.events[count:]))

    def test_failed_archive_upload_preserves_draft_and_windows_logs(self):
        self.api.fail_upload = True
        with self.assertRaisesRegex(ReleaseError, 'network unavailable'):
            technical_cleanup.finish(self.project, api=self.api)
        self.assertIn(self.draft_id, self.api.releases)
        self.assertTrue((self.directory / 'logs/linux/verify-linux.log').exists())

    def test_incomplete_release_or_actionable_bootstrap_failure_is_retained(self):
        atomic_json(self.directory / 'publication.json', {'published': False, 'release_id': 1})
        self.assertFalse(technical_cleanup.finish(self.project, api=self.api))
        atomic_json(self.directory / 'publication.json', {'published': True, 'release_id': 1})
        host_reports.publish(self.project, {'status': 'failed', 'phase': 'bootstrap', 'error': 'ENOSPC'})
        self.assertFalse(technical_cleanup.finish(self.project, api=self.api))
        self.assertIn(self.draft_id, self.api.releases)

    def test_unknown_or_concurrently_received_asset_prevents_draft_cleanup(self):
        original = self.api.upload_verified
        def raced(release, path):
            result = original(release, path)
            if release['id'] == 1:
                self.api.assets[self.draft_id].append({'id': 999, 'name': 'new-data.json', 'size': 0, 'digest': 'sha256:0'})
            return result
        with patch.object(self.api, 'upload_verified', side_effect=raced):
            self.assertFalse(technical_cleanup.finish(self.project, api=self.api))
        self.assertIn(self.draft_id, self.api.releases)
        with self.assertRaisesRegex(ReleaseError, 'Unknown diagnostic'):
            technical_cleanup.finish(self.project, api=self.api)
