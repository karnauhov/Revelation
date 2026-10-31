from copy import deepcopy
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json, digest, lock, read_json, capture, git, queue_install, discover, prepare, run_job, execute_prepared, Context
from local_release.github import GitHubHTTPError
from local_release import retention


class FakeGitHub:
    def __init__(self):
        self.sha = "a" * 40
        self.releases = {1: {"id": 1, "tag_name": "v1.0.0+1", "target_commitish": self.sha,
            "draft": False, "body": "", "html_url": "https://github.com/owner/fixture/releases/tag/v1.0.0%2B1", "assets": []}}
        self.assets = {}
        self.events = []
        self.fail_upload = False

    def pages(self, path):
        if path == "/releases":
            return deepcopy(list(self.releases.values()))
        identifier = int(path.split("/")[2])
        return deepcopy(self.assets.get(identifier, []))

    def tag_sha(self, tag):
        return self.sha if tag == "v1.0.0+1" else None

    def request(self, method, path, data=None):
        self.events.append((method, path))
        if method == 'GET' and path == '':
            return {'default_branch': 'main'}
        if method == "POST":
            identifier = max(self.releases, default=1) + 1
            value = {**data, "id": identifier, "html_url": "https://github.com/owner/fixture/releases/retention", "assets": []}
            self.releases[identifier] = value
            return deepcopy(value)
        identifier = int(path.split("/")[2])
        if method == "DELETE":
            self.releases.pop(identifier, None)
            return None
        if identifier not in self.releases:
            raise GitHubHTTPError("not found", 404)
        return deepcopy(self.releases[identifier])

    def upload_verified(self, release, path):
        if self.fail_upload:
            raise ReleaseError("network unavailable")
        self.events.append(("UPLOAD", path.name))
        assets = self.assets.setdefault(release["id"], [])
        existing = next((a for a in assets if a["name"] == path.name), None)
        payload = path.read_bytes()
        if existing:
            if existing["bytes"] != payload:
                raise ReleaseError("immutable asset collision")
            return {k: existing[k] for k in ("id", "name", "size")}
        asset = {"id": 100 + sum(map(len, self.assets.values())), "name": path.name,
            "bytes": payload, "size": len(payload), "uploader": {"login": "owner"}, "sha256": digest(path),
            "digest": 'sha256:' + digest(path)}
        assets.append(asset)
        return {k: asset[k] for k in ("id", "name", "size")}

    def download_asset(self, asset, destination):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(asset["bytes"])
        return digest(destination)


class RetentionTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.api = FakeGitHub()
        self.project, self.directory = self.create_host("windows")

    def create_host(self, role):
        root = self.base / role
        profile = root / "profile.json"
        config = root / "config.json"
        atomic_json(profile, {"project": "fixture", "repository": "owner/fixture", "adapter": "local_release.profiles.native_fixture"})
        atomic_json(config, {})
        project = {"project": "fixture", "catalogue": str(root), "profile": str(profile), "config": str(config),
                   "repo": str(root), "hosts": ["windows", "linux"], "enabled": True}
        directory = root / "releases/fixture/1.0.0+1" / self.api.sha
        package = directory / "packages/one.zip"
        package.parent.mkdir(parents=True)
        package.write_bytes(b"accepted package")
        atomic_json(directory / "manifest.json", {"schema": 1, "project": "fixture", "version": "1.0.0", "build": 1,
            "sha": self.api.sha, "packages": {"one.zip": {"path": "packages/one.zip", "sha256": digest(package), "size": package.stat().st_size}}})
        snapshot = root / "w" / self.api.sha[:12] / role[0]
        snapshot.mkdir(parents=True)
        (snapshot / "cache.bin").write_bytes(b"temporary build")
        atomic_json(root / "fixture-queue.json", {"project": "fixture", "commits": {self.api.sha: {"status": "running", "sequence": 1}}})
        return project, directory

    def request(self):
        prepared = retention.preview(self.project, self.directory, api=self.api)
        return retention.request_deletion(self.project, prepared)

    def test_preview_and_cancel_change_nothing(self):
        value = retention.preview(self.project, self.directory, api=self.api)
        self.assertEqual(value["package_count"], 1)
        self.assertTrue(self.directory.exists())
        self.assertFalse(retention.deleted(self.project["catalogue"], "fixture", self.api.sha))
        self.assertEqual(self.api.events, [])

    def test_windows_delete_then_isolated_linux_login_and_receipt(self):
        linux, linux_directory = self.create_host("linux")
        foreign = self.base / "windows/releases/fixture/9.0.0+9" / ("b" * 40)
        foreign.mkdir(parents=True)
        (foreign / "keep.bin").write_bytes(b"do not touch")
        self.request()
        record = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertTrue(record["local_deleted"])
        self.assertTrue(record["github_deleted"])
        self.assertEqual(record["status"], "waiting_other_hosts")
        self.assertFalse(self.directory.exists())
        self.assertFalse((Path(self.project["catalogue"]) / "w" / self.api.sha[:12]).exists())
        self.assertTrue((foreign / "keep.bin").exists())
        self.assertNotIn(1, self.api.releases)
        self.assertTrue(linux_directory.exists())
        upload = next(i for i, event in enumerate(self.api.events) if event[0] == "UPLOAD")
        deletion = self.api.events.index(("DELETE", "/releases/1"))
        self.assertLess(upload, deletion)
        retention.synchronize(linux, "linux", api=self.api)
        self.assertFalse(linux_directory.exists())
        result = retention.synchronize(self.project, "windows", api=self.api)[0]
        self.assertEqual(result["status"], "complete")
        self.assertEqual(set(result["acks"]), {"windows", "linux"})
        self.assertEqual(sum(e == ("DELETE", "/releases/1") for e in self.api.events), 1)
        with self.assertRaisesRegex(ReleaseError, "deleted by the owner"):
            retention.ensure_allowed(self.project["catalogue"], "fixture", self.api.sha)
        self.assertEqual(read_json(Path(self.project["catalogue"]) / "fixture-queue.json")["commits"][self.api.sha]["status"], "deleted")

    def test_failed_transport_preserves_all_local_and_remote_packages(self):
        record = self.request()
        self.api.fail_upload = True
        result = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(self.directory.exists())
        self.assertIn(1, self.api.releases)
        self.assertTrue(retention.deleted(self.project["catalogue"], "fixture", self.api.sha))
        self.api.fail_upload = False
        result = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertEqual(result["request"]["request_id"], record["request"]["request_id"])
        self.assertTrue(result["local_deleted"])

    def test_active_builder_is_stopped_before_any_release_or_files_are_removed(self):
        self.request()
        with lock(self.directory / ".windows.lock"):
            record = retention.process(self.project, self.api.sha, role="windows", api=self.api)
            self.assertEqual(record["status"], "stopping")
            self.assertTrue((self.directory / "stop-request.json").exists())
            self.assertIn(1, self.api.releases)
            self.assertTrue((self.directory / "packages/one.zip").exists())
        self.assertTrue(retention.process(self.project, self.api.sha, role="windows", api=self.api)["local_deleted"])

    def test_changed_source_or_foreign_control_release_is_never_deleted(self):
        self.api.sha = "b" * 40
        with self.assertRaisesRegex(ReleaseError, "different source SHA"):
            retention.preview(self.project, self.directory, api=self.api)
        self.assertIn(1, self.api.releases)
        self.assertTrue(self.directory.exists())
        self.api.sha = "a" * 40
        self.request()
        self.api.releases[2] = {"id": 2, "tag_name": "ai11-local-retention-fixture", "draft": True, "body": "unrelated"}
        result = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertEqual(result["status"], "failed")
        self.assertIn(1, self.api.releases)
        self.assertTrue(self.directory.exists())

    def test_paths_and_owner_recovery_journals_are_protected(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "important.bin").write_bytes(b"owner")
        with self.assertRaisesRegex(ReleaseError, "exact managed"):
            retention.safe_remove(self.project["catalogue"], outside, Path("w") / self.api.sha[:12])
        self.assertTrue((outside / "important.bin").exists())
        self.request()
        journal = Path(self.project["catalogue"]) / "w" / self.api.sha[:12] / "snap-acceptance/restore.json"
        atomic_json(journal, {"must": "restore original user data"})
        result = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(journal.exists())
        self.assertTrue(self.directory.exists())

    def test_repeated_request_and_readonly_git_files_are_safe(self):
        first = self.request()
        second = self.request()
        self.assertEqual(first["request"], second["request"])
        readonly = self.directory / "readonly.bin"
        readonly.write_bytes(b"git pack")
        readonly.chmod(stat.S_IREAD)
        result = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertTrue(result["local_deleted"])
        again = retention.process(self.project, self.api.sha, role="windows", api=self.api)
        self.assertEqual(again["request"], result["request"])
        self.assertEqual(sum(e == ("DELETE", "/releases/1") for e in self.api.events), 1)

    def test_untrusted_remote_request_cannot_remove_linux_files(self):
        linux, directory = self.create_host("linux")
        self.request()
        retention.process(self.project, self.api.sha, role="windows", api=self.api)
        control = next(r for r in self.api.releases.values() if r["tag_name"].startswith("ai11-local-retention"))
        self.api.assets[control["id"]][0]["uploader"]["login"] = "stranger"
        with self.assertRaisesRegex(ReleaseError, "trusted repository owner"):
            retention.synchronize(linux, "linux", api=self.api)
        self.assertTrue(directory.exists())

    def test_changed_local_identity_after_preview_preserves_packages(self):
        prepared = retention.preview(self.project, self.directory, api=self.api)
        path = self.directory / 'manifest.json'
        value = read_json(path)
        value['sha'] = 'b' * 40
        atomic_json(path, value)
        with self.assertRaisesRegex(ReleaseError, 'identity changed'):
            retention.request_deletion(self.project, prepared)
        self.assertTrue((self.directory / 'packages/one.zip').exists())
        self.assertEqual(self.api.events, [])

    def test_verified_control_records_are_reused_until_remote_identity_changes(self):
        linux, _ = self.create_host('linux')
        self.request()
        retention.process(self.project, self.api.sha, role='windows', api=self.api)
        retention.synchronize(linux, 'linux', api=self.api)
        retention.synchronize(self.project, 'windows', api=self.api)
        with patch.object(self.api, 'download_asset', wraps=self.api.download_asset) as download:
            retention.synchronize(self.project, 'windows', api=self.api)
            download.assert_not_called()
            control = next(r for r in self.api.releases.values() if r['tag_name'].startswith('ai11-local-retention'))
            self.api.assets[control['id']][0]['id'] += 1000
            retention.synchronize(self.project, 'windows', api=self.api)
            self.assertEqual(download.call_count, 1)

    def test_archive_and_handoff_do_not_restore_a_tombstoned_build(self):
        from local_release.archive import archive_releases
        from local_release.transport import receive_jobs
        package = self.directory / 'packages/one.zip'
        self.api.upload_verified(self.api.releases[1], package)
        self.request()
        package.unlink()
        with patch('local_release.archive.GitHub', return_value=self.api), patch('local_release.archive.credential', return_value='fixture'):
            archive_releases(read_json(Path(self.project['profile'])), Path(self.project['catalogue']), {})
        self.assertFalse(package.exists())
        self.assertFalse((self.directory / 'github-release.json').exists())
        self.api.releases[1].update(draft=True, body='<!-- local-release:fixture-' + self.api.sha + ' -->')
        self.api.assets[1].append({'id': 999, 'name': 'local-transfer-fixture-' + self.api.sha + '-job.tar.gz', 'size': 4, 'bytes': b'junk'})
        with patch('local_release.transport.GitHub', return_value=self.api), patch('local_release.transport.credential', return_value='fixture'):
            self.assertEqual(receive_jobs(read_json(Path(self.project['profile'])), Path(self.project['catalogue']), {}), [])
        self.assertFalse(package.exists())

    def test_commit_discovery_prepare_run_and_publication_cannot_resurrect_deleted_sha(self):
        from local_release.github import publish_job
        repo = self.base / 'git-repo'
        capture(['git', 'init', repo])
        git(repo, 'config', 'user.name', 'Fixture')
        git(repo, 'config', 'user.email', 'fixture@example.invalid')
        (repo / 'source').write_text('baseline')
        git(repo, 'add', '.'); git(repo, 'commit', '-m', 'baseline')
        root = self.base / 'queue-root'
        profile, config = root / 'profile.json', root / 'config.json'
        atomic_json(profile, {'project': 'fixture', 'adapter': 'local_release.profiles.native_fixture'})
        atomic_json(config, {})
        queue = queue_install(repo, root, profile, config)
        (repo / 'source').write_text('ordinary commit')
        git(repo, 'add', '.'); git(repo, 'commit', '-m', 'ordinary change')
        sha = git(repo, 'rev-parse', 'HEAD')
        atomic_json(retention.record_path(root, 'fixture', sha), {'confirmed': True})
        self.assertEqual(discover(repo, root, queue)['commits'][sha]['status'], 'deleted')
        with self.assertRaisesRegex(ReleaseError, 'deleted by the owner'):
            prepare(repo, profile, root, sha, {})
        directory = root / 'releases/fixture/1.0.0+1' / sha
        for action in (lambda: run_job(directory, {}), lambda: execute_prepared(directory, config)):
            with self.assertRaisesRegex(ReleaseError, 'deleted by the owner'):
                action()
        self.request()
        atomic_json(self.directory / 'job.json', {'schema': 1, 'project': 'fixture', 'sha': self.api.sha, 'run_id': 'fixture-a'})
        with self.assertRaisesRegex(ReleaseError, 'deleted by the owner'):
            publish_job(Context(self.directory, {}))
        self.assertIn(1, self.api.releases)


if __name__ == "__main__":
    unittest.main()
