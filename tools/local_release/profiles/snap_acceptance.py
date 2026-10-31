"""Install the exact local Snap, smoke it, and restore the previous revision/data.

The recovery journal stays host-local. No user snapshot is exported to GitHub.
"""

import os
import hashlib
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

from ..core import ReleaseError, atomic_json, digest, read_json
from ..processes import JobStopped, StopMonitor, terminate_tree

NAME = "revelation-x"
SMOKE_SHELL = '''set -eu
export XDG_CONFIG_HOME="$SNAP_USER_COMMON/.ai11-acceptance/config"
export XDG_DATA_HOME="$SNAP_USER_COMMON/.ai11-acceptance/data"
export XDG_CACHE_HOME="$SNAP_USER_COMMON/.ai11-acceptance/cache"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME" "$SNAP_USER_COMMON/.ai11-acceptance/Documents"
printf 'XDG_DOCUMENTS_DIR="%s/Documents"\\n' "$SNAP_USER_COMMON/.ai11-acceptance" > "$XDG_CONFIG_HOME/user-dirs.dirs"
exec "$SNAP/revelation"
'''


def data_paths(ctx):
    root = Path.home() / "snap" / NAME
    return root, root.with_name(".ai11-" + NAME + "-" + ctx.job["sha"])


def user_data_digest(root):
    """Compare owner data without exporting filenames or contents."""
    result = hashlib.sha256()
    if root.exists():
        for path in sorted(root.rglob("*")):
            result.update(path.relative_to(root).as_posix().encode())
            if path.is_symlink():
                result.update(b"link\0" + os.readlink(path).encode())
            elif path.is_file():
                result.update(b"file\0" + digest(path).encode())
            else:
                result.update(b"directory\0")
    return result.hexdigest()


def isolate_user_data(ctx, state):
    root, backup = data_paths(ctx)
    if root.is_symlink() or backup.exists() or backup.is_symlink():
        raise ReleaseError("Snap user-data backup path is already occupied or linked; preserved for inspection")
    if root.exists():
        if user_data_digest(root) != state["user_data_sha256"]:
            raise ReleaseError("Snap user data changed before isolation")
        # Same-parent rename preserves every byte, permissions and timestamps,
        # including paths the Snap snapshot configuration might exclude.
        root.rename(backup)


def restore_user_data(ctx, state):
    root, backup = data_paths(ctx)
    if root.is_symlink() or backup.is_symlink():
        raise ReleaseError("Snap user-data paths changed into symlinks; original backup retained")
    if state.get("user_data_existed"):
        if not backup.exists():
            if user_data_digest(root) != state["user_data_sha256"]:
                raise ReleaseError("Original Snap user-data backup is missing; journal retained")
            return
        if user_data_digest(backup) != state["user_data_sha256"]:
            raise ReleaseError("Original Snap user-data backup digest mismatch; retained")
    elif backup.exists():
        raise ReleaseError("Unexpected Snap user-data backup; it will not be removed")
    if root.exists():
        # Only this exact Snap data directory is replaced, after verifying its
        # original backup; never follow a symlink into another directory.
        if root.parent.resolve() != (Path.home() / "snap").resolve():
            raise ReleaseError("Snap user-data restoration escaped the expected directory")
        shutil.rmtree(root)
    if backup.exists():
        backup.rename(root)
    if state.get("user_data_existed") and user_data_digest(root) != state["user_data_sha256"]:
        raise ReleaseError("Snap user-data restoration digest mismatch")


def installed(ctx):
    text = ctx.command(["snap", "list", NAME], env={"LC_ALL": "C"}, success_codes=(0, 1),
                       cancellable=not getattr(ctx, "restoring_snap", False))
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == NAME and len(fields) >= 6:
            version, revision, tracking = fields[1:4]
            if not re.fullmatch(r"x?\d+", revision):
                raise ReleaseError("Cannot identify the installed Snap revision")
            path = Path("/var/lib/snapd/snaps") / f"{NAME}_{revision}.snap"
            return {"version": version, "revision": revision, "tracking": tracking, "sha256": digest(path)}
    if "no matching snaps installed" in text.lower():
        return None
    raise ReleaseError("Cannot determine whether Revelation Snap is installed; no changes made")


