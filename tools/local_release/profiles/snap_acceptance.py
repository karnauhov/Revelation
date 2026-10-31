"""Install the exact local Snap, smoke it, and restore the previous revision/data.

The recovery journal stays host-local. No user snapshot is exported to GitHub.
"""

import os
import hashlib
from contextlib import contextmanager
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

from ..core import ReleaseError, atomic_json, digest, hidden_flags, read_json
from ..processes import JobStopped, StopMonitor, terminate_tree

NAME = "revelation-x"
SMOKE_ALIVE_SECONDS = 10
SMOKE_TIMEOUT_SECONDS = 45
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


def installed_revision_digest(ctx, revision):
    if not re.fullmatch(r"x?\d+", str(revision)):
        raise ReleaseError("Cannot hash an invalid installed Snap revision")
    path = f"/var/lib/snapd/snaps/{NAME}_{revision}.snap"
    # snapd may keep installed packages root-readable only. Authentication does
    # not elevate this Python process; ask sudo for the digest, never chmod/read
    # the protected package into the unprivileged coordinator.
    output = ctx.command(["sudo", "-n", "sha256sum", "--", path],
        env={"LC_ALL": "C", "LANGUAGE": "C"}, cancellable=False, new_session=False)
    match = re.fullmatch(r"([0-9a-f]{64}) [ *]" + re.escape(path) + r"\s*", output)
    if not match:
        raise ReleaseError("Installed Snap checksum output is invalid; package state preserved")
    return match[1]


def installed(ctx):
    text = ctx.command(["snap", "list", NAME], env={"LC_ALL": "C", "LANGUAGE": "C"}, success_codes=(0, 1),
                       cancellable=not getattr(ctx, "restoring_snap", False))
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] == NAME and len(fields) >= 6:
            version, revision, tracking = fields[1:4]
            if not re.fullmatch(r"x?\d+", revision):
                raise ReleaseError("Cannot identify the installed Snap revision")
            return {"version": version, "revision": revision, "tracking": tracking,
                    "sha256": installed_revision_digest(ctx, revision)}
    if "no matching snaps installed" in text.lower():
        return None
    raise ReleaseError("Cannot determine whether Revelation Snap is installed; no changes made")


def authorize(ctx):
    if os.geteuid() == 0:
        raise ReleaseError("Run the Linux dispatcher as the desktop user, not root")
    try:
        ctx.command(["sudo", "-n", "true"], cancellable=False, new_session=False)
    except ReleaseError:
        if not sys.stdin.isatty():
            raise ReleaseError("Snap validation needs administrator authentication: run sudo -v in the Linux progress terminal and retry")
        print("Ubuntu needs administrator authentication for Snap install/restore. Enter your sudo password in this terminal; it is not logged.", flush=True)
        # Keep the desktop terminal as controlling TTY. Context commands normally
        # create a new session, which would make /dev/tty and sudo timestamps fail.
        result = subprocess.run(["sudo", "-v"], env=ctx.env, check=False)
        if result.returncode:
            raise ReleaseError("Ubuntu administrator authentication failed; Snap installation was not changed")
        ctx.command(["sudo", "-n", "true"], cancellable=False, new_session=False)
    print("Administrator authentication accepted. Checking installed Snap package access.", flush=True)


