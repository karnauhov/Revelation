import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import tarfile
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


class WindowsLogArchiveTest(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'release'
        self.api = ReportsAPI()
        self.api.token = 'private-gh-token'
        self.release = self.api.releases[1]
        self.job = {'project':'fixture','sha':self.api.sha,'run_id':'fixture-'+self.api.sha,
                    'version':'1.0.0','build':1,'tag':'v1.0.0+1','required_steps':{'windows':['verified']}}
        atomic_json(self.directory/'publication.json',{'published':True,'release_id':1,'sha':self.api.sha})
        atomic_json(self.directory/'results/windows.json',{'sha':self.api.sha,'run_id':self.job['run_id'],
                    'status':'built','steps':{'verified':{'status':'passed'}}})
        self.log=self.directory/'logs/windows/build.log';self.log.parent.mkdir(parents=True)
        self.log.write_text('PASS private-map-key private-password private-define private-gh-token',encoding='utf-8')
        atomic_json(self.root/'defines.json',{'API_KEY':'private-define'})
        config={'defines_file':str(self.root/'defines.json'),'environment':{
            'GOOGLE_MAPS_ANDROID_API_KEY':'private-map-key','SIGNING_KEY_PASSWORD':'private-password'}}
        self.context=SimpleNamespace(directory=self.directory,job=self.job,config=config)

    def orphan(self, *, extra=False, wrong_source=False):
        source = b'fixture source'
        self.job['source_bundle_sha256'] = hashlib.sha256(source).hexdigest()
        atomic_json(self.directory/'job.json', self.job)
        technical_cleanup.archive_job(self.context, self.api, self.release)
        draft = self.api.request('POST', '/releases', {'tag_name': 'untagged-ab123', 'draft': True,
            'target_commitish': self.job['sha'], 'body': '<!-- local-release:' + self.job['run_id'] + ' -->'})
        old = {**self.job, 'runtime_sha256': {}}
        if wrong_source:
            old['sha'] = 'b' * 40
        path = self.root/('local-transfer-' + self.job['run_id'] + '-job.tar.gz')
        with tarfile.open(path, 'w:gz') as archive:
            for name, content in {'job.json': json.dumps(old).encode(), 'source.bundle': source,
                                  'release_notes.txt': b'old notes'}.items():
                member = tarfile.TarInfo(name); member.size = len(content)
                archive.addfile(member, io.BytesIO(content))
        self.api.upload_verified(draft, path)
        if extra:
            self.api.assets[draft['id']].append({'id': 999, 'name': 'unarchived-logs.zip', 'size': 1})
        return draft

    def test_redundant_untagged_handoff_removed_only_after_durable_publication_proofs(self):
        draft = self.orphan()
        result = technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        self.assertTrue(result['closed'])
        self.assertNotIn(draft['id'], self.api.releases)
        self.assertIn(self.release['id'], self.api.releases)
        receipt = read_json(self.directory/'results/orphan-drafts-closed.json')
        self.assertTrue(receipt['drafts'][str(draft['id'])]['closed'])
        count = len(self.api.events)
        technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        self.assertFalse(any(e[0]=='DELETE' for e in self.api.events[count:]))

    def test_orphan_with_unknown_assets_or_other_source_is_preserved(self):
        for args in [{'extra': True}, {'wrong_source': True}]:
            with self.subTest(args=args):
                draft = self.orphan(**args)
                with self.assertRaises(ReleaseError):
                    technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
                self.assertIn(draft['id'], self.api.releases)
                self.api.releases.pop(draft['id'])
                self.api.assets.pop(draft['id'])

    def test_orphan_cleanup_retains_incomplete_release_and_unverified_diagnostics(self):
        draft = self.orphan()
        atomic_json(self.directory/'publication.json', {'published':False})
        with self.assertRaisesRegex(ReleaseError, 'published source'):
            technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        atomic_json(self.directory/'publication.json', {'published':True,'release_id':1,'sha':self.api.sha})
        atomic_json(self.directory/'results/build-logs.json', {'closed':False})
        with self.assertRaisesRegex(ReleaseError, 'archived diagnostics'):
            technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        self.assertIn(draft['id'], self.api.releases)

    def test_foreign_draft_is_ignored_and_public_or_wrong_source_run_is_never_deleted(self):
        draft = self.orphan()
        self.api.releases[draft['id']]['body'] = 'owner draft'
        self.assertTrue(technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)['closed'])
        self.assertIn(draft['id'], self.api.releases)
        self.api.releases[draft['id']]['body'] = draft['body']
        for changes in [{'draft':False}, {'target_commitish':'b'*40}]:
            self.api.releases[draft['id']].update(changes)
            with self.assertRaisesRegex(ReleaseError, 'identity mismatch'):
                technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
            self.assertIn(draft['id'], self.api.releases)
            self.api.releases[draft['id']] = dict(draft)

    def test_orphan_receipt_recovers_when_delete_succeeded_but_response_was_lost(self):
        draft = self.orphan()
        original = self.api.request
        def lost(method, path, data=None):
            value = original(method, path, data)
            if method=='DELETE':
                self.assertTrue((self.directory/'results/orphan-drafts-closed.json').is_file())
                raise ReleaseError('lost delete response')
            return value
        with patch.object(self.api, 'request', side_effect=lost):
            with self.assertRaisesRegex(ReleaseError, 'lost delete response'):
                technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        self.assertNotIn(draft['id'], self.api.releases)
        self.assertTrue(technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)['closed'])

    def test_new_asset_arriving_during_orphan_verification_prevents_delete(self):
        draft = self.orphan()
        original = self.api.download_asset
        def raced(asset, destination):
            result = original(asset, destination)
            self.api.assets[draft['id']].append({'id':999,'name':'new-data.json','size':1,'digest':'sha256:fixture'})
            return result
        with patch.object(self.api, 'download_asset', side_effect=raced):
            with self.assertRaisesRegex(ReleaseError, 'changed during verification'):
                technical_cleanup.retire_redundant_drafts(self.context, self.api, self.release)
        self.assertIn(draft['id'], self.api.releases)

    def test_single_windows_host_without_linux_draft_archives_redacted_results_once(self):
        record=technical_cleanup.archive_job(self.context,self.api,self.release)
        self.assertTrue(record['closed'] and record['read_back_verified'])
        asset=self.api.assets[1][0]
        with zipfile.ZipFile(io.BytesIO(asset['bytes'])) as archive:
            self.assertIn('logs/windows/build.log',archive.namelist())
            self.assertIn('results/windows.json',archive.namelist())
            payload=b' '.join(archive.read(n) for n in archive.namelist())
        for secret in [b'private-map-key',b'private-password',b'private-define',b'private-gh-token']:
            self.assertNotIn(secret,payload)
        self.assertEqual(len(self.api.releases),1)
        self.assertFalse(list(self.root.rglob('*.zip')))
        atomic_json(self.directory/'results/build-logs-outbox.json',{'pending':True})
        technical_cleanup.archive_job(self.context,self.api,self.release)
        self.assertEqual(sum(e[0]=='UPLOAD' for e in self.api.events),1)
        self.assertFalse((self.directory/'results/build-logs-outbox.json').exists())

    def test_failed_archival_leaves_durable_outbox_and_all_source_logs_for_retry(self):
        self.api.fail_upload=True
        with self.assertRaises(ReleaseError):technical_cleanup.archive_job(self.context,self.api,self.release)
        self.assertTrue(read_json(self.directory/'results/build-logs-outbox.json')['pending'])
        self.assertTrue(self.log.exists())
        self.assertFalse((self.directory/'results/build-logs.json').exists())
        self.api.fail_upload=False
        technical_cleanup.archive_job(self.context,self.api,self.release)
        self.assertFalse((self.directory/'results/build-logs-outbox.json').exists())

    def test_incomplete_or_foreign_publication_cannot_archive_or_claim_success(self):
        for patch_data in [{'published':False,'release_id':1,'sha':self.api.sha},
                           {'published':True,'release_id':999,'sha':self.api.sha}]:
            atomic_json(self.directory/'publication.json',patch_data)
            with self.assertRaises(ReleaseError):technical_cleanup.archive_job(self.context,self.api,self.release)
        self.assertFalse(self.api.assets)
