"""Observable release/queue behavior in private repositories; no live writes."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from local_release import core
from local_release import github
from local_release.archive import archive_releases
from local_release.hooks import install, remove


class CoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo with spaces"
        self.repo.mkdir()
        core.capture(["git", "init", self.repo])
        core.git(self.repo, "config", "user.name", "Release fixture")
        core.git(self.repo, "config", "user.email", "fixture@example.invalid")
        core.git(self.repo, "config", "core.autocrlf", "false")
        self.commit("baseline")
        self.state = self.root / "state"
        self.profile = self.root / "profile.json"
        core.atomic_json(self.profile, {"project": "fixture", "repository": "owner/repo",
                                        "adapter": "local_release.profiles.fixture"})
        self.config = self.root / "config.json"
        core.atomic_json(self.config, {})
        fixture = types.ModuleType("local_release.profiles.fixture")
        fixture.metadata = lambda repo, sha, profile: {
            "version": "1.0.0", "build": 1, "tag": "v1.0.0+1", "artifacts": ["sample.zip"],
            "required_steps": {core.host_name(): ["compile"]}, "release_notes": "Fixture"}
        fixture.run = lambda ctx: ctx.stage("compile", lambda: self.compile(ctx), ["packages/sample.zip"])
        self.fixture = fixture
        self.module_patch = patch.dict(sys.modules, {fixture.__name__: fixture})
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)

    def commit(self, message):
        path = self.repo / "content.txt"
        path.write_text(path.read_text() + "x" if path.exists() else "x")
        core.git(self.repo, "add", "content.txt")
        core.git(self.repo, "commit", "-m", message)
        return core.git(self.repo, "rev-parse", "HEAD")

    def compile(self, ctx):
        ctx.command([sys.executable, "-c", "from pathlib import Path; Path('count').write_text(Path('count').read_text()+'x' if Path('count').exists() else 'x')"])
        (ctx.output / "sample.zip").write_text(ctx.job["sha"])

    def job(self):
        return core.prepare(self.repo, self.profile, self.state)

    def test_freezes_commit_and_ignores_uncommitted_files(self):
        sha = core.git(self.repo, "rev-parse", "HEAD")
        (self.repo / "secret.env").write_text("not committed")
        (self.repo / "content.txt").write_text("uncommitted owner changes")
        job = self.job()
        ctx = core.Context(job, {})
        ctx.checkout()
        self.assertEqual(core.git(ctx.workspace, "rev-parse", "HEAD"), sha)
        self.assertEqual((ctx.workspace / "content.txt").read_text(), "x")
        self.assertFalse((ctx.workspace / "secret.env").exists())
        self.assertEqual((self.repo / "content.txt").read_text(), "uncommitted owner changes")

    def test_successful_steps_are_not_rebuilt_on_resume(self):
        job = self.job()
        core.run_job(job, {})
        core.run_job(job, {})
        ctx = core.Context(job, {})
        self.assertEqual((ctx.workspace / "count").read_text(), "x")
        self.assertTrue(github.complete_results(job, ctx.job))

    def test_unpushed_source_builds_locally_then_waits_without_rebuilding(self):
        job = self.job()
        waiting = core.SourceUnavailable("source SHA is not accessible")
        with patch("local_release.transport.handoff", side_effect=waiting), patch("local_release.transport.sync_results", side_effect=waiting), patch("local_release.transport.send_result", side_effect=waiting):
            ctx = core.run_job(job, {}, publish=True)
        self.assertEqual(ctx.result["status"], "waiting_source_sha")
        self.assertTrue((ctx.output / "sample.zip").is_file())
        with patch("local_release.transport.handoff"), patch("local_release.transport.sync_results"), patch("local_release.transport.send_result"), patch("local_release.github.publish_job"):
            core.run_job(job, {}, publish=True)
        self.assertEqual((ctx.workspace / "count").read_text(), "x")

    def test_source_404_waits_but_authentication_error_is_distinct(self):
        api = github.GitHub("owner/repo", "fixture-token")
        with patch.object(api, "request", side_effect=github.GitHubHTTPError("HTTP 404", 404)):
            with self.assertRaises(core.SourceUnavailable):
                api.require_source("a" * 40)
        with patch.object(api, "request", side_effect=github.GitHubHTTPError("HTTP 403", 403)):
            with self.assertRaises(github.GitHubHTTPError):
                api.require_source("a" * 40)

    def test_changed_artifact_is_rebuilt_without_reusing_bad_checkpoint(self):
        job = self.job()
        core.run_job(job, {})
        (job / "packages/sample.zip").write_text("corrupt")
        core.run_job(job, {})
        ctx = core.Context(job, {})
        self.assertEqual((ctx.workspace / "count").read_text(), "xx")
        self.assertEqual((job / "packages/sample.zip").read_text(), ctx.job["sha"])

    def test_retry_invalidates_declared_dependents_without_touching_other_platform(self):
        job = self.job()
        specification = core.read_json(job / "job.json")
        specification["step_dependencies"] = {"a-dependent": ["z-source"]}
        core.atomic_json(job / "job.json", specification)
        ctx = core.Context(job, {})
        target = ctx.output / "source.zip"
        ctx.stage("z-source", lambda: target.write_bytes(b"good"), ["packages/source.zip"])
        ctx.stage("a-dependent", lambda: None)
        ctx.stage("m-other-platform", lambda: None)
        target.write_bytes(b"bad")
        resumed = core.Context(job, {})
        resumed.stage("z-source", lambda: target.write_bytes(b"good"), ["packages/source.zip"])
        self.assertNotIn("a-dependent", resumed.result["steps"])
        self.assertEqual(resumed.result["steps"]["m-other-platform"]["status"], "passed")

    def test_failure_survives_restart_and_resumes_only_failed_step(self):
        job = self.job()
        marker = self.root / "allow"
        def pipeline(ctx):
            ctx.stage("compile", lambda: self.compile(ctx), ["packages/sample.zip"])
            ctx.stage("upload-fixture", lambda: ctx.command([sys.executable, "-c", f"from pathlib import Path; import sys; sys.exit(0 if Path({str(marker)!r}).exists() else 9)"]))
        self.fixture.run = pipeline
        with self.assertRaises(core.ReleaseError):
            core.run_job(job, {})
        result = core.read_json(job / "results" / f"{core.host_name()}.json")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["current_step"], "upload-fixture")
        marker.touch()
        core.run_job(job, {})
        self.assertEqual((core.Context(job, {}).workspace / "count").read_text(), "x")

    def test_runtime_and_source_tampering_are_rejected(self):
        job = self.job()
        (job / "source.bundle").write_bytes(b"changed")
        with self.assertRaisesRegex(core.ReleaseError, "digest mismatch"):
            core.run_job(job, {})
        runtime = job / "runtime/local_release/core.py"
        runtime.write_text("changed")
        with self.assertRaisesRegex(core.ReleaseError, "Runtime differs"):
            core.verify_runtime(job)

    def test_queue_keeps_each_commit_and_full_message_skip(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config, test_mode=True)
        one = self.commit("normal one")
        skip_title = self.commit("skip [skip ci]")
        skip_body = self.commit("skip body\n\n[skip ci]")
        two = self.commit("normal two")
        data = core.discover(self.repo, self.state, queue)
        again = core.discover(self.repo, self.state, queue)
        self.assertEqual(data, again)
        queued = sorted(data["commits"], key=lambda s: data["commits"][s]["sequence"])
        self.assertEqual([s for s in queued if data["commits"][s]["status"] == "queued"], [one, two])
        self.assertEqual({s for s, row in data["commits"].items() if row["status"] == "skipped"}, {skip_title, skip_body})
        self.assertEqual(len(data["commits"]), 4)

    def test_remote_commits_and_intermediate_commits_are_discovered(self):
        remote = self.root / "remote"
        core.capture(["git", "clone", "--bare", self.repo, remote])
        core.git(self.repo, "remote", "add", "origin", str(remote))
        queue = core.queue_install(self.repo, self.state, self.profile, self.config)
        other = self.root / "other"
        core.capture(["git", "clone", remote, other])
        core.git(other, "config", "user.name", "Other fixture")
        core.git(other, "config", "user.email", "other@example.invalid")
        commits = []
        for n in range(2):
            (other / "remote.txt").write_text(str(n))
            core.git(other, "add", ".")
            core.git(other, "commit", "-m", f"remote {n}")
            commits.append(core.git(other, "rev-parse", "HEAD"))
        core.git(other, "push", "origin", "HEAD")
        core.git(self.repo, "fetch", "origin")
        self.assertEqual(set(core.discover(self.repo, self.state, queue)["commits"]), set(commits))

    def test_busy_queue_does_not_lose_commit_replaced_by_amend(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config, test_mode=True)
        first = self.commit("before amend")
        with core.lock(self.state / ".queue.lock"):
            core.record_commit_event(self.repo, queue, first)
            with self.assertRaisesRegex(core.ReleaseError, "Busy operation"):
                core.discover(self.repo, self.state, queue)
            core.git(self.repo, "commit", "--amend", "-m", "after amend")
            second = core.git(self.repo, "rev-parse", "HEAD")
            core.record_commit_event(self.repo, queue, second)
        data = core.discover(self.repo, self.state, queue)
        self.assertEqual(set(data["commits"]), {first, second})
        self.assertEqual(list((self.state / "events" / queue.stem).glob("*.json")), [])

    def test_worker_retains_failed_jobs_and_processes_later_commits(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config, test_mode=True)
        one = self.commit("one")
        two = self.commit("two")
        def pipeline(ctx):
            if ctx.job["sha"] == one:
                raise core.ReleaseError("fixture build failure")
            ctx.stage("compile", lambda: self.compile(ctx), ["packages/sample.zip"])
        self.fixture.run = pipeline
        runner = lambda job, config, publish: core.run_job(job, core.read_json(config), publish)
        core.worker(queue, once=True, runner=runner)
        data = core.read_json(queue)
        self.assertEqual(data["commits"][one]["status"], "failed")
        self.assertTrue(Path(data["commits"][one]["job"]).joinpath("results", core.host_name() + ".json").is_file())
        self.assertEqual(data["commits"][two]["status"], "waiting_other_hosts")
        self.fixture.run = lambda ctx: ctx.stage("compile", lambda: self.compile(ctx), ["packages/sample.zip"])
        core.update_queue(self.state, queue, one, status="queued")
        core.worker(queue, once=True, runner=runner)
        self.assertEqual(core.read_json(queue)["commits"][one]["status"], "waiting_other_hosts")
        self.assertEqual((core.Context(self.state / "releases/fixture/1.0.0+1" / two, {}).workspace / "count").read_text(), "x")

    def test_restarted_observer_waits_for_live_builder_and_recovers_interrupted_job(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config, test_mode=True)
        sha = self.commit("interrupted run")
        core.discover(self.repo, self.state, queue)
        job = core.prepare(self.repo, self.profile, self.state, sha)
        core.update_queue(self.state, queue, sha, status="running", job=str(job))
        calls = []
        def runner(directory, config, publish):
            calls.append(directory)
            core.run_job(directory, core.read_json(config), publish)
        with core.lock(job / ("." + core.host_name() + ".lock")):
            core.worker(queue, once=True, runner=runner)
            self.assertEqual(calls, [])
        core.worker(queue, once=True, runner=runner)
        self.assertEqual(calls, [job])
        self.assertEqual(core.read_json(queue)["commits"][sha]["status"], "waiting_other_hosts")

    def test_hooks_preserve_previous_behavior_and_remove_exactly(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config, test_mode=True)
        directory = Path(core.git(self.repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        old = b"#!/bin/sh\nprintf preserved > hook-result\nexit 7\n"
        path = directory / "post-commit"
        path.write_bytes(old)
        os.chmod(path, 0o755)
        # Suppress detached worker creation, while executing real chained hooks.
        with patch("local_release.hooks.register_startup") as startup:
            install(queue, test_mode=True)
            startup.assert_not_called()
        # Run old hook directly through the new wrapper. An inactive test queue
        # prevents a detached worker, but discovery itself remains exercised.
        data = core.read_json(queue)
        data.update(enabled=False, test_mode=False)
        core.atomic_json(queue, data)
        sha = self.commit("hook commit")
        self.assertEqual((self.repo / "hook-result").read_text(), "preserved")
        self.assertIn(sha, core.read_json(queue)["commits"])
        result = subprocess.run(["git", "-C", self.repo, "hook", "run", "post-commit"], capture_output=True)
        self.assertEqual(result.returncode, 7)
        remove(queue)
        self.assertEqual(path.read_bytes(), old)

    def test_activation_without_complete_trial_is_rejected(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config)
        with self.assertRaisesRegex(core.ReleaseError, "published trial"):
            install(queue)
        self.assertFalse(core.read_json(queue)["enabled"])

    def test_failed_startup_install_rolls_back_existing_hooks(self):
        queue = core.queue_install(self.repo, self.state, self.profile, self.config)
        proof = self.job()
        core.run_job(proof, {})
        core.atomic_json(proof / "publication.json", {"published": True, "assets": {"sample.zip": {}}})
        directory = Path(core.git(self.repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        original = b"#!/bin/sh\necho owner-hook\n"
        (directory / "post-commit").write_bytes(original)
        with patch("local_release.hooks.register_startup", side_effect=core.ReleaseError("fixture startup failure")):
            with self.assertRaisesRegex(core.ReleaseError, "startup failure"):
                install(queue, proof)
        self.assertEqual((directory / "post-commit").read_bytes(), original)
        self.assertFalse(core.read_json(queue)["enabled"])
        self.assertFalse((directory / "post-commit.before-local-release").exists())

    def test_lock_does_not_steal_interrupted_operation(self):
        with core.lock(self.root / "lock"):
            with self.assertRaises(core.ReleaseError):
                with core.lock(self.root / "lock"):
                    self.fail("lock stolen")

    def test_logs_redact_configured_secrets(self):
        job = self.job()
        ctx = core.Context(job, {"environment": {"TEST_SECRET": "secret-value-example"}})
        ctx.checkout()
        ctx.stage("secret", lambda: ctx.command([sys.executable, "-c", "import os; print(os.environ['TEST_SECRET'])"]))
        log = (job / "logs" / ctx.host / "secret.log").read_text()
        self.assertNotIn("secret-value-example", log)
        self.assertIn("[REDACTED]", log)


class ReleaseTransportTest(unittest.TestCase):
    def test_existing_tag_from_another_sha_is_not_reused(self):
        api = github.GitHub("owner/repo", "fake-token")
        with patch.object(api, "request", return_value={}), patch.object(api, "tag_sha", return_value="foreign"):
            with self.assertRaisesRegex(core.ReleaseError, "collision"):
                api.ensure_release({"tag": "v1", "sha": "ours"}, "Notes")

    def test_incomplete_other_builder_prevents_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertFalse(github.complete_results(Path(folder), {"required_steps": {"linux": ["snap"]}}))

    def test_archive_keeps_assets_with_same_name_and_different_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            class API:
                asset_id = 11
                content = b"old"
                def __init__(self, *args):
                    pass
                def pages(self, path):
                    if path == "/releases":
                        return [{"id": 1, "tag_name": "v1.0.0+1", "html_url": "https://example.invalid/v1", "draft": False}]
                    return [{"id": self.asset_id, "name": "same.zip", "size": 3, "browser_download_url": "https://example.invalid/a"}]
                def tag_sha(self, tag):
                    return "a" * 40
                def download_asset(self, asset, path):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(self.content)
                    return core.digest(path)
            with patch("local_release.archive.GitHub", API), patch("local_release.archive.credential", return_value="fixture"):
                first = archive_releases({"project": "fixture", "repository": "owner/repo"}, Path(folder), {})
                path = Path(folder) / first["releases"]["1"]["assets"]["11"]["path"]
                self.assertEqual(path.read_bytes(), b"old")
                second = archive_releases({"project": "fixture", "repository": "owner/repo"}, Path(folder), {})
                self.assertEqual(first["releases"], second["releases"])
                API.asset_id, API.content = 12, b"new"
                with self.assertRaisesRegex(core.ReleaseError, "differs from GitHub"):
                    archive_releases({"project": "fixture", "repository": "owner/repo"}, Path(folder), {})
                self.assertEqual(path.read_bytes(), b"old")

    def test_archive_skips_draft_transport_and_keeps_final_metadata_in_one_place(self):
        sha = "a" * 40
        class API:
            def __init__(self, *args):
                pass
            def tag_sha(self, tag):
                return None
            def pages(self, path):
                if path == "/releases":
                    return [{"id": 1, "tag_name": "v1.0.0+1", "target_commitish": sha, "draft": True,
                             "body": f"<!-- local-release:fixture-{sha} -->", "html_url": "https://example.invalid/v1"}]
                return [{"id": n, "name": name, "size": 3, "browser_download_url": "https://example.invalid/asset"}
                        for n, name in enumerate([f"local-transfer-fixture-{sha}-job.tar.gz", "sample.zip", "release-manifest.json"])]
            def download_asset(self, asset, path):
                if asset["name"].startswith("local-transfer-"):
                    raise AssertionError("Temporary exchange was archived")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"abc")
                return core.digest(path)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch("local_release.archive.GitHub", API), patch("local_release.archive.credential", return_value="fixture"):
                archive_releases({"project": "fixture", "repository": "owner/repo"}, root, {})
            directory = root / "releases/fixture/1.0.0+1" / sha
            self.assertEqual([p.name for p in (directory / "packages").iterdir()], ["sample.zip"])
            self.assertTrue((directory / "release-manifest.json").is_file())
            self.assertEqual(core.read_json(directory / "manifest.json")["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
