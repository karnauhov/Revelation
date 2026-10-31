"""Check that every legacy workflow step has an explicit local equivalent."""

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

EQUIVALENTS = {
    "Checkout repository": "core.prepare/source.bundle and Context.checkout at exact Git SHA; private clone; no owner checkout mutation",
    "Install Flutter": "Profile flutter=3.47.2; preflight verifies installed SDK; local SDK/pub caches replace hosted action cache",
    "Get Flutter dependencies": "quality/dependencies: flutter pub get inside isolated checkout",
    "Format check": "quality/format: dart format --output=none --set-exit-if-changed .",
    "Analyze": "quality/analyze: flutter analyze --no-pub",
    "Unit tests": "quality/unit: flutter test --exclude-tags widget",
    "Widget tests": "quality/widget: flutter test --tags widget",
    "Coverage": "quality/coverage: flutter test --coverage",
    "Filter coverage report": "quality/filter-coverage: scripts/filter_lcov.dart",
    "Coverage thresholds": "quality/coverage-threshold: scripts/coverage_baseline.dart --min-effective=90.0",
    "Forbidden pattern checks": "quality/forbidden: scripts/check_forbidden_patterns.dart",
    "Encoding sanity checks": "quality/encoding: scripts/check_encoding_sanity.dart",
    "Set up JDK 17": "Host-local JAVA_HOME/PATH; preflight java -version and flutter doctor -v; no global settings mutation",
    "Extract version and build number (Windows)": "Revelation metadata reads pubspec at source SHA; verify_versions checks all four helper-managed version files",
    "Extract version and build number (Linux)": "Same immutable job version/build; Linux cannot increment or select a new source SHA",
    "Extract Release Notes": "metadata extracts the exact version section from committed CHANGELOG; one release_notes.txt",
    "Build APK": "windows/apk: flutter build apk --release with production defines and signing environment",
    "Rename APK": "Move completed APK to canonical packages/Revelation-android-version-build.apk; no retained duplicate",
    "Build App Bundle (AAB)": "windows/aab: flutter build appbundle --release with the same defines/signing",
    "Rename AAB": "Move completed AAB to canonical packages/Revelation-android-version-build.aab",
    "Build Windows App": "windows/windows: flutter build windows --release --no-tree-shake-icons",
    "Install Inno Setup": "Pre-provisioned local Inno Setup; preflight validates configured ISCC.exe",
    "Build Installer with Inno Setup": "windows/installer: ISCC setup.iss using committed helper-synchronized version/build",
    "Upload windows Artifacts": "Canonical local packages plus SHA-256/checkpoints; GitHub receives only verified mirror assets",
    "Create MSIX Package": "windows/msix: dart run msix:create --build-windows false; Store identity retained",
    "Rename MSIX Package": "Move MSIX directly to canonical packages/Revelation-windows-version-build.msix",
    "Build web": "windows/web: flutter build web --release --source-maps and production defines",
    "Prepare Sentry web source maps": "windows/sentry-web: scripts/prepare_sentry_web_source_maps.dart",
    "Upload Sentry debug symbols and source maps": "windows/sentry-web: sentry_dart_plugin using this OS's local token",
    "Generate web loader manifest": "windows/web-manifest: scripts/generate_web_loader_manifest.py",
    "Remove web source maps from packaged build": "Exclude every .map from distribution ZIP after Sentry upload; retain private builder symbols for resume",
    "Zip Web Build": "windows/web-zip: root-relative ZIP written once into canonical packages",
    "Create GitHub Release": "GitHub.ensure_release creates owned draft at exact SHA/tag; publish_job finalizes after both hosts, seven packages and required gates",
    "Upload upload_url as artifact": "exchange.json records release ID; immutable handoff transfers job through the same draft release",
    "Upload APK to Release": "send_result/publish_job: SHA-256 download read-back of verified APK; existing files never overwritten",
    "Upload AAB to Release": "send_result/publish_job: verified AAB mirror asset and read-back",
    "Upload EXE to Release": "send_result/publish_job: verified Inno installer mirror and read-back",
    "Upload MSIX to Release": "send_result/publish_job: Store MSIX mirror and read-back; unsigned Store package clearly identified",
    "Upload Web ZIP to Release": "send_result/publish_job: map-free Web ZIP mirror and read-back",
    "Download upload_url artifact": "receive_jobs obtains immutable job and exact draft release ID through GitHub; no Windows disk/session required",
    "Read upload_url": "GitHub API resolves owned release ID and verifies target SHA/tag/run marker",
    "Install dependencies": "Linux prerequisites recorded in release guide; native Flutter/Linux/Snap preflight and actual build expose missing packages without hosted fallback",
    "Build Linux": "linux/linux: flutter build linux --release with same job defines/version/build/SHA",
    "Upload Sentry Linux debug symbols": "linux/sentry-linux: sentry_dart_plugin --sentry-define=upload_source_maps=false",
    "Archive Linux Build": "linux/linux-tar: TAR.GZ of x64 release bundle, retaining executable bits/symlinks",
    "Upload Linux Archive to Release": "Linux sends verified TAR.GZ and Snap; Windows sync receives packages/results/logs; temporary exchange IDs cleaned after durable receipt",
}


def inventory():
    source = ROOT / ".github/workflows/flutter_build.yml"
    text = source.read_text(encoding="utf-8")
    # Git stores LF-normalized content; Windows worktree CRLF is not a new blob.
    payload = text.encode("utf-8")
    jobs, current, in_jobs = {}, None, False
    for line in text.splitlines():
        if line == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        match = re.match(r"^  ([a-z0-9-]+):$", line)
        if match:
            current = match.group(1)
            jobs[current] = []
        step = re.match(r"^      - name: (.+)$", line)
        if step:
            name = step.group(1)
            if name not in EQUIVALENTS:
                raise SystemExit("Missing local equivalent: " + name)
            jobs[current].append({"name": name, "local_equivalent": EQUIVALENTS[name]})
    return {"schema": 1, "source": ".github/workflows/flutter_build.yml",
            "git_blob": hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest(),
            "sha256": hashlib.sha256(payload).hexdigest(), "jobs": jobs,
            "actions": sorted(set(re.findall(r"uses: (.+)", text))),
            "secret_names": sorted(set(re.findall(r"secrets\.([A-Z_]+)", text))),
            "legacy_trigger": "push/main with paths and head-commit [skip ci]/[ci skip]; retained until full REV301 trial",
            "local_trigger": "all new local and received remote commits; full message [skip ci]; one durable entry per project+SHA",
            "additional_gates": ["local integration on supported applicable devices", "docs sync", "APK/AAB release certificate",
                                 "MSIX identity/version", "Web map exclusion", "Linux Snap owner commands/install/smoke",
                                 "cross-host failure/receipt/cleanup", "complete seven-package GitHub read-back before trigger activation"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "scripts/local_release/workflow-inventory.json"
    value = inventory()
    if args.check:
        if json.loads(path.read_text(encoding="utf-8")) != value:
            raise SystemExit("Workflow inventory changed; review parity before regenerating")
    else:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Workflow parity: {len(value['jobs'])} jobs, {sum(map(len, value['jobs'].values()))} mapped steps")
