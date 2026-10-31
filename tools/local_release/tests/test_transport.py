"""Two isolated OS catalogues exchanging jobs/results through a fake GitHub API."""

from pathlib import Path
import hashlib
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import core, transport
from local_release.catalogue import verify_catalogue


class FakeGitHub:
    assets = {}
    next_id = 1
    release = None

    def __init__(self, repository, token):
        self.repository = repository

    def ensure_release(self, job, notes):
        if not self.release:
            type(self).release = {"id": 1, "tag_name": job["tag"], "target_commitish": job["sha"],
                                  "body": f"<!-- local-release:{job['run_id']} -->", "draft": True}
        return self.release

    def pages(self, path):
        return [self.release] if path == "/releases" else [a[0] for a in self.assets.values()]

    def tag_sha(self, tag):
        return self.release["target_commitish"]

    def upload_verified(self, release, path, **kwargs):
        content = path.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        name = kwargs.get("asset_name") or path.name
        existing = next((a for a in self.assets.values() if a[0]["name"] == name), None)
        if existing:
            if existing[1] != content:
                raise core.ReleaseError("asset collision")
            record = existing[0]
        else:
            asset_id = type(self).next_id
            type(self).next_id += 1
            record = {"id": asset_id, "name": name, "size": len(content), "digest": "sha256:" + sha,
                      "url": f"https://api.github.com/fixture/assets/{asset_id}",
                      "browser_download_url": f"https://example.invalid/{asset_id}"}
            self.assets[asset_id] = (record, content)
        return {"id": record["id"], "sha256": sha, "url": record["browser_download_url"], "size": len(content)}

    def download_asset(self, asset, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self.assets[asset["id"]][1]
        path.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def request(self, method, path, **kwargs):
        if method != "DELETE":
            raise AssertionError((method, path))
        del self.assets[int(path.rsplit("/", 1)[1])]


class TransportTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        repo = self.base / "repo"
        repo.mkdir()
        core.capture(["git", "init", repo])
        core.git(repo, "config", "user.name", "Fixture")
        core.git(repo, "config", "user.email", "fixture@example.invalid")
        (repo / "source").write_text("fixed source")
        core.git(repo, "add", ".")
        core.git(repo, "commit", "-m", "fixture")
        fixture = types.ModuleType("local_release.profiles.fixture")
        fixture.metadata = lambda *args: {"version": "1.0.0", "build": 1, "tag": "v1.0.0+1",
                                         "artifacts": ["windows.zip", "linux.tar.gz"],
                                         "required_steps": {"windows": ["compile"], "linux": ["compile"]},
                                         "release_notes": "Fixture"}
        self.profile = {"project": "fixture", "repository": "owner/repo", "adapter": fixture.__name__}
        profile = self.base / "profile.json"
        core.atomic_json(profile, self.profile)
        self.modules = patch.dict(sys.modules, {fixture.__name__: fixture})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        job = core.prepare(repo, profile, self.base / "windows-root")
        (job / "release_notes.txt").write_text("Fixture")
        self.windows = core.Context(job, {}, host="windows")
        FakeGitHub.assets, FakeGitHub.next_id, FakeGitHub.release = {}, 1, None
        self.api = patch("local_release.transport.GitHub", FakeGitHub)
        self.api.start()
        self.addCleanup(self.api.stop)
        self.auth = patch("local_release.transport.credential", return_value="fixture-token")
        self.auth.start()
        self.addCleanup(self.auth.stop)

    def compile(self, ctx, name):
        def action():
            (ctx.output / name).write_bytes((ctx.host + " package").encode())
        ctx.stage("compile", action, ["packages/" + name])
        ctx.result["status"] = "built"
        ctx.save()

    def receive(self):
        jobs = transport.receive_jobs(self.profile, self.base / "linux-root", {})
        self.assertEqual(len(jobs), 1)
        return core.Context(jobs[0], {}, host="linux")

    def test_two_way_exchange_keeps_one_package_and_cleans_only_received_transport(self):
        self.compile(self.windows, "windows.zip")
        transport.handoff(self.windows)
        transport.send_result(self.windows)
        linux = self.receive()
        transport.sync_results(linux)
        self.assertEqual((linux.output / "windows.zip").read_bytes(), b"windows package")
        self.compile(linux, "linux.tar.gz")
        transport.send_result(linux)
        receipts = transport.sync_results(self.windows, cleanup=True)
        self.assertEqual(len(receipts), 1)
        manifest = verify_catalogue(self.windows.directory)
        self.assertEqual(manifest["status"], "ready")
        self.assertEqual(len(list(self.windows.output.iterdir())), 2)
        self.assertEqual({a[0]["name"] for a in FakeGitHub.assets.values()}, {"windows.zip", "linux.tar.gz"})

    def published_fixture(self):
        self.compile(self.windows, "windows.zip")
        transport.handoff(self.windows)
        transport.send_result(self.windows)
        linux = self.receive()
        self.compile(linux, "linux.tar.gz")
        transport.send_result(linux)
        transport.sync_results(self.windows)
        api = FakeGitHub("owner/repo", "fixture")
        release = FakeGitHub.release
        records = {name: api.upload_verified(release, self.windows.output / name) for name in self.windows.job["artifacts"]}
        checksums = self.windows.output / "SHA256SUMS"
        checksums.write_text("verified fixture sums")
        manifest = self.windows.directory / "release-manifest.json"
        manifest.write_text("verified fixture manifest")
        core.atomic_json(self.windows.directory / "publication.json", {
            "published": True, "release_id": release["id"], "sha": self.windows.job["sha"], "assets": records,
            "checksums": api.upload_verified(release, checksums), "manifest": api.upload_verified(release, manifest)})
        return api, release

    def test_final_receipt_closes_only_recognized_owned_transport_after_publication(self):
        api, release = self.published_fixture()
        temporary = self.base / "temporary.bin"
        temporary.write_bytes(b"old repair")
        own = api.upload_verified(release, temporary, asset_name=transport.prefix(self.windows.job) + "runtime-v3.tar.gz")
        foreign = api.upload_verified(release, temporary, asset_name="local-transfer-another-run-runtime-v1.tar.gz")
        unknown = api.upload_verified(release, temporary, asset_name=transport.prefix(self.windows.job) + "owner-note.txt")
        transport.close_published_exchange(self.windows, api, release)
        self.assertIn(own["id"], FakeGitHub.assets)  # A draft never permits final cleanup.
        release["draft"] = False
        original = api.request
        def remove(method, path, **kwargs):
            receipt = core.read_json(self.windows.directory / "results/exchange-closed.json")
            self.assertTrue(receipt["all_required_gates_passed"])
            self.assertTrue(any(a["id"] == int(path.rsplit("/", 1)[1]) for a in receipt["temporary_assets"]))
            return original(method, path, **kwargs)
        with patch.object(api, "request", side_effect=remove):
            transport.close_published_exchange(self.windows, api, release)
        self.assertNotIn(own["id"], FakeGitHub.assets)
        self.assertIn(foreign["id"], FakeGitHub.assets)
        self.assertIn(unknown["id"], FakeGitHub.assets)
        self.assertTrue({"windows.zip", "linux.tar.gz", "SHA256SUMS", "release-manifest.json"} <= {a[0]["name"] for a in FakeGitHub.assets.values()})
        transport.close_published_exchange(self.windows, api, release)  # Idempotent after the peer status is gone.

    def test_changed_canonical_asset_prevents_final_transport_deletion(self):
        api, release = self.published_fixture()
        release["draft"] = False
        before = set(FakeGitHub.assets)
        (self.windows.output / "windows.zip").write_bytes(b"changed bytes")
        with self.assertRaises(core.ReleaseError):
            transport.close_published_exchange(self.windows, api, release)
        self.assertEqual(set(FakeGitHub.assets), before)

    def test_failure_status_and_redacted_logs_reach_windows_without_manual_copy(self):
        transport.handoff(self.windows)
        linux = self.receive()
        linux.refresh_redaction(["private-example-token"])
        log = linux.directory / "logs/linux/snap.log"
        log.parent.mkdir(parents=True)
        log.write_text("failure: private-example-token")
        linux.result.update(status="failed", current_step="snap", error="fixture snap failure")
        linux.save()
        transport.send_result(linux)
        transport.sync_results(self.windows)
        result = core.read_json(self.windows.directory / "results/linux.json")
        self.assertEqual(result["status"], "failed")
        received = (self.windows.directory / "logs/linux/snap.log").read_text()
        self.assertNotIn("private-example-token", received)
        self.assertIn("[REDACTED]", received)
        self.assertFalse((self.windows.output / "linux.tar.gz").exists())

    def test_partial_windows_checkpoints_without_uploaded_packages_do_not_block_linux(self):
        self.compile(self.windows, "windows.zip")
        self.windows.job["required_steps"]["windows"].append("integration")
        core.atomic_json(self.windows.directory / "job.json", self.windows.job)
        transport.handoff(self.windows)
        transport.send_result(self.windows)
        linux = self.receive()
        transport.sync_results(linux)
        self.assertFalse((linux.output / "windows.zip").exists())
        self.compile(linux, "linux.tar.gz")
        from local_release.catalogue import catalogue_job
        catalogue_job(linux)
        self.assertEqual(verify_catalogue(linux.directory)["status"], "incomplete")

    def test_windows_evidence_uses_portable_paths_and_reaches_linux(self):
        self.compile(self.windows, "windows.zip")
        proof = self.windows.directory / "results/windows-proof.txt"
        def evidence():
            proof.write_text("verified coverage evidence")
        self.windows.stage("coverage-evidence", evidence, ["results/windows-proof.txt"])
        outputs = self.windows.result["steps"]["coverage-evidence"]["outputs"]
        self.assertEqual(set(outputs), {"results/windows-proof.txt"})
        transport.handoff(self.windows)
        transport.send_result(self.windows)
        linux = self.receive()
        transport.sync_results(linux)
        self.assertEqual((linux.directory / "results/windows-proof.txt").read_text(), "verified coverage evidence")

    def test_one_linux_package_is_transferred_even_when_another_stage_failed(self):
        self.windows.job["artifacts"].append("fixture.snap")
        self.windows.job["required_steps"]["linux"].append("snap")
        self.windows.job["artifact_specs"] = {"linux.tar.gz": {"host": "linux", "gates": ["compile"]}}
        core.atomic_json(self.windows.directory / "job.json", self.windows.job)
        transport.handoff(self.windows)
        linux = self.receive()
        self.compile(linux, "linux.tar.gz")
        linux.result.update(status="failed", current_step="snap")
        linux.result["steps"]["snap"] = {"status": "failed", "error": "fixture Snap failure"}
        linux.save()
        transport.send_result(linux)
        transport.sync_results(self.windows)
        self.assertTrue((self.windows.output / "linux.tar.gz").is_file())
        self.assertFalse((self.windows.output / "fixture.snap").exists())
        self.assertEqual(core.read_json(self.windows.directory / "results/linux.json")["status"], "failed")

    def test_runtime_update_preserves_source_packages_and_repairs_existing_linux_job(self):
        from local_release.runtime_update import prepare_update, send_update
        self.compile(self.windows, "windows.zip")
        transport.handoff(self.windows)
        linux = self.receive()
        self.compile(linux, "linux.tar.gz")
        before = self.windows.job["sha"], self.windows.job["build"]
        prepare_update(self.windows.directory, {}, "b" * 40, reason="Repair the fixture version probe")
        updated = core.Context(self.windows.directory, {}, host="windows")
        self.assertEqual(updated.job["tooling_changes"][-1]["reason"], "Repair the fixture version probe")
        first = send_update(updated)
        second = send_update(updated)
        self.assertEqual(first["sha256"], second["sha256"])
        transport.receive_jobs(self.profile, self.base / "linux-root", {})
        received = core.Context(linux.directory, {}, host="linux")
        self.assertEqual((received.job["sha"], received.job["build"]), before)
        self.assertEqual(received.job["preparation_revision"], 2)
        self.assertEqual((received.output / "linux.tar.gz").read_bytes(), b"linux package")
        self.assertTrue((received.directory / "results/runtime-updates-received.json").is_file())

    def test_runtime_upgrade_rejects_source_change_or_gate_removal_and_base_is_cached(self):
        from copy import deepcopy
        from local_release.protocol import validate_upgrade
        old = self.windows.job
        new = deepcopy(old)
        new["preparation_revision"] = 2
        validate_upgrade(old, new)
        new["sha"] = "c" * 40
        with self.assertRaisesRegex(core.ReleaseError, "source identity"):
            validate_upgrade(old, new)
        new["sha"] = old["sha"]
        new["required_steps"]["linux"] = []
        with self.assertRaisesRegex(core.ReleaseError, "removes required"):
            validate_upgrade(old, new)
        transport.handoff(self.windows)
        self.receive()
        with patch.object(FakeGitHub, "download_asset", side_effect=AssertionError("cached base was downloaded twice")):
            transport.receive_jobs(self.profile, self.base / "linux-root", {})

    def test_runtime_archive_refuses_symlinks_and_escape_paths(self):
        import io
        import tarfile
        from local_release.runtime_update import unpack
        for name, kind in (("../escape.py", tarfile.REGTYPE), ("symlink.py", tarfile.SYMTYPE)):
            path = self.base / "unsafe.tar"
            with tarfile.open(path, "w") as archive:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.size = 0
                archive.addfile(member, io.BytesIO(b""))
            with self.assertRaises(core.ReleaseError):
                unpack(path, self.base / "extract")

    def test_early_linux_failure_preserves_unacknowledged_windows_results(self):
        self.compile(self.windows, "windows.zip")
        transport.handoff(self.windows)
        transport.send_result(self.windows)
        linux = self.receive()
        linux.result.update(status="failed", current_step="preflight", error="toolchain missing")
        linux.save()
        transport.send_result(linux)
        transport.sync_results(self.windows, cleanup=True)
        names = {a[0]["name"] for a in FakeGitHub.assets.values()}
        self.assertIn(transport.prefix(self.windows.job) + "windows-status.json", names)
        self.assertIn(transport.prefix(self.windows.job) + "windows-logs.zip", names)
        self.assertIn(transport.prefix(self.windows.job) + "job.tar.gz", names)
        # The already received Linux job can resume and obtain forward evidence.
        transport.sync_results(linux)
        self.assertEqual((linux.output / "windows.zip").read_bytes(), b"windows package")
        self.compile(linux, "linux.tar.gz")
        transport.send_result(linux)
        transport.sync_results(self.windows, cleanup=True)
        self.assertEqual({a[0]["name"] for a in FakeGitHub.assets.values()}, {"windows.zip", "linux.tar.gz"})

    def test_network_failure_leaves_local_result_and_remote_payload_for_retry(self):
        transport.handoff(self.windows)
        linux = self.receive()
        self.compile(linux, "linux.tar.gz")
        transport.send_result(linux)
        before = set(FakeGitHub.assets)
        with patch.object(FakeGitHub, "download_asset", side_effect=core.ReleaseError("offline")):
            with self.assertRaisesRegex(core.ReleaseError, "offline"):
                transport.sync_results(self.windows, cleanup=True)
        self.assertEqual(set(FakeGitHub.assets), before)
        transport.sync_results(self.windows, cleanup=True)
        self.assertTrue((self.windows.output / "linux.tar.gz").exists())

    def test_remote_result_from_other_sha_is_not_imported_or_deleted(self):
        transport.handoff(self.windows)
        linux = self.receive()
        transport.send_result(linux)
        for asset_id, (asset, content) in list(FakeGitHub.assets.items()):
            if asset["name"].endswith("linux-status.json"):
                value = json.loads(content)
                value["sha"] = "b" * 40
                changed = json.dumps(value).encode()
                asset.update(size=len(changed), digest="sha256:" + hashlib.sha256(changed).hexdigest())
                FakeGitHub.assets[asset_id] = (asset, changed)
        before = set(FakeGitHub.assets)
        with self.assertRaisesRegex(core.ReleaseError, "different build"):
            transport.sync_results(self.windows, cleanup=True)
        self.assertEqual(set(FakeGitHub.assets), before)


if __name__ == "__main__":
    unittest.main()
