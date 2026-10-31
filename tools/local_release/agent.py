"""One registry and sequential login dispatcher for registered project profiles."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from .core import (Context, ReleaseError, atomic_json, execute_prepared, git,
                   host_name, install_local_excludes, inside, lock, prepare, read_json)


def registry_path():
    if os.name == "nt":
        return Path(os.environ["LOCALAPPDATA"]) / "AI11/LocalRelease/registry.json"
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "ai11-local-release/registry.json"


def register(registry, repo, profile, catalogue, config, hosts=("windows", "linux")):
    data = read_json(registry) if registry.exists() else {"schema": 1, "projects": {}}
    identity = read_json(profile)
    name = identity["project"]
    previous = data["projects"].get(name, {})
    if previous and Path(previous["repo"]).resolve() != repo.resolve():
        raise ReleaseError("This project ID already points to another checkout")
    data["projects"][name] = {**previous, "project": name, "repo": str(repo.resolve()),
        "profile": str(profile.resolve()), "catalogue": str(catalogue.resolve()), "config": str(config.resolve()),
        "hosts": list(hosts), "enabled": True,
        "cursor": previous.get("cursor", git(repo, "rev-parse", "HEAD"))}
    atomic_json(registry, data)
    install_local_excludes(repo)
    return data["projects"][name]


def sync_project_catalogue(registry, catalogue, *, allow_clone=False):
    """Only explicitly registered repositories are discovered, never arbitrary folders."""
    data = read_json(registry) if registry.exists() else {"schema": 1, "projects": {}}
    projects_root = Path(data.get("projects_root", str(Path.home() / "Projects")))
    for entry in read_json(catalogue)["projects"]:
        if not entry.get("enabled") or host_name() not in entry["hosts"]:
            continue
        if not re.fullmatch(r"karnauhov/[A-Za-z0-9_.-]+", entry["repository"]):
            raise ReleaseError("Project catalogue repository requires explicit owner registration")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", entry["directory"]):
            raise ReleaseError("Invalid project checkout directory")
        existing = data["projects"].get(entry["project"])
        repo = Path(existing["repo"]) if existing else projects_root / entry["directory"]
        if not repo.exists() and allow_clone:
            projects_root.mkdir(parents=True, exist_ok=True)
            from .core import capture
            capture(["git", "clone", "https://github.com/" + entry["repository"] + ".git", repo])
        if not repo.exists():
            continue
        profile = inside(repo, entry["profile"])
        if not profile.is_file():
            continue
        config = Path(existing["config"]) if existing else registry.parent / (entry["project"] + ".json")
        if not config.exists():
            atomic_json(config, {"defines_file": str(repo / "api-keys.json"), "sentry_properties": str(repo / "sentry.properties"),
                                 "github_git_credential": True, "auto_provision_flutter": host_name() == "linux", "stream_output": host_name() == "linux"})
            if os.name != "nt":
                config.chmod(0o600)
        register(registry, repo, profile, repo / ".local-releases", config, entry["hosts"])


def update_main(project):
    repo = Path(project["repo"])
    install_local_excludes(repo)
    if git(repo, "branch", "--show-current") != "main":
        raise ReleaseError("Switch this project to main once before enabling the login dispatcher")
    if git(repo, "diff", "HEAD", "--name-only"):
        raise ReleaseError("Tracked owner changes prevent automatic main update; files preserved")
    git(repo, "fetch", "origin")
    git(repo, "merge", "--ff-only", "origin/main")


def discover_jobs(project):
    repo = Path(project["repo"])
    current = git(repo, "rev-parse", "HEAD")
    cursor = project.get("cursor", current)
    commits = git(repo, "rev-list", "--reverse", cursor + ".." + current).splitlines()
    for sha in commits:
        from .retention import deleted
        if deleted(Path(project["catalogue"]), project["project"], sha):
            continue
        if "[skip ci]" not in git(repo, "show", "-s", "--format=%B", sha):
            prepare(repo, Path(project["profile"]), Path(project["catalogue"]), sha,
                    config=read_json(Path(project["config"])))
    return current


def diagnose(ctx):
    """Known diagnostic commands only; never execute text from an error log."""
    commands = [["git", "--version"], ["flutter", "--version", "--machine"]]
    if ctx.host == "linux":
        commands += [["uname", "-a"], ["snapcraft", "--version"], ["snap", "version"], ["unsquashfs", "-version"]]
    for command in commands:
        try:
            ctx.command(command, cwd=ctx.directory)
        except (ReleaseError, OSError):
            pass


def remediation(directory, project):
    path = directory / "results/linux.json"
    if not path.exists():
        return
    result, job = read_json(path), read_json(directory / "job.json")
    if result.get("status") not in ("failed", "stopped", "interrupted") and not result.get("pending_runtime_revision"):
        for name in ("linux-remediation.json", "linux-repair.sh"):
            (directory / "results" / name).unlink(missing_ok=True)
        return
    error = result.get("error", "Linux stage failed")
    attempted = result.get("attempt_runtime_revision", result.get("runtime_revision", 1))
    ready = job.get("preparation_revision", 1) > attempted
    commands = ["#!/usr/bin/env bash", "set -euo pipefail",
                'if [ -n "${AI11_PROJECT_DIR:-}" ]; then cd -- "$AI11_PROJECT_DIR"; fi',
                'test -f scripts/local_release/run-linux.sh || { echo "Run from this project checkout, or set AI11_PROJECT_DIR"; exit 2; }',
                "git fetch origin", "git merge --ff-only origin/main",
                "bash scripts/local_release/run-linux.sh"]
    script = directory / "results/linux-repair.sh"
    script.write_text("\n".join(commands) + "\n", encoding="utf-8", newline="\n")
    atomic_json(directory / "results/linux-remediation.json", {
        "schema": 1, "source_sha": job["sha"], "error": error,
        "runtime_update_ready": ready, "repair_script": "results/linux-repair.sh",
        "attempt_runtime_revision": attempted, "repair_runtime_revision": job.get("preparation_revision", 1),
        "action": "Next Linux login receives the audited runtime repair and retries with diagnostics" if ready else
                  "Next Linux login retries failed stages and returns fresh diagnostics; unknown log text is never executed"})


def project_cycle(project, role):
    from .transport import receive_jobs, sync_results, handoff
    from .github import publish_job, reconcile_published
    profile = read_json(Path(project["profile"]))
    config = read_json(Path(project["config"]))
    root = Path(project["catalogue"])
    if role == "linux":
        update_main(project)
        config.setdefault("auto_provision_flutter", True)
        config["stream_output"] = True
        atomic_json(Path(project["config"]), config)
    from .retention import synchronize, deleted
    synchronize(project, role)
    received = receive_jobs(profile, root, config)
    jobs = {path for path in received}
    if role == "linux":
        project["cursor"] = discover_jobs(project)
    jobs.update(path.parent for path in (root / "releases" / profile["project"]).glob("*/*/job.json"))
    records = []
    for directory in sorted(jobs):
        if deleted(root, profile["project"], directory.name):
            continue
        job = read_json(directory / "job.json")
        publication = directory / "publication.json"
        if publication.exists() and read_json(publication).get("published"):
            if role == "windows":
                closed = directory / "results/exchange-closed.json"
                if not closed.exists() or not read_json(closed).get("closed"):
                    try:
                        sync_results(Context(directory, config, host=role), cleanup=True)
                    except ReleaseError as error:
                        if not str(error).startswith("Busy operation:"):
                            raise
            continue
        print(f"{profile['project']} {job['version']}+{job['build']} {job['sha'][:12]}", flush=True)
        try:
            ctx = Context(directory, config, host=role)
            if role == "linux":
                if reconcile_published(ctx):
                    records.append({"run_id": job["run_id"], "status": "published"})
                    print("Already published; completed packages and stages are preserved.", flush=True)
                    continue
                if (directory / "stop-request.json").exists():
                    records.append({"run_id": job["run_id"], "status": "stopped"})
                    continue
                previous = directory / "results/linux.json"
                if previous.exists() and read_json(previous).get("status") == "failed":
                    ctx.result["current_step"] = "diagnostics"
                    diagnose(ctx)
                # New jobs first prepared here also get the exact same transport.
                if not (directory / "received.json").exists():
                    handoff(ctx)
                execute_prepared(directory, Path(project["config"]), publish=True)
            else:
                sync_results(ctx)
                remediation(directory, project)
                if not (directory / "stop-request.json").exists():
                    publish_job(ctx)
                    if publication.exists() and read_json(publication).get("published"):
                        sync_results(ctx, cleanup=True)
            current = directory / "results" / f"{role}.json"
            state = read_json(current).get("status") if current.exists() else "waiting"
            records.append({"run_id": job["run_id"], "status": state})
        except Exception as error:
            records.append({"run_id": job["run_id"], "status": "failed", "error": str(error)})
            print(f"FAILED {job['run_id']}: {error}", flush=True)
    return records


def cycle(registry, role=None, runner=project_cycle):
    role = role or host_name()
    data = read_json(registry)
    report = {"schema": 1, "host": role, "started": time.time(), "projects": {}}
    with lock(registry.parent / ("." + role + "-agent.lock")):
        for name, project in sorted(data["projects"].items()):
            if not project.get("enabled") or role not in project["hosts"]:
                continue
            print(f"\n=== {name}: {role} ===", flush=True)
            try:
                report["projects"][name] = {"jobs": runner(project, role), "status": "processed"}
                # Persist just this cursor, preserving registry edits from the UI.
                latest = read_json(registry)
                latest["projects"][name]["cursor"] = project["cursor"]
                atomic_json(registry, latest)
            except Exception as error:
                report["projects"][name] = {"status": "failed", "error": str(error)}
                print(f"FAILED {name}: {error}", flush=True)
        report["finished"] = time.time()
        report["status"] = "finished_with_errors" if any(
            value["status"] == "failed" or any(job.get("status") in ("failed", "stopped", "incomplete", "interrupted") for job in value.get("jobs", []))
            for value in report["projects"].values()) else "finished"
        atomic_json(registry.parent / (role + "-agent-result.json"), report)
    print("\n" + report["status"], flush=True)
    for name, record in report["projects"].items():
        print(f"{name}: {record['status']} - " + ", ".join(job["status"] for job in record.get("jobs", [])), flush=True)
    print("Build activity finished. You may reboot manually.", flush=True)
    return report


def install_linux_startup(repo, registry):
    if sys.platform != "linux":
        raise ReleaseError("Install the Linux login entrypoint while running Linux")
    directory = Path.home() / ".config/autostart"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "ai11-local-builds.desktop"
    marker = "X-AI11-LocalRelease=true"
    if path.exists() and marker not in path.read_text():
        raise ReleaseError("An unrelated startup entry already uses this name")
    bootstrap = repo / "scripts/local_release/agent_bootstrap.py"
    # Desktop Entry quoting differs from shell quoting: escape special bytes.
    def quote(value):
        return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$") + '"'
    command = " ".join(quote(part) for part in (sys.executable, bootstrap, "--terminal", "--registry", registry))
    path.write_text("[Desktop Entry]\nType=Application\nName=AI11 Local Builds\nExec=" + command +
                    "\nTerminal=false\nX-GNOME-Autostart-enabled=true\n" + marker + "\n", encoding="utf-8")
    return path


def open_linux_terminal(bootstrap, registry):
    arguments = [sys.executable, str(bootstrap), "--run", "--hold", "--registry", str(registry)]
    for executable, flags in (("gnome-terminal", ["--title=AI11 Local Builds", "--"]),
                              ("konsole", ["-e"]), ("xfce4-terminal", ["-x"]), ("x-terminal-emulator", ["-e"])):
        if shutil.which(executable):
            subprocess.Popen([executable, *flags, *arguments], start_new_session=True)
            return
    raise ReleaseError("No supported terminal emulator is installed")
