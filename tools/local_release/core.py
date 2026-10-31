"""Durable release jobs, isolated builders, redacted logs and Git discovery.

No project-specific build commands or credentials belong in this module.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid


class ReleaseError(RuntimeError):
    pass


class SourceUnavailable(ReleaseError):
    """The exact local source commit is not yet accessible on GitHub."""


def hidden_flags():
    """GUI/background parents must never allocate consoles for CLI children."""
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
        return result.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        # Windows indexers/antivirus may briefly hold the destination without
        # delete sharing. Retain the exact new payload and retry for <= 2 s.
        for attempt in range(8):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if os.name != "nt" or attempt == 7:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        temporary.unlink(missing_ok=True)


def capture(argv, cwd=None, env=None) -> str:
    result = subprocess.run(
        [str(arg) for arg in argv], cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8",
        errors="replace", check=False,
        creationflags=hidden_flags(),
    )
    if result.returncode:
        # External stderr may include credentials. Persist it only via Context.
        raise ReleaseError(f"{Path(str(argv[0])).name} exited {result.returncode}")
    return result.stdout.strip()


def git(repo: Path, *args) -> str:
    return capture(["git", "-C", repo, *args])


def host_name() -> str:
    return {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}[platform.system()]


def install_local_excludes(repo: Path):
    """Keep private release state ignored even while an older branch is checked out."""
    path = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude"))
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    additions = [line for line in ("/.local-releases/", "**/.gradle/") if line not in original.splitlines()]
    if additions:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(original.rstrip() + "\n# AI11 local build state (all branches)\n" + "\n".join(additions) + "\n", encoding="utf-8")


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ReleaseError(f"Path escapes release directory: {relative}")
    return path


@contextlib.contextmanager
def lock(path: Path):
    """OS-backed SQLite lock, automatically released on process exit/reboot.

    Use a local filesystem (including a dual-boot shared data volume), not a
    synchronizing cloud folder. No timeout or PID guessing can steal a live lock.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=0)
    try:
        connection.execute("BEGIN EXCLUSIVE")
        yield
    except sqlite3.OperationalError as error:
        raise ReleaseError(f"Busy operation: {path}") from error
    finally:
        connection.rollback()
        connection.close()


class Redactor:
    def __init__(self, values=()):
        self.values = sorted({str(v) for v in values if v and len(str(v)) >= 4}, key=len, reverse=True)

    def __call__(self, text: str) -> str:
        for value in self.values:
            text = text.replace(value, "[REDACTED]")
        return re.sub(r"(?i)(bearer\s+|auth_token\s*[=:]\s*)\S+", r"\1[REDACTED]", text)


