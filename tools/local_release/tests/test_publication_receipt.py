from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, _run_job, atomic_json, digest, read_json
from local_release.github import reconcile_published, publish_job, repair_publication_urls


class PublicationReceiptTest(unittest.TestCase):
    def test_repeated_publish_keeps_public_release_with_a_later_log_archive_immutable(self):
        saved = {'published': True, 'sha': self.job['sha'], 'release_id': 1}
        atomic_json(self.directory / 'publication.json', saved)
        atomic_json(self.directory / 'results/build-logs.json', {'archive': {'id': 99}, 'closed': True})
        before = (self.directory / 'publication.json').read_bytes()
        with patch('local_release.github.credential', return_value='fixture'), patch('local_release.github.GitHub') as api:
            self.assertEqual(publish_job(self.context), saved)
            api.return_value.request.assert_not_called()
            api.return_value.upload_verified.assert_not_called()
        self.assertEqual((self.directory / 'publication.json').read_bytes(), before)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "releases/fixture/1.0.0+1" / ("a" * 40)
        self.job = {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture", "repository": "owner/repo",
            "version": "1.0.0", "build": 1, "tag": "v1.0.0+1", "source_bundle_sha256": "b" * 64,
            "compile_defines_sha256": "c" * 64, "artifacts": ["linux.tar.gz"],
            "required_steps": {"windows": ["integration-web"], "linux": ["verify-linux"]}}
        atomic_json(self.directory / "job.json", self.job)
        atomic_json(self.directory / "publication.json", {"release_id": 1, "published": False})
        self.context = Context(self.directory, {}, host="linux")
        self.summary = {key: self.job[key] for key in ("run_id", "sha", "version", "build", "tag", "source_bundle_sha256", "compile_defines_sha256")}
        self.summary.update(verified_gates=deepcopy(self.job["required_steps"]), packages={"linux.tar.gz": {
            "sha256": hashlib.sha256(b"package").hexdigest(), "size": 7}})
        self.release = {"id": 1, "draft": False, "tag_name": self.job["tag"], "body": "<!-- local-release:fixture-a -->",
                        "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0+1"}

    def prepare_draft(self, api):
        fields = {'runtime_sha256': {}, 'profile': {'adapter': 'local_release.profiles.tapnibbles'}}
        self.job.update(fields)
        self.context.job.update(fields)
        atomic_json(self.directory / 'job.json', self.job)
        (self.directory / 'release_notes.txt').write_text('Fixture notes', encoding='utf-8')
        name = 'linux.tar.gz'
        path = self.context.output / name
        path.write_bytes(b'package')
        for host, gates in self.job['required_steps'].items():
            atomic_json(self.directory / f'results/{host}.json', {
                **{key: self.job[key] for key in ('sha', 'run_id', 'compile_defines_sha256')},
                'steps': {gates[0]: {'status': 'passed', 'outputs': (
                    {'packages/' + name: digest(path)} if host == 'linux' else {})}},
            })
        atomic_json(self.directory / 'manifest.json', {
            **{key: self.job[key] for key in ('project', 'sha', 'run_id', 'version', 'build')},
            'packages': {name: {'sha256': digest(path), 'size': 7, 'path': 'packages/' + name}},
        })
        self.draft = True
        self.fail_patch = None
        self.inventory = {}
        self.remote_calls = []

        def url(name):
            tag = 'untagged-deadbeef' if self.draft else 'v1.0.0%2B1'
            return 'https://github.com/Owner/Repo/releases/download/' + tag + '/' + name

        def upload(release, path, *, allow_upload):
            self.assertTrue(allow_upload)
            record = {'id': len(self.inventory) + 2, 'size': path.stat().st_size,
                      'sha256': digest(path), 'url': url(path.name), 'asset_name': path.name}
            self.inventory[path.name] = {'id': record['id'], 'name': path.name, 'size': record['size'],
                                         'digest': 'sha256:' + record['sha256'], 'state': 'uploaded'}
            return record

        def release():
            return dict(self.release, draft=self.draft, target_commitish=self.job['sha'],
                        tag_name='untagged-deadbeef' if self.draft else self.job['tag'])

        def request(method, path, data=None):
            self.remote_calls.append(method)
            self.assertEqual(path, '/releases/1')
            if method == 'PATCH':
                self.assertTrue(self.draft)
                self.assertEqual(data['tag_name'], self.job['tag'])
                if self.fail_patch != 'before':
                    self.draft = False
                if self.fail_patch:
                    raise TimeoutError('Publication response lost')
            else:
                self.assertEqual(method, 'GET')
            return release()

        api.ensure_release.side_effect = lambda *args: release()
        api.request.side_effect = request
        api.upload_verified.side_effect = upload
        api.tag_sha.side_effect = lambda tag: None if self.draft else self.job['sha']
        api.pages.side_effect = lambda path: [dict(a, browser_download_url=url(n)) for n, a in self.inventory.items()]

    def assert_canonical(self, receipt):
        self.assertTrue(receipt['published'])
        self.assertNotIn('awaiting_publication_confirmation', receipt)
        assets = receipt['assets']
        for record in [*assets.values(), receipt['manifest'], receipt['checksums']]:
            self.assertIn('/download/v1.0.0%2B1/', record['url'])
            self.assertEqual(record['id'], self.inventory[record['asset_name']]['id'])
        self.assertEqual(read_json(self.directory / 'manifest.json')['packages']['linux.tar.gz']['url'],
                         assets['linux.tar.gz']['url'])

    @patch('local_release.github.credential', return_value='fixture')
    @patch('local_release.github.GitHub')
    def test_publication_refreshes_all_draft_urls_from_final_inventory(self, github, credential):
        self.prepare_draft(github.return_value)
        self.assert_canonical(publish_job(self.context))
        self.assertEqual(self.remote_calls, ['PATCH', 'GET'])

    @patch('local_release.github.credential', return_value='fixture')
    @patch('local_release.github.GitHub')
    def test_lost_patch_response_resumes_without_reupload_or_second_patch(self, github, credential):
        api = github.return_value
        self.prepare_draft(api)
        self.fail_patch = 'after'
        with self.assertRaises(TimeoutError):
            publish_job(self.context)
        pending = read_json(self.directory / 'publication.json')
        self.assertTrue(pending['awaiting_publication_confirmation'])
        self.assertFalse(pending['published'])
        self.assertIn('/untagged-', pending['assets']['linux.tar.gz']['url'])
        self.remote_calls.clear()
        api.upload_verified.reset_mock()
        self.assert_canonical(publish_job(self.context))
        self.assertEqual(set(self.remote_calls), {'GET'})
        api.upload_verified.assert_not_called()

    @patch('local_release.github.credential', return_value='fixture')
    @patch('local_release.github.GitHub')
    def test_builder_retry_skips_exchange_and_preserves_completed_evidence(self, github, credential):
        self.prepare_draft(github.return_value)
        self.fail_patch = 'after'
        with (patch('local_release.core.host_name', return_value='windows'),
              patch('local_release.core.verify_runtime'), patch.object(Context, 'checkout'),
              patch.object(Context, 'attach_short_workspace'), patch.object(Context, 'detach_short_workspace'),
              patch('local_release.profiles.tapnibbles.run') as build,
              patch('local_release.transport.handoff') as handoff,
              patch('local_release.transport.sync_results') as sync,
              patch('local_release.transport.send_result') as send):
            with self.assertRaises(TimeoutError):
                _run_job(self.directory, {}, publish=True)
            result_path = self.directory / 'results/windows.json'
            self.assertEqual(read_json(result_path)['status'], 'built')
            before = result_path.read_bytes()
            for action in (build, handoff, send):
                action.assert_called_once()  # No error-path resend after PATCH.
                action.reset_mock()
            sync.reset_mock()
            _run_job(self.directory, {}, publish=True)
            for action in (build, handoff, sync, send):
                action.assert_not_called()
            self.assertEqual(result_path.read_bytes(), before)
            self.assert_canonical(read_json(self.directory / 'publication.json'))

    @patch('local_release.github.credential', return_value='fixture')
    @patch('local_release.github.GitHub')
    def test_retry_before_publication_requires_same_draft_assets(self, github, credential):
        self.prepare_draft(github.return_value)
        self.fail_patch = 'before'
        with self.assertRaises(TimeoutError):
            publish_job(self.context)
        self.fail_patch = None
        asset = self.inventory['linux.tar.gz']
        asset['id'] += 100
        self.remote_calls.clear()
        with self.assertRaisesRegex(ReleaseError, 'asset identity changed'):
            publish_job(self.context)
        self.assertEqual(self.remote_calls, ['GET'])
        asset['id'] -= 100
        self.assert_canonical(publish_job(self.context))

    @patch('local_release.github.credential', return_value='fixture')
    @patch('local_release.github.GitHub')
    def test_legacy_repair_preserves_ids_and_hashes_and_is_read_only_on_github(self, github, credential):
        self.prepare_draft(github.return_value)
        original = publish_job(self.context)
        path = self.directory / 'publication.json'
        manifest_path = self.directory / 'manifest.json'
        original_manifest = read_json(manifest_path)
        legacy = deepcopy(original)
        legacy_manifest = deepcopy(original_manifest)
        for record in [*legacy['assets'].values(), legacy['manifest'], legacy['checksums'],
                       *legacy_manifest['packages'].values()]:
            record['url'] = record['url'].replace('v1.0.0%2B1', 'untagged-deadbeef')
        atomic_json(path, legacy)
        atomic_json(manifest_path, legacy_manifest)
        self.remote_calls.clear()
        asset = self.inventory['SHA256SUMS']
        actual_digest = asset['digest']
        asset['digest'] = 'sha256:' + 'f' * 64
        with self.assertRaisesRegex(ReleaseError, 'asset digest changed'):
            repair_publication_urls(self.directory, {})
        self.assertEqual(read_json(path), legacy)
        self.assertEqual(read_json(manifest_path), legacy_manifest)
        asset['digest'] = actual_digest
        self.assertEqual(repair_publication_urls(self.directory, {}), original)
        self.assertEqual(read_json(manifest_path), original_manifest)
        self.assertEqual(set(self.remote_calls), {'GET'})

    @patch('local_release.github.credential')
    def test_repair_does_not_touch_a_tombstoned_job(self, credential):
        from local_release.retention import record_path

        tombstone = record_path(self.context.root, self.job['project'], self.job['sha'])
        atomic_json(tombstone, {'status': 'deleted'})
        with self.assertRaisesRegex(ReleaseError, 'tombstone'):
            repair_publication_urls(self.directory, {})
        self.assertFalse((self.directory / '.publication.lock').exists())
        credential.assert_not_called()

    def run_receipt(self, changed_digest=False):
        manifest = json.dumps(self.summary).encode()
        package = self.summary["packages"]["linux.tar.gz"]
        sums = (package["sha256"] + "  linux.tar.gz\n").encode()
        assets = [
            {"id": 2, "name": "release-manifest.json", "size": len(manifest), "browser_download_url": "https://example.invalid/2"},
            {"id": 3, "name": "linux.tar.gz", **package, "digest": "sha256:" + ("f" * 64 if changed_digest else package["sha256"]), "browser_download_url": "https://example.invalid/3"},
            {"id": 4, "name": "SHA256SUMS", "size": len(sums), "digest": "sha256:" + hashlib.sha256(sums).hexdigest(), "browser_download_url": "https://example.invalid/4"},
        ]
        def download(asset, path):
            self.assertEqual(asset["name"], "release-manifest.json")
            path.write_bytes(manifest)
            return hashlib.sha256(manifest).hexdigest()
        with patch("local_release.github.credential", return_value="fixture"), patch("local_release.github.GitHub") as api:
            api.return_value.request.return_value = self.release
            api.return_value.tag_sha.return_value = self.job["sha"]
            api.return_value.pages.return_value = assets
            api.return_value.download_asset.side_effect = download
            return reconcile_published(self.context)

    def test_peer_recognizes_completed_release_without_transport_or_fabricated_checkpoints(self):
        original = {"sha": self.job["sha"], "run_id": self.job["run_id"], "host": "windows", "status": "incomplete", "steps": {}}
        atomic_json(self.directory / "results/windows.json", original)
        self.assertTrue(self.run_receipt())
        self.assertTrue(read_json(self.directory / "publication.json")["published"])
        self.assertEqual(read_json(self.directory / "results/windows.json"), original)
        self.assertFalse((self.context.output / "linux.tar.gz").exists())  # No duplicate package download.
        self.assertTrue((self.directory / "results/publication-received.json").exists())

    def test_draft_changed_package_or_missing_gates_never_close_the_local_job(self):
        self.release["draft"] = True
        self.assertFalse(self.run_receipt())
        self.release["draft"] = False
        with self.assertRaisesRegex(ReleaseError, "package metadata"):
            self.run_receipt(changed_digest=True)
        self.summary["verified_gates"]["windows"] = []
        with self.assertRaisesRegex(ReleaseError, "omits required"):
            self.run_receipt()
        self.assertFalse(read_json(self.directory / "publication.json")["published"])
