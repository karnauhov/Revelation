"""Cancellation applies only to a child process tree owned by this job."""

import os
from pathlib import Path
import signal
import subprocess
import threading

from .core import ReleaseError, hidden_flags


class JobStopped(ReleaseError):
    pass


def terminate_tree(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False, creationflags=hidden_flags())
    else:
        try:
            if getattr(process, "owned_process_group", True):
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except ProcessLookupError:
            pass


class StopMonitor:
    def __init__(self, process, request: Path, *, enabled=True):
        self.process, self.request = process, request
        self.enabled = enabled
        self.finished = threading.Event()
        self.stopped = False
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def watch(self):
        while not self.finished.wait(0.25):
            if self.enabled and self.request.exists():
                self.stopped = True
                terminate_tree(self.process)
                return

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.finished.set()
        self.thread.join(timeout=5)