class Context:
    def __init__(self, job_dir: Path, config: dict, host: str | None = None):
        self.directory = job_dir.resolve()
        self.job = read_json(self.directory / "job.json")
        if self.job["schema"] != 1:
            raise ReleaseError("Unsupported job schema")
        self.host = host or host_name()
        self.config = config
        self.root = self.directory.parents[3]
        self.workspace = self.root / "w" / self.job["sha"][:12] / self.host[0]
        self.output = self.directory / "packages"
        self.result_path = self.directory / "results" / f"{self.host}.json"
        self.result = read_json(self.result_path) if self.result_path.exists() else {
            "schema": 1, "project": self.job["project"], "sha": self.job["sha"],
            "run_id": self.job["run_id"], "host": self.host, "steps": {}, "status": "pending",
        }
        if (self.result["sha"], self.result["run_id"]) != (self.job["sha"], self.job["run_id"]):
            raise ReleaseError("Result belongs to a different job")
        for step in self.result["steps"].values():
            step["outputs"] = {name.replace("\\", "/"): value for name, value in step.get("outputs", {}).items()}
        self.env = os.environ.copy()
        self.env.update({str(k): str(v) for k, v in config.get("environment", {}).items()})
        self.redact = Redactor(v for k, v in self.env.items() if re.search("TOKEN|PASSWORD|SECRET|BASE64", k))
        self.output.mkdir(exist_ok=True)

    def save(self):
        self.result["updated"] = time.time()
        self.result["runtime_revision"] = self.job.get("preparation_revision", 1)
        atomic_json(self.result_path, self.result)

    def refresh_redaction(self, values=()):
        self.redact = Redactor([*self.redact.values, *values])

    def command(self, argv, *, cwd=None, env=None, stdin=None):
        step = self.result.get("current_step", "preflight")
        log = self.directory / "logs" / self.host / f"{step}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        command_env = self.env.copy()
        command_env.update(env or {})
        resolved = [str(arg) for arg in argv]
        if resolved[0] == "python":
            resolved[0] = sys.executable
        elif os.name == "nt":
            resolved[0] = shutil.which(resolved[0], path=command_env.get("PATH")) or resolved[0]
        # Arguments contain paths/flags only. Secret values are supplied in env/files.
        with log.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(self.redact(json.dumps(resolved)) + "\n")
            stream.flush()
            process = subprocess.Popen(
                resolved, cwd=cwd or getattr(self, "command_workspace", self.workspace), env=command_env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=stdin,
                encoding="utf-8", errors="replace", bufsize=1,
                start_new_session=os.name != "nt",
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0) | hidden_flags(),
            )
            from .processes import StopMonitor, JobStopped, terminate_tree
            monitor = StopMonitor(process, self.directory / "stop-request.json")
            monitor.__enter__()
            output = []
            try:
                for line in process.stdout:
                    output.append(line)
                    stream.write(self.redact(line))
                    stream.flush()
                    if self.config.get("stream_output") and sys.stdout:
                        print(self.redact(line), end="", flush=True)
                code = process.wait()
            except BaseException:
                terminate_tree(process)
                process.wait()
                raise
            finally:
                process.stdout.close()
                monitor.__exit__()
            stream.write(f"exit_code={code}\n")
            if monitor.stopped:
                raise JobStopped("Stopped by owner; verified packages and checkpoints preserved")
        if code:
            raise ReleaseError(f"{step}: {Path(resolved[0]).name} exited {code}; log: {log}")
        return "".join(output)

    def stage(self, name, action, outputs=(), *, always=False):
        if (self.directory / "stop-request.json").exists():
            from .processes import JobStopped
            raise JobStopped("Stopped by owner before the next stage")
        previous = self.result["steps"].get(name, {})
        paths = [inside(self.directory, value) for value in outputs]
        if not always and previous.get("status") == "passed":
            hashes = previous.get("outputs", {})
            if all(path.is_file() and hashes.get(path.relative_to(self.directory).as_posix()) == digest(path)
                   for path in paths):
                return False
        self.result.update(status="running", current_step=name)
        self.result.pop("error", None)
        # Only declared dependents are invalidated. JSON key order and independent
        # platform branches cannot make a successful build disappear on retry.
        if name in self.result["steps"]:
            self.invalidate_dependents(name)
        self.result["steps"][name] = {"status": "running", "started": time.time()}
        self.save()
        try:
            action()
            if any(not path.is_file() for path in paths):
                raise ReleaseError(f"{name}: required output is missing")
            self.result["steps"][name].update(
                status="passed", finished=time.time(),
                outputs={p.relative_to(self.directory).as_posix(): digest(p) for p in paths},
            )
            self.save()
            print(f"PASS {self.host}/{name}", flush=True)
            return True
        except BaseException as error:
            from .processes import JobStopped
            state = "stopped" if isinstance(error, JobStopped) else "failed"
            self.result.update(status=state, error=self.redact(str(error)))
            self.result["steps"][name].update(status=state, finished=time.time(), error=self.redact(str(error)))
            self.save()
            raise

    def invalidate_dependents(self, name):
        dependencies = self.job.get("step_dependencies", {})
        affected = {name}
        while True:
            extra = {step for step, parents in dependencies.items() if affected.intersection(parents)}
            if extra <= affected:
                break
            affected.update(extra)
        for step in affected - {name}:
            self.result["steps"].pop(step, None)

    def checkout(self):
        bundle = self.directory / "source.bundle"
        if digest(bundle) != self.job["source_bundle_sha256"]:
            raise ReleaseError("Source bundle digest mismatch")
        if not self.workspace.exists():
            self.workspace.parent.mkdir(parents=True, exist_ok=True)
            hooks = (self.workspace / ".git/ai11-no-hooks").as_posix()
            capture(["git", "-c", "core.hooksPath=" + hooks, "clone", "--no-checkout", "-c", "core.longpaths=true", bundle, self.workspace])
            git(self.workspace, "config", "core.hooksPath", hooks)
            git(self.workspace, "checkout", "--detach", self.job["sha"])
        if git(self.workspace, "rev-parse", "HEAD") != self.job["sha"]:
            raise ReleaseError("Builder checkout SHA differs from job")
        changed = git(self.workspace, "diff", "HEAD", "--name-only", "--no-ext-diff").splitlines()
        allowed = set(self.job.get("generated_output_paths", []))
        overlays = self.job.get("generated_source_overlays", {})
        if any(path not in allowed and not (path in overlays and digest(self.workspace / path) == overlays[path]) for path in changed):
            raise ReleaseError("Builder tracked sources changed; inspect before resuming")

    def attach_short_workspace(self):
        drive = self.config.get("workspace_drive")
        if os.name != "nt" or self.host != "windows" or not drive:
            return
        drive = drive.upper()
        if not re.fullmatch(r"[D-Z]:", drive):
            raise ReleaseError("workspace_drive must be a free Windows drive letter D: through Z:")
        import ctypes
        used = ctypes.windll.kernel32.GetLogicalDrives()
        if used & (1 << (ord(drive[0]) - ord("A"))):
            raise ReleaseError("Workspace drive is already occupied; it will not be changed: " + drive)
        target = self.root / "w"
        capture(["subst", drive, str(target)])
        self.command_workspace = Path(drive + "/") / self.workspace.relative_to(target)
        self.owned_drive = drive
        self.drive_target = target
        atomic_json(self.directory / "results/windows-workspace.json", {
            "drive": drive, "target": str(target), "workspace": str(self.command_workspace),
            "run_id": self.job["run_id"], "temporary": True})

    def detach_short_workspace(self):
        drive = getattr(self, "owned_drive", None)
        if drive:
            mappings = capture(["subst"])
            expected = str(self.drive_target).replace("/", "\\").casefold()
            matching = [line for line in mappings.splitlines() if line.upper().startswith(drive + "\\:")]
            if len(matching) != 1 or matching[0].split("=>", 1)[-1].strip().casefold() != expected:
                raise ReleaseError("Workspace drive changed externally; preserved for inspection")
            capture(["subst", drive, "/D"])
            self.owned_drive = None


