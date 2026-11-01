"""Bootstrap and ENOSPC diagnostics use a separate bounded, owned channel."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import host_reports as reports
from local_release.core import ReleaseError, atomic_json, read_json
from test_retention import FakeGitHub


class ReportsAPI(FakeGitHub):
    def request(self, method, path, data=None):
        if method == 'DELETE' and path.startswith('/releases/assets/'):
            identifier = int(path.rsplit('/', 1)[1])
            for release, assets in self.assets.items():
                self.assets[release] = [a for a in assets if a['id'] != identifier]
            return
        return super().request(method, path, data)


class HostReportsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = {'project': 'fixture', 'catalogue': str(self.root),
            'profile': str(self.root / 'profile.json'), 'config': str(self.root / 'config.json')}
        atomic_json(Path(self.project['profile']), {'project': 'fixture', 'repository': 'owner/fixture'})
        atomic_json(Path(self.project['config']), {'environment': {'SECRET_TOKEN': 'private-build-secret'}})
        self.api = ReportsAPI()
        for target, kwargs in (('local_release.host_reports.GitHub', {'return_value': self.api}),
                               ('local_release.host_reports.credential', {'return_value': 'private-gh-token'})):
            mock = patch(target, **kwargs)
            mock.start()
            self.addCleanup(mock.stop)

    def test_bootstrap_failure_is_redacted_uploaded_without_job_and_imported_on_windows(self):
        self.assertTrue(reports.report_failure(self.project, 'ENOSPC private-build-secret private-gh-token'))
        bodies = b' '.join(a['bytes'] for assets in self.api.assets.values() for a in assets)
        self.assertNotIn(b'private-build-secret', bodies)
        self.assertNotIn(b'private-gh-token', bodies)
        reports.receive(self.project)
        value = read_json(self.root / 'host-reports/linux.json')
        self.assertIn('ENOSPC', value['error'])
        self.assertEqual(value['phase'], 'bootstrap')
        self.assertEqual(len(list((self.root / 'host-reports').glob('report-linux-*.json'))), 2)  # payload and receipt
        with patch.object(self.api, 'download_asset') as download:
            reports.receive(self.project)
            download.assert_not_called()

    def test_failed_delivery_has_one_bounded_outbox_and_must_drain_before_new_attempts(self):
        self.api.fail_upload = True
        for index in range(3):
            self.assertFalse(reports.report_failure(self.project, 'failed ' + str(index)))
        path = reports.outbox_path(self.project)
        self.assertEqual(len(list(self.root.glob('*.linux-outbox.json'))), 1)
        with self.assertRaises(ReleaseError):
            reports.drain(self.project)
        self.assertTrue(path.exists())
        self.api.fail_upload = False
        reports.drain(self.project)
        self.assertFalse(path.exists())

    def test_final_history_survives_mutable_progress_when_windows_is_offline(self):
        reports.publish(self.project, {'status': 'failed', 'phase': 'bootstrap', 'error': 'first error'})
        reports.publish(self.project, {'status': 'running', 'phase': 'building', 'sha': 'a' * 40})
        reports.publish(self.project, {'status': 'built', 'phase': 'cleaned', 'sha': 'a' * 40})
        reports.receive(self.project)
        history = [read_json(p) for p in (self.root / 'host-reports').glob('report-linux-*.json') if not p.name.endswith('.receipt.json')]
        self.assertEqual({p['phase'] for p in history}, {'bootstrap', 'cleaned'})

    def test_foreign_release_and_wrong_host_never_accepted(self):
        self.api.releases[2] = {'id': 2, 'tag_name': 'ai11-local-reports-fixture', 'body': 'owner note', 'draft': True}
        with self.assertRaisesRegex(ReleaseError, 'ownership'):
            reports.control(self.api, 'fixture')
        with self.assertRaisesRegex(ReleaseError, 'ownership'):
            reports.receive(self.project)


if __name__ == '__main__':
    unittest.main()
