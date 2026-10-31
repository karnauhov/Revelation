"""Run the owner's unchanged Snap script; send q to its debug Flutter session."""

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import time

from .core import ReleaseError, atomic_json, digest, git, read_json


class QuitGate:
    def __init__(self, delay=5):
        self.delay = delay
        self.buffer = ""
        self.startup = None
        self.interactive = False
        self.sent = False

    def observe(self, text, now):
        self.buffer = (self.buffer + text)[-8192:]
        if self.startup is None and "Started on TargetPlatform.linux" in self.buffer:
            self.startup = now
        if "Flutter run key commands." in self.buffer:
            self.interactive = True

    def ready(self, now):
        if not self.sent and self.interactive and self.startup is not None and now - self.startup >= self.delay:
            self.sent = True
            return True
        return False


def flutter_debug(argv, *, timeout=900, evidence_path=None):
    if sys.platform != "linux":
        raise ReleaseError("The interactive Flutter adapter requires native Linux")
    import errno
    import pty
    import select
    import signal
    stopped = False
    def stop(*args):
        nonlocal stopped
        stopped = True
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGINT)}
    pid, master = pty.fork()
    if pid == 0:
        # pty.fork supplies a controlling terminal and a new owned session.
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.execv(argv[0], argv)
    gate, deadline, quit_deadline, status = QuitGate(), time.monotonic() + timeout, None, None
    try:
        while not stopped:
            now = time.monotonic()
            if now > (quit_deadline or deadline):
                raise ReleaseError("Timed out waiting for the original Flutter debug run to finish")
            readable, _, _ = select.select([master], [], [], .1)
            if readable:
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno != errno.EIO:
                        raise
                    chunk = b""
                if chunk:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                    gate.observe(chunk.decode("utf-8", errors="replace"), now)
            if gate.ready(now):
                print("\nLocal release: sending q to the original Flutter debug session after startup.", flush=True)
                os.write(master, b"q")
                quit_deadline = now + 60
            exited, value = os.waitpid(pid, os.WNOHANG)
            if exited:
                status = value
                return os.waitstatus_to_exitcode(value)
        raise ReleaseError("Original Flutter debug run stopped by owner")
    finally:
        if status is None:
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            until = time.monotonic() + 5
            while time.monotonic() < until:
                exited, value = os.waitpid(pid, os.WNOHANG)
                if exited:
                    break
                time.sleep(.1)
            else:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                os.waitpid(pid, 0)
        os.close(master)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        if evidence_path:
            atomic_json(evidence_path, {"exit_code": os.waitstatus_to_exitcode(status) if status is not None else None,
                "automatic_q": gate.sent, "startup_observed": gate.startup is not None})


def run(ctx, snapshot):
    script = snapshot / "snapcraft_build.sh"
    if snapshot.is_symlink() or not snapshot.resolve().is_relative_to(ctx.root.resolve()):
        raise ReleaseError("Original Snap script must run inside the isolated release checkout")
    if git(snapshot, "hash-object", str(script)) != git(snapshot, "rev-parse", ctx.job["sha"] + ":snapcraft_build.sh"):
        raise ReleaseError("Snap build script differs from the owner's committed source")
    flutter = shutil.which("flutter", path=ctx.env.get("PATH"))
    if not flutter:
        raise ReleaseError("The pinned Flutter SDK is unavailable")
    shim = ctx.root / "w" / ctx.job["sha"][:12] / "snap-cli"
    shim.mkdir(parents=True, exist_ok=True)
    wrapper = shim / "flutter"
    wrapper.write_text("#!/usr/bin/env bash\nexec " + shlex.join([
        sys.executable, "-m", "local_release.snap_script", "--flutter", flutter,
        "--state-dir", str(shim / "debug-state"), "--"]) + ' "$@"\n', encoding="utf-8")
    wrapper.chmod(0o755)
    debug_result = shim / "debug-state/result.json"
    debug_result.unlink(missing_ok=True)
    ctx.command(["bash", str(script)], cwd=snapshot, env={
        "PATH": str(shim) + os.pathsep + ctx.env.get("PATH", ""),
        "PYTHONPATH": str(Path(__file__).resolve().parent.parent) + os.pathsep + ctx.env.get("PYTHONPATH", "")})
    if not debug_result.is_file() or read_json(debug_result).get("exit_code") != 0:
        raise ReleaseError("The original Snap script did not finish its Flutter debug step successfully")
    atomic_json(ctx.directory / "results/linux-snap-script.json", {
        "source_sha": ctx.job["sha"], "script_git_blob": git(snapshot, "hash-object", str(script)),
        "script_sha256": digest(script), "original_script_executed": True,
        "debug_run": read_json(debug_result)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flutter", required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    values = args.args[1:] if args.args[:1] == ["--"] else args.args
    argv = [args.flutter, *values]
    if values[:1] == ["run"] and "--debug" in values:
        for variable, name in (("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data"), ("XDG_CACHE_HOME", "cache")):
            directory = args.state_dir / name
            directory.mkdir(parents=True, exist_ok=True)
            os.environ[variable] = str(directory)
        documents = args.state_dir / "Documents"
        documents.mkdir(parents=True, exist_ok=True)
        (args.state_dir / "config/user-dirs.dirs").write_text(
            "XDG_DOCUMENTS_DIR=" + json.dumps(str(documents), ensure_ascii=False) + "\n", encoding="utf-8")
        return flutter_debug(argv, evidence_path=args.state_dir / "result.json")
    os.execv(args.flutter, argv)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ReleaseError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
