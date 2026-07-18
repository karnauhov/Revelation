from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from .sources import DEFAULT_SOURCE_CACHE_DIR, DEFAULT_SOURCE_LOCK_PATH, SOURCE_SPECS

USER_AGENT = "Revelation Bible module source fetcher"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _previous_sources_by_id(
    manifest: Mapping[str, object] | None,
) -> dict[str, Mapping[str, object]]:
    if not manifest:
        return {}
    entries = manifest.get("sources")
    if not isinstance(entries, list):
        return {}
    by_id: dict[str, Mapping[str, object]] = {}
    for entry in entries:
        if isinstance(entry, Mapping) and isinstance(entry.get("source_id"), str):
            by_id[str(entry["source_id"])] = entry
    return by_id


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _download_to_path(url: str, target_path: Path) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response:
        with tempfile.NamedTemporaryFile(
            "wb",
            delete=False,
            dir=str(target_path.parent),
            prefix=f".{target_path.name}.",
            suffix=".tmp",
        ) as temp_file:
            temp_path = Path(temp_file.name)
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)
    temp_path.replace(target_path)


def _manifest_local_path(target_path: Path, manifest_path: Path) -> str:
    try:
        return target_path.resolve().relative_to(manifest_path.parent.resolve()).as_posix()
    except ValueError:
        return target_path.as_posix()


def _resolve_manifest_local_path(local_path_value: str, manifest_path: Path) -> Path:
    local_path = Path(local_path_value)
    if local_path.is_absolute():
        return local_path
    return manifest_path.parent / local_path


def build_source_manifest(
    *,
    cache_dir: Path = DEFAULT_SOURCE_CACHE_DIR,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    force: bool = False,
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    previous_manifest = load_manifest(manifest_path)
    previous_entries = _previous_sources_by_id(previous_manifest)
    generated_at = generated_at_utc or _utc_now_iso()
    source_entries: list[dict[str, object]] = []
    manifest_changed = False

    for spec in SOURCE_SPECS:
        target_path = cache_dir / spec.filename
        downloaded = force or not target_path.exists()
        if downloaded:
            _download_to_path(spec.source_url, target_path)

        checksum = sha256_file(target_path)
        previous_entry = previous_entries.get(spec.source_id, {})
        previous_checksum = previous_entry.get("sha256")
        manifest_changed = manifest_changed or downloaded or previous_checksum != checksum
        previous_downloaded_at = previous_entry.get("downloaded_at_utc")
        downloaded_at = (
            previous_downloaded_at
            if isinstance(previous_downloaded_at, str)
            and previous_checksum == checksum
            and not downloaded
            else generated_at
        )

        source_entries.append(
            {
                "source_id": spec.source_id,
                "title": spec.title,
                "version": spec.version,
                "source_commit": spec.source_commit,
                "downloaded_at_utc": downloaded_at,
                "source_url": spec.source_url,
                "source_page_url": spec.source_page_url,
                "license": spec.license_name,
                "license_url": spec.license_url,
                "local_path": _manifest_local_path(target_path, manifest_path),
                "sha256": checksum,
                "bytes": target_path.stat().st_size,
                "notes": spec.notes,
            }
        )

    if (
        not generated_at_utc
        and not manifest_changed
        and isinstance(previous_manifest, Mapping)
        and isinstance(previous_manifest.get("generated_at_utc"), str)
    ):
        generated_at = str(previous_manifest["generated_at_utc"])

    return {
        "schema_version": 1,
        "generated_at_utc": generated_at,
        "source_cache_dir": _manifest_local_path(cache_dir, manifest_path),
        "policy": {
            "canon": "canonical_protestant_66_only",
            "strong_format": "no_leading_zeroes",
            "rvr1960_requires_explicit_owner_permission": True,
            "crosswire_lxx_owner_permission_confirmed": True,
        },
        "sources": source_entries,
    }


def write_source_manifest(
    *,
    cache_dir: Path = DEFAULT_SOURCE_CACHE_DIR,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
    force: bool = False,
) -> dict[str, object]:
    manifest = build_source_manifest(
        cache_dir=cache_dir,
        manifest_path=manifest_path,
        force=force,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def verify_source_manifest(
    *,
    manifest_path: Path = DEFAULT_SOURCE_LOCK_PATH,
) -> list[str]:
    manifest = load_manifest(manifest_path)
    if manifest is None:
        return [f"Missing source manifest: {manifest_path}"]
    entries = manifest.get("sources")
    if not isinstance(entries, list):
        return [f"Invalid source manifest sources list: {manifest_path}"]

    errors: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            errors.append("Invalid source manifest entry")
            continue
        source_id = str(entry.get("source_id") or "<unknown>")
        local_path_value = entry.get("local_path")
        checksum = entry.get("sha256")
        if not isinstance(local_path_value, str):
            errors.append(f"{source_id}: missing local_path")
            continue
        if not isinstance(checksum, str):
            errors.append(f"{source_id}: missing sha256")
            continue
        local_path = _resolve_manifest_local_path(local_path_value, manifest_path)
        if not local_path.exists():
            errors.append(f"{source_id}: cached source is missing: {local_path}")
            continue
        actual = sha256_file(local_path)
        if actual != checksum:
            errors.append(f"{source_id}: checksum mismatch: expected {checksum}, got {actual}")
    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and lock Bible module source data for repeatable imports.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_SOURCE_CACHE_DIR,
        help="Directory where downloaded source files are cached.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_LOCK_PATH,
        help="Path to the generated source manifest lock file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download sources even when cached files already exist.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify cached source checksums without downloading.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.check:
        errors = verify_source_manifest(manifest_path=args.manifest)
        if errors:
            for error in errors:
                print(error)
            return 1
        print(f"Verified source manifest: {args.manifest}")
        return 0

    manifest = write_source_manifest(
        cache_dir=args.cache_dir,
        manifest_path=args.manifest,
        force=args.force,
    )
    print(
        f"Locked {len(manifest['sources'])} Bible source files in {args.manifest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
