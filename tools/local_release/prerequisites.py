"""Own the isolated emulator and headless browser driver used by release tests."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
from urllib.request import urlopen

from .core import ReleaseError, digest, hidden_flags
from .processes import JobStopped, terminate_tree


def port_free(port):
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def wait_ready(ctx, probe, process, label, seconds=240):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if (ctx.directory / "stop-request.json").exists():
            raise JobStopped(label + " startup stopped by owner")
        if process.poll() is not None:
            raise ReleaseError(label + " exited during startup; see prerequisite log")
        if probe():
            return
        time.sleep(1)
    raise ReleaseError(label + " did not become ready; see prerequisite log")


@contextmanager
def child(ctx, argv, label, env=None):
    log = ctx.directory / "logs" / ctx.host / (label + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as stream:
        process = subprocess.Popen([str(a) for a in argv], env=env or ctx.env,
            stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
            creationflags=hidden_flags(), start_new_session=os.name != "nt")
        try:
            yield process
        finally:
            terminate_tree(process)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@contextmanager
def android_device(ctx):
    """Never use a phone/global ADB server or terminate a borrowed emulator."""
    avd, serial = ctx.config.get("android_avd_name"), ctx.config.get("android_device", "")
    match = re.fullmatch(r"emulator-(\d+)", serial)
    port = ctx.config.get("adb_server_port")
    if not avd or not match or type(port) is not int or not 1024 <= port <= 65535 or port == 5037:
        raise ReleaseError("Configure an explicit isolated AVD, emulator serial and non-global adb_server_port")
    console = int(match[1])
    if not 5554 <= console <= 5682 or console % 2:
        raise ReleaseError("Isolated emulator requires an even console port from 5554 to 5682")
    adb = Path(ctx.config["android_sdk"]) / "platform-tools/adb.exe"
    previous = {name: ctx.env.get(name) for name in ("ANDROID_ADB_SERVER_PORT", "ADB_SERVER_SOCKET")}
    ctx.env.update(ANDROID_ADB_SERVER_PORT=str(port), ADB_SERVER_SOCKET=f"tcp:127.0.0.1:{port}")

    def identity():
        value = ctx.command([adb, "-P", str(port), "-s", serial, "emu", "avd", "name"])
        if avd not in value.splitlines():
            raise ReleaseError("Configured emulator serial belongs to another AVD; it was not changed")

    try:
        devices = ctx.command([adb, "-P", str(port), "devices"])
        if any(line.split()[:1] == [serial] for line in devices.splitlines()):
            identity()
            yield serial
            return
        if not port_free(console) or not port_free(console + 1):
            raise ReleaseError("Configured emulator ports are occupied; existing processes preserved")
        executable = Path(ctx.config["android_sdk"]) / "emulator/emulator.exe"
        argv = [executable, "-avd", avd, "-port", str(console), "-no-window", "-no-audio",
                "-no-snapshot-save", "-read-only", "-gpu", "swiftshader_indirect"]
        with child(ctx, argv, "android-emulator") as process:
            def ready():
                try:
                    return ctx.command([adb, "-P", str(port), "-s", serial, "shell", "getprop", "sys.boot_completed"]).strip() == "1"
                except ReleaseError:
                    return False
            wait_ready(ctx, ready, process, "Android emulator")
            identity()
            try:
                yield serial
            finally:
                # The serial and AVD were verified before use. Only our launch
                # is shut down; the borrowed-device branch never enters here.
                ctx.command([adb, "-P", str(port), "-s", serial, "emu", "kill"], cancellable=False)
    finally:
        for name, value in previous.items():
            if value is None:
                ctx.env.pop(name, None)
            else:
                ctx.env[name] = value


@contextmanager
def chrome_driver(ctx):
    executable, port = ctx.config.get("chromedriver_path"), ctx.config.get("chromedriver_port")
    if not executable:
        if not port:
            raise ReleaseError("Configure a matching ChromeDriver executable and chromedriver_port")
        yield  # Retain support for an explicitly managed external driver.
        return
    expected = ctx.config.get("chromedriver_sha256")
    if not expected or digest(Path(executable)) != expected:
        raise ReleaseError("Configured ChromeDriver digest differs from the approved executable")
    if type(port) is not int or not 1024 <= port <= 65535 or not port_free(port):
        raise ReleaseError("ChromeDriver requires a free dedicated port; existing browser sessions preserved")
    with child(ctx, [executable, "--port=" + str(port), "--allowed-ips=127.0.0.1"], "chrome-driver") as process:
        def ready():
            try:
                with urlopen(f"http://127.0.0.1:{port}/status", timeout=1) as response:
                    return json.load(response).get("value", {}).get("ready") is True
            except (OSError, ValueError):
                return False
        wait_ready(ctx, ready, process, "ChromeDriver", 30)
        yield
