"""Temporary installed-module fixtures with verified restoration on native hosts."""

from contextlib import contextmanager
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import csv

from .core import ReleaseError, atomic_json, capture, digest, read_json, hidden_flags

MODULES = ("bible_ohienko_1988.sqlite", "bible_kjv.sqlite", "bible_lxx_tr.sqlite")


def documents_directory():
    if os.name == "nt":
        buffer = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buffer):
            raise ReleaseError("Windows Documents directory is unavailable")
        return Path(buffer.value)
    return Path(capture(["xdg-user-dir", "DOCUMENTS"]))


def application_running():
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq revelation.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, errors="replace", creationflags=hidden_flags())
        return any(row and row[0].lower() == "revelation.exe" for row in csv.reader(result.stdout.splitlines()))
    return subprocess.run(["pgrep", "-x", "revelation"], capture_output=True).returncode == 0


def restore(journal: Path, backup: Path, allowed_targets):
    state = read_json(journal)
    allowed = {str(path.resolve()): index for index, path in enumerate(allowed_targets)}
    for record in state["files"]:
        if record["target"] not in allowed or record["backup"] != f"original-{allowed[record['target']]}.bin" or not isinstance(record["existed"], bool):
            raise ReleaseError("Native fixture journal escaped its expected files; preserved for inspection")
    for record in state["files"]:
        target = Path(record["target"])
        source = backup / record["backup"]
        if record["existed"]:
            if not source.is_file() or digest(source) != record["sha256"]:
                raise ReleaseError("Native fixture backup digest mismatch; original backup preserved")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if digest(target) != record["sha256"]:
                raise ReleaseError("Native fixture restore digest mismatch")
        else:
            target.unlink(missing_ok=True)
    for record in state["files"]:
        (backup / record["backup"]).unlink(missing_ok=True)
    journal.unlink()
    backup.rmdir()


@contextmanager
def installed_modules(workspace: Path, backup: Path, *, documents=None, preferences=None, running_probe=application_running):
    """Restore the exact original bytes/timestamps even after a failed test."""
    if running_probe():
        raise ReleaseError("Revelation is already open; native fixture tests wait without changing owner data")
    journal = backup / "restore.json"
    folder = (documents or documents_directory()) / "revelation" / "db"
    targets = [(workspace / "web/db" / name, folder / name) for name in MODULES]
    if preferences is None and os.name == "nt":
        preferences = Path(os.environ["APPDATA"]) / "AI11/revelation/shared_preferences.json"
    if preferences is not None:
        targets.append((None, preferences))
    allowed_targets = [target for source, target in targets]
    if journal.exists():
        restore(journal, backup, allowed_targets)
    elif backup.exists() and any(backup.iterdir()):
        raise ReleaseError("Unrecognized native fixture backup; inspect before overwriting it")
    backup.mkdir(parents=True, exist_ok=True)
    state = {"schema": 1, "files": []}
    atomic_json(journal, state)
    unchanged = set()
    for index, (source, target) in enumerate(targets):
        if source is not None and source.is_file() and target.is_file() and digest(source) == digest(target):
            unchanged.add(target)
        record = {"target": str(target.resolve()), "backup": f"original-{index}.bin", "existed": target.exists()}
        if target.exists():
            saved = backup / record["backup"]
            try:
                shutil.copy2(target, saved)
                record["sha256"] = digest(target)
                if digest(saved) != record["sha256"]:
                    raise ReleaseError("Native fixture backup copy failed")
            except BaseException:
                saved.unlink(missing_ok=True)
                raise
        state["files"].append(record)
        atomic_json(journal, state)
    atomic_json(journal, state)
    try:
        for source, target in targets:
            if source is not None and target not in unchanged:
                if not source.is_file():
                    raise ReleaseError("Committed integration module is missing: " + source.name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                if digest(source) != digest(target):
                    raise ReleaseError("Native integration fixture copy failed")
        yield {"unchanged_modules": [path.name for path in unchanged],
               "protected_originals": [{"name": Path(r["target"]).name, "existed": r["existed"], "sha256": r.get("sha256")} for r in state["files"]]}
    finally:
        if running_probe():
            raise ReleaseError("Revelation is still open; original state backup retained for safe restoration")
        restore(journal, backup, allowed_targets)
