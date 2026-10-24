"""Archive two obsolete, unreferenced stage-7 trial directories before removal.

The canonical stage-7 work tree and its inventory are never selected. Restoration:
python -m zipfile -e <archive.zip> scripts/bible_module/work
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

from .build_ohienko_1988 import PROJECT_ROOT, sha256_file

DIRECTORIES = (
    "ukrainian_stage_7_archive_pre_selected_20260808",
    "ukrainian_stage_7_preflight_selected",
)
WORK_ROOT = PROJECT_ROOT / "scripts/bible_module/work"


def selected_files(work_root: Path) -> tuple[list[Path], list[Path]]:
    root = work_root.resolve(strict=True)
    targets, files = [], []
    for name in DIRECTORIES:
        target = root / name
        if target.is_symlink() or target.resolve(strict=True).parent != root:
            raise ValueError(f"Archive target escapes the intended work tree: {target}")
        if not target.is_dir():
            raise ValueError(f"Archive target is not a directory: {target}")
        targets.append(target)
        for path in sorted(target.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Refusing an archive tree containing a symlink: {path}")
            if path.is_file():
                files.append(path)
    return targets, files


def archive_and_remove(work_root: Path, archive_path: Path, receipt_path: Path) -> dict:
    root = work_root.resolve(strict=True)
    targets, files = selected_files(root)
    destination = archive_path.resolve()
    receipt = receipt_path.resolve()
    if destination.is_relative_to(root) or receipt.is_relative_to(root):
        raise ValueError("The recoverable archive and receipt must be outside the work tree")
    if destination == receipt or destination.exists() or receipt.exists():
        raise FileExistsError("Archive and receipt must be new, distinct files")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".rev201-archive-", suffix=".zip", dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    entries = []
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=1, allowZip64=True) as archive:
            for source in files:
                relative = source.relative_to(root).as_posix()
                digest = hashlib.sha256()
                size = 0
                with source.open("rb") as input_file, archive.open(relative, "w", force_zip64=True) as output:
                    for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                entries.append({"path": relative, "bytes": size, "sha256": digest.hexdigest()})
        with zipfile.ZipFile(temporary) as archive:
            if archive.namelist() != [entry["path"] for entry in entries]:
                raise ValueError("Archive file roster differs")
            for entry in entries:
                digest = hashlib.sha256()
                with archive.open(entry["path"]) as member:
                    for chunk in iter(lambda: member.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != entry["sha256"]:
                    raise ValueError(f"Archive verification failed: {entry['path']}")
        # A changed or added input cancels deletion even after a valid archive.
        current_targets, current_files = selected_files(root)
        if current_files != files or current_targets != targets:
            raise ValueError("Source roster changed during archiving")
        for entry in entries:
            source = root / entry["path"]
            if source.stat().st_size != entry["bytes"] or sha256_file(source) != entry["sha256"]:
                raise ValueError(f"Source changed during archiving: {source}")
        os.replace(temporary, destination)
        result = {
            "status": "archive_verified_before_removal", "archive": str(destination),
            "archive_sha256": sha256_file(destination), "archive_bytes": destination.stat().st_size,
            "original_bytes": sum(entry["bytes"] for entry in entries),
            "files": entries, "removed_directories": [],
            "restore_command": f'python -m zipfile -e "{destination}" "{root}"',
        }
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for target in targets:
            # Recheck the absolute deletion boundary immediately before each rmtree.
            if target.is_symlink() or target.resolve(strict=True).parent != root:
                raise ValueError(f"Unsafe removal target: {target}")
            shutil.rmtree(target)
            result["removed_directories"].append(str(target))
            receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["status"] = "archived_and_removed"
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        if args.archive is None or args.receipt is None:
            parser.error("--apply requires --archive and --receipt")
        result = archive_and_remove(WORK_ROOT, args.archive, args.receipt)
        print(json.dumps({k: v for k, v in result.items() if k != "files"}, ensure_ascii=False))
    else:
        targets, files = selected_files(WORK_ROOT)
        print(json.dumps({"targets": [str(p) for p in targets], "files": len(files),
                          "bytes": sum(p.stat().st_size for p in files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