@contextmanager
def sudo_lease(ctx):
    authorize(ctx)
    finished = threading.Event()
    def renew():
        while not finished.wait(60):
            try:
                subprocess.run(["sudo", "-n", "-v"], env=ctx.env, stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                return
    thread = threading.Thread(target=renew, daemon=True)
    thread.start()
    try:
        yield
    finally:
        finished.set()
        thread.join(timeout=16)


def privileged(ctx, *args):
    return ctx.command(["sudo", "-n", "snap", *args], env={"LC_ALL": "C", "LANGUAGE": "C"},
                       cancellable=False, new_session=False)


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
                if installed_revision_digest(ctx, test_revision) != state["package_sha256"]:
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


class EarlySnapClose(ReleaseError):
    """A normal close before the observation period is an incomplete check."""


def smoke_once(ctx, attempt):
    """Keep the ten-second gate and record exit details before our own cleanup."""
    log = ctx.directory / "logs/linux/snap-smoke.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    command = ["snap", "run", "--shell", NAME, "-c", SMOKE_SHELL]
    started = threading.Event()
    failed = threading.Event()
    env = ctx.env.copy()
    env["LC_ALL"] = "C.UTF-8"
    print("Проверка готового Snap: не закрывайте окно Revelation. После запуска проверка наблюдает "
          "его 10 секунд, затем сама закроет окно и восстановит прежнюю установку. Пересборка не выполняется.", flush=True)
    launched = time.monotonic()
    with log.open("a", encoding="utf-8") as stream:
        stream.write(f"\nSnap smoke attempt {attempt['attempt']}\n")
        stream.flush()
        process = subprocess.Popen(command, cwd=ctx.workspace, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            start_new_session=True, creationflags=hidden_flags())
        def consume():
            for line in process.stdout:
                stream.write(ctx.redact(line))
                stream.flush()
                if "Started on TargetPlatform.linux" in line:
                    if not started.is_set():
                        attempt["startup_at_seconds"] = time.monotonic() - launched
                    started.set()
                if re.search(r"FATAL|failed to start crashpad|sentry_init.*failed|posix_spawn.*[Dd]enied", line):
                    failed.set()
        reader = threading.Thread(target=consume, daemon=True)
        reader.start()
        try:
            with StopMonitor(process, ctx.directory / "stop-request.json") as monitor:
                deadline, last_remaining = launched + SMOKE_TIMEOUT_SECONDS, None
                while time.monotonic() < deadline:
                    if monitor.stopped:
                        raise JobStopped("Snap smoke stopped by owner")
                    code = process.poll()
                    if code is not None:
                        # Drain final output before classifying an exit; a last
                        # fatal line must never turn into a retryable clean close.
                        reader.join(timeout=1)
                    if failed.is_set():
                        raise ReleaseError(f"Installed Snap reported a fatal startup error (exit={code}); see snap-smoke.log")
                    if code is not None:
                        if code == 0 and started.is_set():
                            raise EarlySnapClose("Snap window closed normally before the ten-second check finished")
                        raise ReleaseError(f"Installed Snap exited before acceptance (exit={code}, startup={started.is_set()}); see snap-smoke.log")
                    if started.is_set():
                        elapsed = time.monotonic() - launched - attempt["startup_at_seconds"]
                        if elapsed >= SMOKE_ALIVE_SECONDS:
                            return {"startup_marker": True, "alive_seconds_after_startup": SMOKE_ALIVE_SECONDS}
                        remaining = int(SMOKE_ALIVE_SECONDS - elapsed) + 1
                        if remaining != last_remaining:
                            print(f"Snap запущен. До автоматического закрытия: {remaining} с. Не закрывайте окно.", flush=True)
                            last_remaining = remaining
                    time.sleep(.1)
                raise ReleaseError("Installed Snap did not report Flutter startup within 45 seconds; see snap-smoke.log")
        finally:
            attempt.update(startup_marker=started.is_set(), fatal_output=failed.is_set(),
                exit_code_before_cleanup=process.poll(), elapsed_seconds=round(time.monotonic() - launched, 3))
            stream.write("Smoke observation: " + str(attempt) + "\n")
            stream.flush()
            terminate_tree(process)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            reader.join(timeout=5)
            process.stdout.close()


def smoke(ctx):
    """Retry one clean early close in place, without reinstalling or rebuilding."""
    report = {"schema": 1, "sha": ctx.job["sha"], "required_alive_seconds": SMOKE_ALIVE_SECONDS, "attempts": []}
    target = ctx.directory / "results/linux-snap-smoke.json"
    for number in (1, 2):
        attempt = {"attempt": number}
        report["attempts"].append(attempt)
        try:
            proof = smoke_once(ctx, attempt)
        except EarlySnapClose as error:
            attempt.update(status="closed_early", error=str(error))
            report["status"] = "incomplete"
            atomic_json(target, report)
            if number == 1:
                print("Окно Snap закрыто до окончания проверки. Повторяю только запуск один раз. "
                      "Не закрывайте окно - оно закроется автоматически. Пакеты и сборка сохраняются.", flush=True)
                continue
            raise ReleaseError("Snap window closed normally twice before the ten-second check finished. "
                               "Keep it open until automatic closure; built packages are preserved.") from error
        except BaseException as error:
            attempt.update(status="stopped" if isinstance(error, JobStopped) else "failed", error=str(error))
            report["status"] = attempt["status"]
            atomic_json(target, report)
            raise
        attempt["status"] = report["status"] = "passed"
        atomic_json(target, report)
        print("Проверка запуска Snap пройдена. Окно закрыто автоматически; восстанавливаю прежнюю установку.", flush=True)
        return {**proof, "smoke_attempts": number}


def verify(ctx):
    from ..native_fixture import application_running
    if application_running():
        raise ReleaseError("Revelation is already open; Snap validation waits without changing owner data")
    if not (ctx.env.get("DISPLAY") or ctx.env.get("WAYLAND_DISPLAY")):
        raise ReleaseError("Snap smoke requires the owner's native graphical Linux session")
    with sudo_lease(ctx):
        verify_authorized(ctx)


def verify_authorized(ctx):
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
