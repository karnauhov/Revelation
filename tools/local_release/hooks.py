"""Reversible chained hooks and per-user login observer registration."""

from __future__ import annotations

import os
import hashlib
from pathlib import Path
import shlex
import subprocess
import sys

from .core import ReleaseError, atomic_json, capture, git, lock, read_json
from .github import complete_results


MARKER = "# AI11 shared local release hook v1"


def hook_directory(repo):
    return Path(git(repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))


def install(queue, proof=None, test_mode=False):
    root = queue.parent
    with lock(root / ".queue.lock"):
        data = read_json(queue)
        if data["enabled"]:
            raise ReleaseError("Trigger is already installed; remove it before updating")
        if test_mode and not data["test_mode"]:
            raise ReleaseError("Test trigger requires an isolated test queue")
        if not test_mode:
            if not proof:
                raise ReleaseError("A complete published trial is required before activation")
            job = read_json(proof / "job.json")
            publication = read_json(proof / "publication.json")
            if job["project"] != data["project"] or not publication.get("published") or not complete_results(proof, job):
                raise ReleaseError("Trial proof is incomplete")
            if set(publication.get("assets", {})) != set(job["artifacts"]):
                raise ReleaseError("Trial release assets are incomplete")
        repo = Path(data["repo"])
        directory = hook_directory(repo)
        directory.mkdir(parents=True, exist_ok=True)
        script = Path(__file__).with_name("cli.py").resolve()
        paths = []
        names = ("post-commit", "post-merge", "post-checkout", "post-rewrite")
        for name in names:
            if (directory / (name + ".before-local-release")).exists():
                raise ReleaseError("Previous hook backup already exists: " + name)
        startup = None
        try:
            for name in names:
                path = directory / name
                previous = directory / (name + ".before-local-release")
                if path.exists():
                    path.rename(previous)
                paths.append(str(path))
                old = shlex.quote(previous.as_posix())
                command = " ".join(shlex.quote(str(p).replace("\\", "/")) for p in
                                   (sys.executable, script, "notify", "--queue", queue.resolve()))
                path.write_text("#!/bin/sh\n" + MARKER + "\n"
                                + 'release_sha=$(git rev-parse HEAD) || release_sha=HEAD\nrelease_status=0\n'
                                + f"if [ -x {old} ]; then {old} \"$@\" || release_status=$?; fi\n"
                                + command + ' --sha "$release_sha" >/dev/null 2>&1 || :\n'
                                + 'exit "$release_status"\n', encoding="utf-8", newline="\n")
                os.chmod(path, 0o755)
            # Test mode never installs a user-session startup item.
            if not test_mode:
                startup = register_startup(data["project"], queue)
            data.update(enabled=True, hook_paths=paths, startup=startup)
            atomic_json(queue, data)
        except BaseException:
            if startup:
                unregister_startup(startup)
            for value in reversed(paths):
                path = Path(value)
                path.unlink(missing_ok=True)
                previous = path.with_name(path.name + ".before-local-release")
                if previous.exists():
                    previous.rename(path)
            raise


def register_startup(project, queue):
    argv = [sys.executable, str(Path(__file__).with_name("cli.py").resolve()), "worker", "--queue", str(queue.resolve())]
    if os.name == "nt":
        suffix = hashlib.sha256(str(queue.resolve()).encode()).hexdigest()[:8]
        name = "AI11LocalRelease-" + project + "-" + suffix
        query = subprocess.run(["schtasks", "/Query", "/TN", name], capture_output=True, check=False)
        if query.returncode == 0:
            raise ReleaseError("Existing startup task would be overwritten: " + name)
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if not pythonw.is_file():
            raise ReleaseError("pythonw.exe is required for a hidden Windows startup observer")
        argv = [str(pythonw), str(Path(__file__).with_name("cli.py").resolve()), "notify", "--queue", str(queue.resolve())]
        capture(["schtasks", "/Create", "/SC", "ONLOGON", "/TN", name,
                 "/TR", subprocess.list2cmdline(argv), "/F"])
        return {"kind": "scheduled-task", "name": name}
    directory = Path.home() / ".config/systemd/user"
    directory.mkdir(parents=True, exist_ok=True)
    unit = "ai11-local-release-" + project + ".service"
    command = " ".join('"' + str(a).replace('"', '\\"') + '"' for a in argv)
    path = directory / unit
    if path.exists():
        raise ReleaseError("Existing systemd unit would be overwritten")
    path.write_text("[Unit]\nDescription=AI11 local release observer\n[Service]\nExecStart=" + command +
                    "\nRestart=on-failure\nRestartSec=30\n[Install]\nWantedBy=default.target\n", encoding="utf-8")
    try:
        capture(["systemctl", "--user", "daemon-reload"])
        capture(["systemctl", "--user", "enable", "--now", unit])
    except BaseException:
        subprocess.run(["systemctl", "--user", "disable", "--now", unit], capture_output=True, check=False)
        path.unlink(missing_ok=True)
        subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True, check=False)
        raise
    return {"kind": "systemd-user", "name": unit, "path": str(path)}


def unregister_startup(startup):
    if startup["kind"] == "scheduled-task":
        capture(["schtasks", "/Delete", "/TN", startup["name"], "/F"])
    else:
        capture(["systemctl", "--user", "disable", "--now", startup["name"]])
        Path(startup["path"]).unlink()
        capture(["systemctl", "--user", "daemon-reload"])


def remove(queue):
    with lock(queue.parent / ".queue.lock"):
        data = read_json(queue)
        for value in data.get("hook_paths", []):
            path = Path(value)
            if not path.exists() or MARKER not in path.read_text(encoding="utf-8"):
                raise ReleaseError("Hook was changed by another tool; preserve and reconcile: " + value)
        startup = data.get("startup")
        if startup:
            unregister_startup(startup)
        for value in data.get("hook_paths", []):
            path = Path(value)
            path.unlink()
            previous = path.with_name(path.name + ".before-local-release")
            if previous.exists():
                previous.rename(path)
        data.update(enabled=False, hook_paths=[], startup=None)
        atomic_json(queue, data)