def authorize(ctx):
    if os.geteuid() == 0:
        raise ReleaseError("Run the Linux dispatcher as the desktop user, not root")
    try:
        ctx.command(["sudo", "-n", "true"], cancellable=False)
    except ReleaseError:
        if not sys.stdin.isatty():
            raise ReleaseError("Snap validation needs administrator authentication: run sudo -v in the Linux progress terminal and retry")
        print("Ubuntu needs administrator authentication for Snap install/restore. Enter your sudo password in this terminal; it is not logged.", flush=True)
        ctx.command(["sudo", "-v"], cancellable=False)


def privileged(ctx, *args):
    return ctx.command(["sudo", "-n", "snap", *args], env={"LC_ALL": "C"},
                       cancellable=False)


def restore(ctx, journal):
    state = read_json(journal)
    if state.get("name") != NAME or state.get("sha") != ctx.job["sha"]:
        raise ReleaseError("Snap restoration journal belongs to another job; preserved for inspection")
    if not re.fullmatch(r"[0-9a-f]{64}", state.get("package_sha256", "")) or (
            state.get("snapshot") is not None and (type(state["snapshot"]) is not int or state["snapshot"] <= 0)):
        raise ReleaseError("Snap restoration journal has invalid package/snapshot identifiers")
    for revision in (state.get("test_revision"), (state.get("before") or {}).get("revision")):
        if revision is not None and not re.fullmatch(r"x?\d+", str(revision)):
            raise ReleaseError("Snap restoration journal has an invalid revision")
    before, current = state["before"], installed(ctx)
    if before:
        if not current:
            raise ReleaseError("Original Snap disappeared; snapshot/journal retained for recovery")
        if current["sha256"] not in (before["sha256"], state["package_sha256"]):
            raise ReleaseError("Snap changed outside this test; recovery journal retained without replacing it")
        if current["revision"] != before["revision"]:
            privileged(ctx, "revert", NAME, "--revision=" + before["revision"])
        if installed(ctx) != before:
            raise ReleaseError("Original Snap revision/hash/tracking was not restored")
        snapshot = str(state["snapshot"]) if state.get("snapshot") else None
        if snapshot and state.get("installation_started", True):
            privileged(ctx, "restore", snapshot, NAME)
            privileged(ctx, "check-snapshot", snapshot, NAME)
        test_revision = state.get("test_revision")
        if test_revision and test_revision != before["revision"]:
            # Remove only the exact disabled revision created by this test.
            path = Path("/var/lib/snapd/snaps") / f"{NAME}_{test_revision}.snap"
            if path.exists():
                if digest(path) != state["package_sha256"]:
                    raise ReleaseError("Disabled test revision changed; it will not be removed")
                privileged(ctx, "remove", NAME, "--revision=" + test_revision)
        if "user_data_existed" in state:
            restore_user_data(ctx, state)
        if snapshot:
            state["snapshot"] = None
            atomic_json(journal, state)
            privileged(ctx, "forget", snapshot)
    elif current:
        if current["sha256"] != state["package_sha256"]:
            raise ReleaseError("An unrelated Snap appeared; it will not be removed")
        privileged(ctx, "remove", "--purge", NAME)
        if installed(ctx) is not None:
            raise ReleaseError("Temporary Snap installation was not removed")
        if "user_data_existed" in state:
            restore_user_data(ctx, state)
    elif "user_data_existed" in state:
        restore_user_data(ctx, state)
    journal.unlink()


def smoke(ctx):
    """Require actual Flutter startup and ten seconds alive, then close our tree."""
    log = ctx.directory / "logs/linux/snap-smoke.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = ["snap", "run", "--shell", NAME, "-c", SMOKE_SHELL]
    started = threading.Event()
    failed = threading.Event()
    env = ctx.env.copy()
    env["LC_ALL"] = "C.UTF-8"
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(command, cwd=ctx.workspace, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            start_new_session=True)
        def consume():
            for line in process.stdout:
                stream.write(ctx.redact(line))
                stream.flush()
                if "Started on TargetPlatform.linux" in line:
                    started.set()
                if re.search(r"FATAL|failed to start crashpad|sentry_init.*failed|posix_spawn.*[Dd]enied", line):
                    failed.set()
        reader = threading.Thread(target=consume, daemon=True)
        reader.start()
        try:
            with StopMonitor(process, ctx.directory / "stop-request.json") as monitor:
                deadline, observed = time.monotonic() + 45, None
                while time.monotonic() < deadline:
                    if monitor.stopped:
                        raise JobStopped("Snap smoke stopped by owner")
                    if process.poll() is not None or failed.is_set():
                        raise ReleaseError("Installed Snap failed during startup; see snap-smoke.log")
                    if started.is_set():
                        observed = observed or time.monotonic()
                        if time.monotonic() - observed >= 10:
                            return {"startup_marker": True, "alive_seconds_after_startup": 10}
                    time.sleep(.1)
                raise ReleaseError("Installed Snap did not report Flutter startup within 45 seconds; see snap-smoke.log")
        finally:
            terminate_tree(process)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            reader.join(timeout=5)
            process.stdout.close()