def prepare(repo: Path, profile_path: Path, root: Path, sha="HEAD", config=None) -> Path:
    repo, root = repo.resolve(), root.resolve()
    install_local_excludes(repo)
    profile = read_json(profile_path)
    full_sha = git(repo, "rev-parse", f"{sha}^{{commit}}")
    adapter = importlib.import_module(profile["adapter"])
    metadata = adapter.metadata(repo, full_sha, profile)
    if hasattr(adapter, "input_metadata"):
        if config is None:
            raise ReleaseError("This profile requires --config to pin host-independent compile inputs")
        metadata.update(adapter.input_metadata(config))
    from .catalogue import release_directory
    destination = release_directory(root, profile["project"], metadata["version"], metadata["build"], full_sha)
    with lock(root / ".prepare.lock"):
        if destination.exists():
            existing = read_json(destination / "job.json")
            if existing["sha"] != full_sha or existing["profile"] != profile:
                raise ReleaseError("Existing job has a different immutable profile")
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=".prepare-", dir=destination.parent))
        try:
            # A private clone avoids modifying refs or hooks in the owner's checkout.
            clone = temporary / "clone"
            capture(["git", "clone", "--shared", "--bare", repo, clone])
            git(clone, "update-ref", "refs/heads/local-release", full_sha)
            git(clone, "bundle", "create", str(temporary / "source.bundle"), "refs/heads/local-release")
            shutil.rmtree(clone)
            runtime = temporary / "runtime" / "local_release"
            runtime.mkdir(parents=True)
            source = Path(__file__).parent
            for item in source.glob("*.py"):
                shutil.copy2(item, runtime / item.name)
            # Profile adapters are shipped with the coordinator, outside source.bundle.
            shutil.copytree(source / "profiles", runtime / "profiles", ignore=shutil.ignore_patterns("__pycache__"))
            runtime_hashes = {p.relative_to(temporary / "runtime").as_posix(): digest(p)
                              for p in runtime.rglob("*.py")}
            job = dict(schema=1, project=profile["project"], repository=profile["repository"],
                       sha=full_sha, run_id=f"{profile['project']}-{full_sha}", profile=profile,
                       created=time.time(), source_bundle_sha256=digest(temporary / "source.bundle"),
                       runtime_sha256=runtime_hashes, **metadata)
            atomic_json(temporary / "job.json", job)
            (temporary / "release_notes.txt").write_text(job["release_notes"] + "\n", encoding="utf-8", newline="\n")
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return destination


