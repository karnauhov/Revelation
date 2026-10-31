"""Local HTTP integration: catalogues, control, restart recovery and file access."""

from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import atomic_json, digest, host_name, read_json, capture, git, queue_install
from local_release.service import Dashboard, make_server


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.registry = self.root / "registry.json"
        self.jobs = {}
        projects = {}
        for name, letter in (("first", "a"), ("second", "b")):
            directory = self.root / name / "releases" / name / "1.0.0+1" / (letter * 40)
            package = directory / "packages/package.zip"
            package.parent.mkdir(parents=True)
            package.write_bytes(b"one canonical package")
            manifest = {"project": name, "sha": letter * 40, "version": "1.0.0", "build": 1, "status": "archived",
                "packages": {package.name: {"path": "packages/" + package.name, "size": package.stat().st_size, "sha256": digest(package)}}}
            atomic_json(directory / "manifest.json", manifest)
            config = self.root / (name + ".json")
            atomic_json(config, {"environment": {"SECRET_TOKEN": "must-stay-private"}})
            projects[name] = {"project": name, "catalogue": str(self.root / name), "hosts": [host_name()], "enabled": True,
                              "config": str(config), "repo": str(self.root / name), "profile": str(self.root / "profile.json")}
            self.jobs[name] = directory
        atomic_json(self.registry, {"schema": 1, "projects": projects})
        self.server = make_server(self.registry, 0)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)

    def close(self):
        for process in self.server.dashboard.children.values():
            if process.poll() is None:
                process.wait(timeout=10)
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, data=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=10)
        content = json.dumps(data) if data is not None else None
        connection.request("POST" if data is not None else "GET", path, body=content, headers=headers or {})
        response = connection.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return result

    def control(self, action):
        return self.request("/api/action", {"project": "first", "sha": "a" * 40, "action": action}, {
            "Content-Type": "application/json", "X-AI11-Token": self.server.dashboard.token,
            "Origin": f"http://127.0.0.1:{self.port}"})

    def wait(self, predicate):
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(.08)
        self.fail("Timed out waiting for the owned fixture builder")

    def prepare_runnable(self):
        directory = self.jobs["first"]
        runtime = directory / "runtime/local_release/cli.py"
        runtime.parent.mkdir(parents=True)
        tools = str(Path(__file__).resolve().parents[2])
        runtime.write_text('''import sys, time
from pathlib import Path
sys.path.insert(0, TOOLS)
from local_release.core import Context, atomic_json, lock, read_json
from local_release.processes import JobStopped
directory=Path(sys.argv[sys.argv.index('--job')+1])
ctx=Context(directory, {})
ctx.workspace.mkdir(parents=True,exist_ok=True)
with lock(directory/('.'+ctx.host+'.lock')):
 attempt=directory/'results/attempt.json'
 count=read_json(attempt)['count']+1 if attempt.exists() else 1
 atomic_json(attempt,{'count':count})
 try:
  ctx.stage('fixture',lambda:ctx.command([sys.executable,'-c','import time; time.sleep(30)' if count==1 else 'print("complete")']))
  ctx.result.update(status='built',current_step=None);ctx.save()
 except JobStopped:
  sys.exit(2)
'''.replace("TOOLS", repr(tools)))
        atomic_json(directory / "job.json", {"schema": 1, "project": "first", "sha": "a" * 40, "run_id": "first-a",
            "version": "1.0.0", "build": 1, "profile": {"adapter": "local_release.profiles.native_fixture"},
            "required_steps": {host_name(): ["fixture"]}, "runtime_sha256": {"local_release/cli.py": digest(runtime)}})
        return directory

    def test_lists_two_project_archives_without_copying_and_serves_verified_file(self):
        status, data, _ = self.request("/api/state")
        self.assertEqual(status, 200)
        value = json.loads(data)
        self.assertEqual([p["name"] for p in value["projects"]], ["first", "second"])
        self.assertNotIn(b"must-stay-private", data)
        link = value["projects"][0]["releases"][0]["files"][0]["url"]
        self.assertEqual(self.request(link)[1], b"one canonical package")
        self.assertEqual(len(list(self.root.rglob("package.zip"))), 2)
        self.assertEqual(self.control("start")[0], 400)
        self.jobs["first"].joinpath("packages/package.zip").write_bytes(b"changed")
        self.assertEqual(self.request(link)[0], 400)

    def test_rejects_foreign_origin_host_missing_token_and_file_traversal(self):
        self.assertEqual(self.request("/api/state", headers={"Host": "attacker.invalid"})[0], 403)
        payload = {"project": "first", "sha": "a" * 40, "action": "stop"}
        self.assertEqual(self.request("/api/action", payload, {"Content-Type": "application/json"})[0], 403)
        self.assertEqual(self.request("/api/action", payload, {"Content-Type": "application/json", "X-AI11-Token": self.server.dashboard.token, "Origin": "https://foreign.invalid"})[0], 403)
        query = urlencode({"project": "first", "sha": "a" * 40, "log": "../../../../first.json"})
        self.assertEqual(self.request("/api/file?" + query)[0], 400)

    def test_real_start_stop_retry_and_service_restart_preserve_packages(self):
        directory = self.prepare_runnable()
        package = directory / "packages/package.zip"
        expected = digest(package)
        self.assertEqual(self.control("start")[0], 200)
        self.wait(lambda: self.server.dashboard.busy(directory))
        self.assertEqual(self.control("start")[0], 400)
        # A fresh service sees the actual OS lock, without trusting old PIDs.
        restarted = Dashboard(self.registry)
        self.assertTrue(restarted.state()["projects"][0]["releases"][0]["active"])
        self.assertEqual(self.control("stop")[0], 200)
        result = directory / "results" / (host_name() + ".json")
        self.wait(lambda: result.exists() and read_json(result)["status"] == "stopped")
        self.wait(lambda: all(p.poll() is not None for p in self.server.dashboard.children.values()))
        self.assertEqual(self.control("retry")[0], 200)
        self.wait(lambda: read_json(result)["status"] == "built")
        self.assertEqual(read_json(directory / "results/attempt.json")["count"], 2)
        self.assertEqual(digest(package), expected)
        self.assertFalse((directory / "stop-request.json").exists())

    def test_unverified_package_and_stale_running_state_are_explicit(self):
        directory = self.prepare_runnable()
        manifest = read_json(directory / "manifest.json")
        manifest["unverified_packages"] = manifest.pop("packages")
        atomic_json(directory / "manifest.json", manifest)
        atomic_json(directory / "results" / (host_name() + ".json"), {"status": "running", "steps": {}})
        release = self.server.dashboard.state()["projects"][0]["releases"][0]
        self.assertFalse(release["files"][0]["verified"])
        self.assertEqual(release["hosts"][host_name()]["status"], "interrupted")
        atomic_json(directory / "results" / (host_name() + ".json"), {
            "status": "pending", "steps": {}, "runtime_revision": 14,
            "attempt_runtime_revision": 13, "pending_runtime_revision": 14})
        repair = self.server.dashboard.state()["projects"][0]["releases"][0]["hosts"][host_name()]
        self.assertEqual(repair["attempt_runtime_revision"], 13)
        self.assertEqual(repair["pending_runtime_revision"], 14)
        atomic_json(directory / "results" / (host_name() + ".json"), {
            "status": "failed", "current_step": "verify-linux", "error": "Linux phases incomplete: build",
            "steps": {"verify-linux": {"status": "failed", "error": "Snap authentication is required"}}})
        failure = self.server.dashboard.state()["projects"][0]["releases"][0]["hosts"][host_name()]
        self.assertEqual(failure["error"], "Snap authentication is required")

    def test_commit_discovery_is_visible_but_does_not_start_a_gated_project(self):
        repo = self.root / "first"
        capture(["git", "init", repo])
        git(repo, "config", "user.name", "Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "commit", "--allow-empty", "-m", "baseline")
        profile = self.root / "profile.json"
        atomic_json(profile, {"project": "first"})
        queue_install(repo, repo, profile, self.root / "first.json")
        git(repo, "commit", "--allow-empty", "-m", "maintenance\n\n[skip ci]")
        skipped = git(repo, "rev-parse", "HEAD")
        git(repo, "commit", "--allow-empty", "-m", "next build")
        queued = git(repo, "rev-parse", "HEAD")
        self.server.dashboard.scan()
        state = json.loads(self.request("/api/state")[1])["projects"][0]
        self.assertFalse(state["automatic_builds"])
        self.assertEqual(state["queue"][skipped]["status"], "skipped")
        self.assertEqual(state["queue"][queued]["status"], "queued")
        self.assertEqual(self.server.dashboard.children, {})

    def test_completed_linux_and_pending_windows_are_distinct_from_publication(self):
        directory = self.prepare_runnable()
        job = read_json(directory / "job.json")
        job["required_steps"] = {"linux": ["verify-linux"], "windows": ["integration-android", "integration-web"]}
        job["artifacts"] = ["package.zip", "missing.snap"]
        atomic_json(directory / "job.json", job)
        atomic_json(directory / "results/linux.json", {"status": "built", "steps": {"verify-linux": {"status": "passed"}}})
        atomic_json(directory / "results/windows.json", {"status": "incomplete", "steps": {}})
        release = json.loads(self.request("/api/state")[1])["projects"][0]["releases"][0]
        self.assertEqual(release["waiting_checks"], {"windows": ["integration-android", "integration-web"]})
        self.assertEqual(release["hosts"]["linux"]["status"], "built")
        self.assertEqual(release["missing_packages"], ["missing.snap"])
        atomic_json(directory / "publication.json", {"published": True, "url": "https://github.com/fixture/release"})
        published = json.loads(self.request("/api/state")[1])["projects"][0]["releases"][0]
        self.assertEqual(published["status"], "published")
        self.assertFalse(published["controllable"])
        self.assertTrue(published["publication"]["published"])
        self.assertEqual(published["waiting_checks"], {})
        self.assertTrue(published["hosts"]["windows"]["verified_elsewhere"])

    def test_prepared_versions_sort_numerically_with_archived_releases(self):
        base = self.jobs["first"].parents[1]
        archived = base / "1.0.9+999" / ("c" * 40)
        atomic_json(archived / "manifest.json", {"version": "1.0.9", "build": 999, "status": "archived", "packages": {}})
        prepared = base / "1.0.10+1000" / ("d" * 40)
        atomic_json(prepared / "job.json", {"version": "1.0.10", "build": 1000, "required_steps": {}, "artifacts": []})
        releases = json.loads(self.request("/api/state")[1])["projects"][0]["releases"]
        self.assertEqual([record["version"] for record in releases], ["1.0.10", "1.0.9", "1.0.0"])

    def test_local_completion_waits_for_the_other_os_without_a_failed_build_status(self):
        directory = self.prepare_runnable()
        local, peer = host_name(), "linux" if host_name() != "linux" else "windows"
        job = read_json(directory / "job.json")
        job["required_steps"] = {local: [], peer: ["integration-" + peer]}
        atomic_json(directory / "job.json", job)
        atomic_json(directory / f"results/{local}.json", {"status": "built", "steps": {}})
        release = json.loads(self.request("/api/state")[1])["projects"][0]["releases"][0]
        self.assertEqual(release["status"], "waiting_other_hosts")
        self.assertEqual(release["waiting_hosts"], [peer])
        self.assertEqual(release["hosts"][local]["missing"], [])


if __name__ == "__main__":
    unittest.main()