def verify(ctx):
    from ..native_fixture import application_running
    if application_running():
        raise ReleaseError("Revelation is already open; Snap validation waits without changing owner data")
    if not (ctx.env.get("DISPLAY") or ctx.env.get("WAYLAND_DISPLAY")):
        raise ReleaseError("Snap smoke requires the owner's native graphical Linux session")
    authorize(ctx)
    folder = ctx.root / "w" / ctx.job["sha"][:12] / "snap-acceptance"
    folder.mkdir(parents=True, exist_ok=True)
    journal = folder / "restore.json"
    # Restoration commands must finish even when cancellation was requested.
    def recover():
        ctx.restoring_snap = True
        try:
            restore(ctx, journal)
        finally:
            ctx.restoring_snap = False
    if journal.exists():
        recover()
    package = ctx.output / next(n for n in ctx.job["artifacts"] if n.endswith(".snap"))
    expected = read_json(ctx.directory / "results/linux-snap-package.json")["sha256"]
    if digest(package) != expected:
        raise ReleaseError("Snap bytes changed since package inspection")
    before = installed(ctx)
    user_data, backup = data_paths(ctx)
    if user_data.is_symlink() or backup.exists() or backup.is_symlink():
        raise ReleaseError("Snap user-data backup path is occupied or linked; no installation changes made")
    state = {"schema": 1, "name": NAME, "sha": ctx.job["sha"], "before": before,
             "package_sha256": expected, "snapshot": None, "test_revision": None,
             "user_data_sha256": user_data_digest(user_data), "user_data_existed": user_data.exists(),
             "installation_started": False}
    atomic_json(journal, state)
    try:
        if before:
            output = privileged(ctx, "save", NAME)
            match = re.search(r"^\s*(\d+)\s+" + NAME + r"\s", output, re.M)
            if not match:
                raise ReleaseError("Cannot identify the Snap data snapshot; installation was not changed")
            state["snapshot"] = int(match[1])
            atomic_json(journal, state)
            privileged(ctx, "check-snapshot", str(state["snapshot"]), NAME)
        isolate_user_data(ctx, state)
        if not before or before["sha256"] != expected:
            state["installation_started"] = True
            atomic_json(journal, state)
            privileged(ctx, "install", "--dangerous", str(package))
        current = installed(ctx)
        if not current or current["sha256"] != expected or current["version"] != f"{ctx.job['version']}.{ctx.job['build']}":
            raise ReleaseError("Installed Snap differs from the inspected release package")
        state["test_revision"] = current["revision"]
        atomic_json(journal, state)
        proof = smoke(ctx)
    finally:
        recover()
    proof.update({"schema": 1, "sha": ctx.job["sha"], "version": ctx.job["version"], "build": ctx.job["build"],
        "package_sha256": expected, "installation": "passed", "restored": True,
        "previous_revision": before["revision"] if before else None,
        "isolated_xdg_directories": True})
    atomic_json(ctx.directory / "results/linux-packages.json", proof)


def acceptance(ctx):
    """An explicitly pinned custom verifier remains supported; default is built in."""
    script, expected = ctx.config.get("snap_verify_script"), ctx.config.get("snap_verify_script_sha256")
    if script or expected:
        if not script or not expected or digest(Path(script)) != expected:
            raise ReleaseError("Configured custom Snap verifier digest mismatch")
        package = ctx.output / next(n for n in ctx.job["artifacts"] if n.endswith(".snap"))
        ctx.command(["bash", str(Path(script).resolve())], env={"LOCAL_RELEASE_SNAP_OUTPUT": str(package)})
        atomic_json(ctx.directory / "results/linux-packages.json", {"snap": "install/smoke/restore passed", "verify_script_sha256": expected})
    else:
        verify(ctx)