def verify_runtime(directory: Path):
    job = read_json(directory / "job.json")
    for relative, expected in job["runtime_sha256"].items():
        if digest(inside(directory / "runtime", relative)) != expected:
            raise ReleaseError("Runtime differs from the prepared job")


def queue_install(repo: Path, root: Path, profile: Path, config: Path, *, test_mode=False):
    """Record a complete historical boundary; hook activation is a separate step."""
    root.mkdir(parents=True, exist_ok=True)
    project = read_json(profile)["project"]
    path = root / f"{project}-queue.json"
    with lock(root / ".queue.lock"):
        if path.exists():
            raise ReleaseError("Queue already installed; preserve its boundary and jobs")
        baseline = git(repo, "rev-list", "--all", "HEAD").splitlines()
        data = dict(schema=1, project=project, repo=str(repo.resolve()),
                    profile=str(profile.resolve()), config=str(config.resolve()),
                    baseline=baseline, commits={}, enabled=False, test_mode=test_mode)
        atomic_json(path, data)
    return path


def record_commit_event(repo: Path, queue_path: Path, sha="HEAD"):
    """Durable hook spool independent of the queue lock, including amended tips."""
    full_sha = git(repo, "rev-parse", f"{sha}^{{commit}}")
    folder = queue_path.parent / "events" / queue_path.stem
    atomic_json(folder / (full_sha + ".json"), {"sha": full_sha})
    return full_sha


def discover(repo: Path, root: Path, queue_path: Path):
    """Discover every reachable local/remote/tag commit, independently of branch/path."""
    with lock(root / ".queue.lock"):
        data = read_json(queue_path)
        pending_version = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "ai11-version-pending.json"))
        if pending_version.exists() and git(repo, "rev-parse", "HEAD") != read_json(pending_version)["base_head"]:
            return data
        known = set(data["baseline"]) | set(data["commits"])
        events = sorted((root / "events" / queue_path.stem).glob("*.json"))
        tips = [read_json(path)["sha"] for path in events]
        commits = git(repo, "rev-list", "--reverse", "--topo-order", "--all", "HEAD", *tips).splitlines()
        for sha in commits:
            if sha in known:
                continue
            message = git(repo, "show", "-s", "--format=%B", sha)
            skip = "[skip ci]" in message
            data["commits"][sha] = {"status": "skipped" if skip else "queued",
                                    "reason": "[skip ci] in full commit message" if skip else None,
                                    "sequence": len(data["commits"]) + 1,
                                    "discovered": time.time()}
        atomic_json(queue_path, data)
        for path in events:
            path.unlink(missing_ok=True)
        return data


def update_queue(root, path, sha, **fields):
    with lock(root / ".queue.lock"):
        data = read_json(path)
        data["commits"][sha].update(fields)
        atomic_json(path, data)


def run_job(directory: Path, config: dict, publish=False):
    verify_runtime(directory)
    context = Context(directory, config)
    with lock(directory / f".{context.host}.lock"):
        try:
            if publish:
                # Receive peer evidence before any local build can fail. Receipts
                # travel back with the result and govern exchange cleanup.
                from .transport import sync_results
                try:
                    if context.host == "windows":
                        from .transport import handoff
                        handoff(context)
                    context.stage("exchange-receive", lambda: sync_results(context), always=True)
                except SourceUnavailable:
                    # Local commits build before push. Remote transfer resumes
                    # once that exact SHA becomes accessible, without pushing it.
                    pass
                except (ReleaseError, OSError) as exchange_error:
                    from .processes import JobStopped
                    if isinstance(exchange_error, JobStopped):
                        raise
                    context.result["transfer_error"] = context.redact(str(exchange_error))
                    context.save()
                    atomic_json(context.directory / "results" / f"{context.host}-outbox.json", {
                        "pending": True, "sha": context.job["sha"], "reason": context.redact(str(exchange_error)),
                        "action": "Local stages continue; transfer is retried after network/authentication recovery"})
            context.stage("checkout", context.checkout, always=True)
            context.attach_short_workspace()
            adapter = importlib.import_module(context.job["profile"]["adapter"])
            adapter.run(context)
            complete = all(context.result["steps"].get(name, {}).get("status") == "passed"
                           for name in context.job["required_steps"][context.host])
            context.result.update(status="built" if complete else "incomplete", current_step=None)
            context.result.pop("error", None)
            context.save()
            from .catalogue import catalogue_job
            catalogue_job(context)
            if publish:
                from .transport import send_result, sync_results
                send_result(context)
                sync_results(context)
                from .github import publish_job
                publish_job(context)
        except SourceUnavailable as error:
            context.result.update(status="waiting_source_sha", current_step=None, error=context.redact(str(error)))
            context.save()
            atomic_json(context.directory / "results" / f"{context.host}-outbox.json", {
                "pending": True, "sha": context.job["sha"], "waiting_source_sha": True,
                "reason": context.redact(str(error)), "action": "Worker resumes when the exact source SHA is accessible on GitHub"})
        except BaseException as error:
            from .processes import JobStopped
            context.result.update(status="stopped" if isinstance(error, JobStopped) else "failed", error=context.redact(str(error)))
            context.save()
            if publish:
                try:
                    from .transport import send_result
                    send_result(context)
                except Exception as transfer_error:
                    atomic_json(context.directory / "results" / f"{context.host}-outbox.json", {
                        "pending": True, "sha": context.job["sha"],
                        "reason": context.redact(str(transfer_error)),
                        "action": "Rerun send-result after restoring network/authentication"})
            raise
        finally:
            context.detach_short_workspace()
    return context


