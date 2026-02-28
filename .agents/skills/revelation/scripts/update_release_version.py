#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update Revelation release/version fields across project files.",
    )
    parser.add_argument(
        "--repo-root",
        help="Path to repository root. Defaults to auto-detected root.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    for inc_cmd in ("inc-build", "bump-build", "increase-build"):
        inc_parser = subparsers.add_parser(
            inc_cmd,
            help="Increment build number.",
        )
        inc_parser.add_argument(
        "--step",
        type=int,
        default=1,
        help="Increment step for build number (default: 1).",
        )

    set_parser = subparsers.add_parser(
        "set-version",
        help="Set semantic version (X.Y.Z).",
    )
    set_parser.add_argument("version", help="Semantic version in X.Y.Z format.")
    set_parser.add_argument(
        "--build",
        type=int,
        help="Optional build number override. If omitted, current build is kept.",
    )

    return parser.parse_args()


def detect_repo_root(args_repo_root: str | None) -> Path:
    if args_repo_root:
        root = Path(args_repo_root).resolve()
    else:
        root = Path(__file__).resolve().parents[4]
    if not (root / "pubspec.yaml").exists():
        raise SystemExit(f"Could not find pubspec.yaml in repo root: {root}")
    return root


def replace_once(text: str, pattern: str, replacement: str, file_path: Path) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Pattern not found in {file_path}: {pattern}")
    return updated


def parse_pubspec_version(pubspec_text: str) -> tuple[str, int]:
    match = re.search(
        r"^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$",
        pubspec_text,
        flags=re.MULTILINE,
    )
    if not match:
        raise SystemExit("Could not parse version from pubspec.yaml")
    return match.group(1), int(match.group(2))


def parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if not match:
        raise SystemExit(f"Wrong semantic version format: {version}. Expected X.Y.Z")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def compose_msix_version(semantic_version: str, build: int) -> str:
    major, minor, patch = parse_semver(semantic_version)
    third_segment = patch + build
    return f"{major}.{minor}.{third_segment}.0"


def update_files(repo_root: Path, semantic_version: str, build: int) -> None:
    if build < 0:
        raise SystemExit("Build number must be >= 0")

    pubspec_path = repo_root / "pubspec.yaml"
    setup_path = repo_root / "setup.iss"
    snapcraft_path = repo_root / "snap" / "snapcraft.yaml"
    desktop_path = repo_root / "snap" / "gui" / "revelation-x.desktop"

    for path in [pubspec_path, setup_path, snapcraft_path, desktop_path]:
        if not path.exists():
            raise SystemExit(f"File not found: {path}")

    msix_version = compose_msix_version(semantic_version, build)
    dotted = f"{semantic_version}.{build}"

    pubspec_text = pubspec_path.read_text(encoding="utf-8")
    pubspec_text = replace_once(
        pubspec_text,
        r"^version:\s*\d+\.\d+\.\d+\+\d+\s*$",
        f"version: {semantic_version}+{build}",
        pubspec_path,
    )
    pubspec_text = replace_once(
        pubspec_text,
        r"^(\s*msix_version:\s*)\d+\.\d+\.\d+\.\d+\s*$",
        rf"\g<1>{msix_version}",
        pubspec_path,
    )

    setup_text = setup_path.read_text(encoding="utf-8")
    setup_text = replace_once(
        setup_text,
        r'^#define MyAppVersion "\d+\.\d+\.\d+"\s*$',
        f'#define MyAppVersion "{semantic_version}"',
        setup_path,
    )
    setup_text = replace_once(
        setup_text,
        r'^#define MyAppBuild "\d+"\s*$',
        f'#define MyAppBuild "{build}"',
        setup_path,
    )

    snapcraft_text = snapcraft_path.read_text(encoding="utf-8")
    snapcraft_text = replace_once(
        snapcraft_text,
        r"^version:\s*'\d+\.\d+\.\d+\.\d+'\s*$",
        f"version: '{dotted}'",
        snapcraft_path,
    )

    desktop_text = desktop_path.read_text(encoding="utf-8")
    desktop_text = replace_once(
        desktop_text,
        r"^Version=\d+\.\d+\.\d+\.\d+\s*$",
        f"Version={dotted}",
        desktop_path,
    )

    pubspec_path.write_text(pubspec_text, encoding="utf-8")
    setup_path.write_text(setup_text, encoding="utf-8")
    snapcraft_path.write_text(snapcraft_text, encoding="utf-8")
    desktop_path.write_text(desktop_text, encoding="utf-8")

    print("Updated versions:")
    print(f"  semantic version: {semantic_version}")
    print(f"  build: {build}")
    print(f"  pubspec version: {semantic_version}+{build}")
    print(f"  msix_version: {msix_version}")
    print(f"  snap/desktop version: {dotted}")


def main() -> None:
    args = parse_args()
    repo_root = detect_repo_root(args.repo_root)

    pubspec_text = (repo_root / "pubspec.yaml").read_text(encoding="utf-8")
    current_version, current_build = parse_pubspec_version(pubspec_text)

    if args.command in ("inc-build", "bump-build", "increase-build"):
        if args.step <= 0:
            raise SystemExit("--step must be > 0")
        new_version = current_version
        new_build = current_build + args.step
    elif args.command == "set-version":
        parse_semver(args.version)
        new_version = args.version
        new_build = current_build if args.build is None else args.build
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    update_files(repo_root, new_version, new_build)


if __name__ == "__main__":
    main()