def execute_prepared(directory: Path, config_path: Path, publish=False):
    command = [sys.executable, str(directory / "runtime/local_release/cli.py"), "run", "--job", str(directory),
               "--config", str(config_path)]
    if publish:
        command.append("--publish")
    result = subprocess.run(command, check=False, creationflags=hidden_flags())
    if result.returncode:
        raise ReleaseError("Prepared builder exited " + str(result.returncode))


def worker(queue_path: Path, *, once=False, interval=30, runner=None):
    root = queue_path.parent
    with lock(root / ".worker.lock"):
        while True:
            data = read_json(queue_path)
            if not data["enabled"] and not data["test_mode"]:
                raise ReleaseError("Automatic worker has not been activated")
            data = discover(Path(data["repo"]), root, queue_path)
            for sha, entry in sorted(data["commits"].items(), key=lambda pair: pair[1]["sequence"]):
                if entry["status"] == "running" and entry.get("job"):
                    try:
                        with lock(Path(entry["job"]) / ("." + host_name() + ".lock")):
                            pass
                    except ReleaseError as error:
                        if str(error).startswith("Busy operation:"):
                            continue
                        raise
                    # Previous observer exited. The builder lock is free and
                    # verified step checkpoints decide what actually needs work.
                    entry["status"] = "queued"
                if entry["status"] == "waiting_source_sha":
                    try:
                        from .github import GitHub, credential
                        config = read_json(Path(data["config"]))
                        GitHub(read_json(Path(data["profile"]))["repository"], credential(config)).require_source(sha)
                    except ReleaseError:
                        continue
                    entry["status"] = "queued"
                if entry["status"] != "queued":
                    publication = Path(entry["job"]) / "publication.json" if entry.get("job") else None
                    if entry["status"] != "skipped" and publication and publication.exists() and read_json(publication).get("published"):
                        update_queue(root, queue_path, sha, status="published")
                    continue
                try:
                    job = prepare(Path(data["repo"]), Path(data["profile"]), root, sha, config=read_json(Path(data["config"])))
                    update_queue(root, queue_path, sha, status="running", job=str(job), started=time.time(), error=None)
                    if runner:
                        runner(job, Path(data["config"]), not data["test_mode"])
                    else:
                        execute_prepared(job, Path(data["config"]), publish=not data["test_mode"])
                    publication = job / "publication.json"
                    result_path = job / "results" / (host_name() + ".json")
                    result = read_json(result_path) if result_path.exists() else {}
                    status = ("published" if publication.exists() and read_json(publication).get("published") else
                              "waiting_source_sha" if result.get("status") == "waiting_source_sha" else "waiting_other_hosts")
                    update_queue(root, queue_path, sha, status=status, job=str(job), error=None)
                except Exception as error:
                    # Continue later commits; a failed SHA is never replaced by the newest SHA.
                    saved_job = read_json(queue_path)["commits"][sha].get("job")
                    result_path = Path(saved_job) / "results" / (host_name() + ".json") if saved_job else None
                    stopped = result_path and result_path.exists() and read_json(result_path).get("status") == "stopped"
                    update_queue(root, queue_path, sha, status="stopped" if stopped else "failed", error=str(error))
            if once:
                return
            time.sleep(interval)
