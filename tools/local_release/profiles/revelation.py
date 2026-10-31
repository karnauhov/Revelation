"""Revelation's build/sign/package policy; the coordinator stays project-neutral."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
import tempfile
import time
import zipfile

from ..core import ReleaseError, atomic_json, capture, digest, git, inside, read_json


QUALITY = ["dependencies", "format", "analyze", "unit", "widget", "coverage", "filter-coverage",
           "coverage-threshold", "forbidden", "encoding", "docs-sync"]
WINDOWS = ["apk", "aab", "windows", "installer", "msix", "web", "sentry-web", "web-manifest", "web-zip", "verify-windows"]
LINUX = ["linux", "sentry-linux", "linux-tar", "snap", "verify-linux"]


def quality_steps(repo, sha):
    steps = list(QUALITY)
    # Historical app snapshots predate the coordinator. New snapshots carry
    # the committed inventory/cutover guard and must execute it on both hosts.
    if git(repo, "ls-tree", "--name-only", sha, "--", "scripts/local_release/inventory.py"):
        steps.append("workflow-parity")
    return steps


def metadata(repo, sha, profile):
    pubspec = git(repo, "show", f"{sha}:pubspec.yaml")
    match = re.search(r"^version:\s*(\d+\.\d+\.\d+)\+(\d+)\s*$", pubspec, re.M)
    if not match:
        raise ReleaseError("Cannot parse committed version")
    version, build = match.group(1), int(match.group(2))
    names = [f"Revelation-android-{version}-{build}.apk", f"Revelation-android-{version}-{build}.aab",
             f"Revelation-windows-{version}-{build}.exe", f"Revelation-windows-{version}-{build}.msix",
             f"Revelation-web-{version}-{build}.zip", f"Revelation-linux-{version}-{build}.tar.gz",
             f"Revelation-linux-{version}-{build}-amd64.snap"]
    changelog = git(repo, "show", f"{sha}:CHANGELOG.md")
    notes = re.search(r"(^## \[" + re.escape(version) + r"\].*?)(?=\n## |\Z)", changelog, re.M | re.S)
    if not notes:
        raise ReleaseError("Release notes missing for committed version")
    from .linux_release import overlays
    overlay_hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in overlays(repo, sha, profile).items()}
    specifications = {name: {"host": "windows", "gates": ["verify-windows"]} for name in names[:5]}
    specifications[names[5]] = {"host": "linux", "gates": ["linux-tar", "inspect-linux-tar"]}
    specifications[names[6]] = {"host": "linux", "gates": ["snap", "inspect-snap"]}
    checks = quality_steps(repo, sha)
    return dict(version=version, build=build, tag=f"v{version}+{build}", artifacts=names,
                protocol_version=2, artifact_specs=specifications, generated_source_overlays=overlay_hashes,
                release_notes=notes.group(1).strip().removesuffix("---").strip(),
                required_steps={"windows": ["preflight", *checks, "integration-windows", "integration-android", "integration-web", "signing-preflight", *WINDOWS],
                                "linux": ["preflight", *checks, "integration-linux", *LINUX, "inspect-linux-tar", "inspect-snap"]},
                architectures={"android": ["armeabi-v7a", "arm64-v8a", "x86_64"],
                               "windows": ["x64"], "linux": ["x64"], "snap": ["amd64"], "web": ["javascript"]},
                generated_output_paths=["coverage/lcov.info"],
                step_dependencies={
                    "installer": ["windows"], "msix": ["windows"],
                    "sentry-web": ["web"], "web-manifest": ["sentry-web"], "web-zip": ["web-manifest"],
                    "verify-windows": ["apk", "aab", "installer", "msix", "web-zip"],
                    "sentry-linux": ["linux"], "linux-tar": ["linux"],
                    "inspect-linux-tar": ["linux-tar"], "inspect-snap": ["snap"],
                    "verify-linux": ["snap", "linux-tar", "inspect-linux-tar", "inspect-snap"],
                },
                apple="Outside current REV301 scope; no Apple builder is required for this profile")


def compile_defines(config):
    defines_path = Path(config.get("defines_file", ""))
    if not defines_path.is_file():
        raise ReleaseError("Configure this OS's defines_file outside the job")
    defines = read_json(defines_path)
    # The workflow explicitly sets production, independent of local dev settings.
    defines["SENTRY_ENVIRONMENT"] = "production"
    required = ("SUPABASE_URL", "SUPABASE_KEY", "SENTRY_DSN")
    if any(not defines.get(key) for key in required):
        raise ReleaseError("Production SUPABASE_URL, SUPABASE_KEY and SENTRY_DSN are required")
    if defines.get("SENTRY_ENVIRONMENT") != "production":
        raise ReleaseError("Production defines require SENTRY_ENVIRONMENT=production")
    return defines


def input_metadata(config):
    value = json.dumps(compile_defines(config), sort_keys=True, separators=(",", ":")).encode()
    return {"compile_defines_sha256": hashlib.sha256(value).hexdigest()}


def configured_secrets(ctx):
    defines = compile_defines(ctx.config)
    fingerprint = input_metadata(ctx.config)["compile_defines_sha256"]
    if ctx.job.get("compile_defines_sha256") and ctx.job["compile_defines_sha256"] != fingerprint:
        raise ReleaseError("Production compile defines differ from the prepared job; keep the same settings on both OSes")
    ctx.result["compile_defines_sha256"] = fingerprint
    token = ctx.env.get("SENTRY_AUTH_TOKEN")
    if not token and ctx.config.get("sentry_properties") and Path(ctx.config["sentry_properties"]).is_file():
        text = Path(ctx.config["sentry_properties"]).read_text(encoding="utf-8")
        match = re.search(r"^auth_token\s*[=:]\s*(.+)\s*$", text, re.M)
        token = match.group(1).strip() if match else None
    if token:
        ctx.env["SENTRY_AUTH_TOKEN"] = token
    if ctx.host == "windows" and ctx.config.get("signing_store_file"):
        store = Path(ctx.config["signing_store_file"])
        ctx.env["SIGNING_STORE_FILE_BASE64"] = base64.b64encode(store.read_bytes()).decode("ascii")
    ctx.refresh_redaction([token, *defines.values()])
    ctx.refresh_redaction([base64.b64encode(f"{key}={value}".encode()).decode() for key, value in defines.items()])
    ctx.refresh_redaction([ctx.env.get("SIGNING_STORE_FILE_BASE64")])
    # Keep compile-time secrets host-local; never include them in source.bundle.
    local_defines = ctx.workspace / "api-keys.json"
    atomic_json(local_defines, defines)
    return local_defines


def verify_versions(ctx):
    pubspec = (ctx.workspace / "pubspec.yaml").read_text(encoding="utf-8")
    v, b = ctx.job["version"], ctx.job["build"]
    major, minor, patch = map(int, v.split("."))
    checks = [
        (pubspec, rf"^version:\s*{re.escape(v)}\+{b}\s*$"),
        (pubspec, rf"^\s*msix_version:\s*{major}\.{minor}\.{patch + b}\.0\s*$"),
        ((ctx.workspace / "setup.iss").read_text(), rf'^#define MyAppVersion "{re.escape(v)}"\s*$'),
        ((ctx.workspace / "setup.iss").read_text(), rf'^#define MyAppBuild "{b}"\s*$'),
        ((ctx.workspace / "snap/snapcraft.yaml").read_text(encoding="utf-8"), rf"^version:\s*'{re.escape(v)}\.{b}'\s*$"),
        ((ctx.workspace / "snap/gui/revelation-x.desktop").read_text(), rf"^Version={re.escape(v)}\.{b}\s*$"),
    ]
    if any(not re.search(pattern, text, re.M) for text, pattern in checks):
        raise ReleaseError("Version files are not synchronized; use the existing version helper in the source repository")


def preflight(ctx):
    if ctx.host == "linux":
        from .linux_release import provision_flutter, apply_overlays
        provision_flutter(ctx)
        apply_overlays(ctx)
        collect_snap_history(ctx)
    verify_versions(ctx)
    flutter = json.loads(ctx.command(["flutter", "--version", "--machine"]))
    if flutter["frameworkVersion"] != ctx.job["profile"]["flutter"]:
        raise ReleaseError("Flutter version differs from the release profile")
    ctx.command(["git", "--version"])
    ctx.command(["flutter", "doctor", "-v"])
    configured_secrets(ctx)
    if ctx.host == "windows":
        java = ctx.command(["java", "-version"])
        if not re.search(r'version "17[.\"]', java):
            raise ReleaseError("Windows Android builder requires Java 17, matching the workflow")
        for key in ("SIGNING_KEY_ALIAS", "SIGNING_KEY_PASSWORD", "SIGNING_STORE_PASSWORD", "SIGNING_STORE_FILE_BASE64"):
            if not ctx.env.get(key):
                raise ReleaseError("Missing Android release signing variable: " + key)
        if not Path(ctx.config.get("inno_setup", "")).is_file():
            raise ReleaseError("Configure the installed Inno Setup compiler")
    if ctx.host == "linux":
        if capture(["uname", "-m"]) != "x86_64":
            raise ReleaseError("This profile currently requires an x86_64 Linux builder")
        # Snap-only tools are checked in their own build/inspection stages.
        # Their absence or diagnostic exit codes must not block a portable TAR.
    (ctx.directory / "release_notes.txt").write_text(ctx.job["release_notes"] + "\n", encoding="utf-8", newline="\n")
    atomic_json(ctx.directory / "results" / f"{ctx.host}-environment.json", {
        "sha": ctx.job["sha"], "version": ctx.job["version"], "build": ctx.job["build"],
        "flutter": flutter, "python": sys.version, "host": ctx.host,
        "snap_tools": {name: shutil.which(name, path=ctx.env.get("PATH")) for name in ("snapcraft", "unsquashfs")}
                      if ctx.host == "linux" else {},
    })


def collect_snap_history(ctx):
    """Collect bounded, non-secret command candidates for owner-specific setup.

    History is evidence, never an instruction to execute arbitrary shell text.
    """
    candidates = []
    history = Path.home() / ".bash_history"
    if history.is_file():
        import shlex
        for line in history.read_text(encoding="utf-8", errors="replace").splitlines()[-5000:]:
            if not re.search(r"\b(snapcraft|multipass|lxc|lxd)\b", line):
                continue
            if re.search(r"[;$`|><]|token|password|secret|login|credential|auth|key|environment\.", line, re.I):
                continue
            try:
                words = shlex.split(line)
            except ValueError:
                continue
            if words and (Path(words[0]).name in ("snapcraft", "multipass", "lxc", "lxd")
                          or words[0] == "sudo" and len(words) > 1 and Path(words[1]).name in ("snapcraft", "multipass", "lxc", "lxd")):
                if line not in candidates:
                    candidates.append(line)
    path = ctx.directory / "logs/linux/snap-history-candidates.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Past command candidates for review; none were executed automatically.\n" +
                    "\n".join(ctx.redact(line) for line in candidates) + "\n", encoding="utf-8")


def quality(ctx):
    commands = {
        "dependencies": ["flutter", "pub", "get"],
        "format": ["dart", "format", "--output=none", "--set-exit-if-changed", "."],
        "analyze": ["flutter", "analyze", "--no-pub"],
        "unit": ["flutter", "test", "--no-pub", "--exclude-tags", "widget", "--concurrency=1", "--reporter=expanded"],
        "widget": ["flutter", "test", "--no-pub", "--tags", "widget", "--concurrency=1", "--reporter=expanded"],
        "coverage": ["flutter", "test", "--no-pub", "--coverage", "--concurrency=1", "--reporter=expanded"],
        "filter-coverage": ["dart", "run", "scripts/filter_lcov.dart", "--lcov=coverage/lcov.info"],
        "coverage-threshold": ["dart", "run", "scripts/coverage_baseline.dart", "--min-effective=90.0"],
        "forbidden": ["dart", "run", "scripts/check_forbidden_patterns.dart"],
        "encoding": ["dart", "run", "scripts/check_encoding_sanity.dart"],
        "docs-sync": ["dart", "run", "scripts/check_docs_sync.dart"],
        "workflow-parity": ["python", "scripts/local_release/inventory.py", "--check"],
    }
    for name, argv in commands.items():
        if name == "workflow-parity" and name not in ctx.job["required_steps"][ctx.host]:
            continue
        def action(argv=argv, name=name):
            ctx.command(argv)
            if name == "coverage-threshold":
                shutil.copy2(ctx.workspace / "coverage/lcov.info", ctx.directory / "results" / f"{ctx.host}-lcov.info")
        outputs = [f"results/{ctx.host}-lcov.info"] if name == "coverage-threshold" else []
        ctx.stage(name, action, outputs)


def integration_files(ctx, platform, action):
    tests = sorted((ctx.workspace / "integration_test").rglob("*_test.dart"))
    if not tests:
        raise ReleaseError("No integration tests found in the pinned checkout")
    records = []
    for test in tests:
        relative = test.relative_to(ctx.workspace).as_posix()
        step = "integration-" + platform + "-" + relative.removeprefix("integration_test/").removesuffix(".dart").replace("/", "_")
        ctx.stage(step, lambda test=test: action(test))
        records.append(relative)
    return records


def recover_for_deletion(ctx):
    """Restore only existing owner-state journals; never start another test."""
    from .. import native_fixture
    folder = ctx.root / "w" / ctx.job["sha"][:12]
    backup = folder / (ctx.host + "-test-state")
    journal = backup / "restore.json"
    if journal.exists():
        if native_fixture.application_running():
            raise ReleaseError("Close Revelation so original user data can be restored before deletion")
        targets = [native_fixture.documents_directory() / "revelation/db" / name for name in native_fixture.MODULES]
        if ctx.host == "windows":
            targets.append(Path(os.environ["APPDATA"]) / "AI11/revelation/shared_preferences.json")
        native_fixture.restore(journal, backup, targets)
    journal = folder / "snap-acceptance/restore.json"
    if journal.exists():
        if ctx.host != "linux" or native_fixture.application_running():
            raise ReleaseError("Linux Snap user-data restoration must finish before deleting this build")
        from .snap_acceptance import restore, sudo_lease
        with sudo_lease(ctx):
            ctx.restoring_snap = True
            try:
                restore(ctx, journal)
            finally:
                ctx.restoring_snap = False


def integration(ctx):
    targets = set(ctx.config.get("integration_targets", [ctx.host, "android", "web"] if ctx.host == "windows" else [ctx.host]))
    if ctx.host in targets and ctx.host in ("windows", "linux"):
        def native():
            from ..native_fixture import installed_modules
            backup = ctx.root / "w" / ctx.job["sha"][:12] / (ctx.host + "-test-state")
            with installed_modules(ctx.workspace, backup) as state:
                # Flutter 3.47.2 closes DesktopLogReader after one application;
                # use a fresh tool process for every file and retain checkpoints.
                tests = integration_files(ctx, ctx.host, lambda test: ctx.command([
                    "flutter", "test", "--no-pub", test.relative_to(ctx.workspace).as_posix(),
                    "-d", ctx.host, "--reporter=expanded"]))
            atomic_json(ctx.directory / "results" / f"{ctx.host}-integration-state.json", {**state, "restored": True, "tests": tests})
        ctx.stage("integration-" + ctx.host, native, [f"results/{ctx.host}-integration-state.json"])
    if ctx.host == "windows" and "android" in targets:
        def android():
            from ..prerequisites import android_device
            device = ctx.config.get("android_device")
            if not device:
                raise ReleaseError("Configure an isolated Android device for all local integration tests")
            with android_device(ctx):
                prepare_android_fixture(ctx, device)
                integration_files(ctx, "android", lambda test: ctx.command([
                    "flutter", "test", "--no-pub", "--no-uninstall", test.relative_to(ctx.workspace).as_posix(),
                    "-d", device, "--reporter=expanded"], cwd=ctx.workspace))
        ctx.stage("integration-android", android)
    if ctx.host == "windows" and "web" in targets:
        def web():
            from ..prerequisites import chrome_driver
            recover_web_cache(ctx)
            if not ctx.config.get("chromedriver_port"):
                raise ReleaseError("Start a matching ChromeDriver and configure chromedriver_port")
            def run_file(test):
                target = web_integration_target(ctx, test)
                ctx.command(["flutter", "drive", "--no-pub", "--release", "--driver=test_driver/integration_test.dart",
                             "--target=" + target, "-d", "web-server",
                             "--browser-name=chrome", "--headless", "--driver-port=" + str(ctx.config["chromedriver_port"]),
                             "--web-port=" + str(ctx.config.get("web_port", 8796)),
                             "--web-browser-flag=--incognito",
                             "--web-browser-flag=--user-data-dir=" + str(ctx.root / "w" / "chrome-Revelation-REV301-a5305")],
                            cwd=ctx.workspace)
            with chrome_driver(ctx):
                integration_files(ctx, "web", run_file)
        ctx.stage("integration-web", web)


def recover_web_cache(ctx):
    """Discard only Web bookkeeping containing the temporary MSBuild alias.

    Flutter compares output path strings when removing previous configurations.
    C: and SUBST R: name the same files, so mixed paths delete fresh resources.
    Keep Web commands physical and forget that obsolete output bookkeeping.
    """
    drive = str(ctx.config.get("workspace_drive", "")).rstrip("/\\").upper()
    if not drive or drive == ctx.workspace.drive.upper():
        return
    removed = []
    cache = ctx.workspace / ".dart_tool/flutter_build"
    stamps = [*cache.glob("*/web_*.stamp"), *cache.glob("*/gen_localizations.stamp")]
    for stamp in stamps:
        if not re.fullmatch(r"[a-f0-9]{32}", stamp.parent.name):
            continue
        try:
            outputs = read_json(stamp).get("outputs", [])
        except (OSError, ValueError, AttributeError):
            continue
        if any(isinstance(path, str) and path.upper().startswith(drive + "\\") for path in outputs):
            removed.append({"path": stamp.relative_to(ctx.workspace).as_posix(), "sha256": digest(stamp)})
            stamp.unlink()
    if removed:
        (ctx.workspace / "build/web/.last_build_id").unlink(missing_ok=True)
        evidence = ctx.directory / "results/windows-web-cache-recovery.json"
        old = read_json(evidence) if evidence.exists() else {"repairs": []}
        old["repairs"].append({"physical_workspace": str(ctx.workspace), "removed_bookkeeping": removed,
                               "reason": "Flutter output cleanup compared physical and SUBST paths"})
        atomic_json(evidence, old)


def web_integration_target(ctx, test):
    relative = test.relative_to(ctx.workspace).as_posix()
    source = test.read_text(encoding="utf-8")
    if not re.fullmatch(r"integration_test/[A-Za-z0-9_/]+_test\.dart", relative):
        raise ReleaseError("Web integration entrypoint must be a local reviewed test path")
    name = hashlib.sha256(relative.encode()).hexdigest()[:16] + "_test.dart"
    target = ctx.workspace / ".dart_tool/ai11_integration" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    scenario = "../../" + relative
    compatibility = None
    adapted, reason = source, None
    # Exact historical smoke tests predate Web/native and parallel-reader rules.
    # Keep the immutable app/test checkout intact and record the reviewed test-only
    # adapter. New source snapshots contain the same platform assertions directly.
    if (relative == "integration_test/smoke/about_download_navigation_smoke_test.dart" and
            hashlib.sha256(source.encode()).hexdigest() == "f2dffa6c40999a4250ab56b8d3ef3932bf8e77b04b33faa778ef945a3f391839"):
        adapted = "import 'package:flutter/foundation.dart';\n" + source
        for key in ("refresh_databases", "show_local_folder"):
            adapted = adapted.replace(f"expect(find.text(l10n.{key}), findsOneWidget);",
                f"expect(find.text(l10n.{key}), kIsWeb ? findsNothing : findsOneWidget);")
        adapted = adapted.replace("import 'smoke_test_harness.dart';",
            "import '../../integration_test/smoke/smoke_test_harness.dart';")
        reason = "Assert that native-only maintenance tools are absent on Web"
    elif (relative == "integration_test/smoke/bible_first_load_retry_smoke_test.dart" and
            hashlib.sha256(source.encode()).hexdigest() == "a089fa74624dd0979cd08933a817a95a5591e4cdcbf228d1169242f04451a739"):
        adapted = source.replace("expect(source.listCalls, 2);",
            "expect(source.listCalls, 1 + context.read<BibleWorkspaceCubit>().state.paneIds.length);")
        adapted = adapted.replace("'failureBoundary': 'module discovery',",
            "'failureBoundary': 'module discovery',\n"
            "            'readerPanes': context.read<BibleWorkspaceCubit>().state.paneIds.length,\n"
            "            'moduleDiscoveryCalls': source.listCalls,")
        reason = "One failed primary discovery plus one successful discovery per open reader, including default translation"
    if reason:
        copied = target.with_name(target.stem + "_scenario.dart")
        copied.write_text(adapted, encoding="utf-8", newline="\n")
        scenario = copied.name
        compatibility = {"reason": reason,
                         "target": copied.relative_to(ctx.workspace).as_posix(), "sha256": digest(copied)}
    target.write_text("import 'package:flutter_test/flutter_test.dart';\n"
        "import 'package:integration_test/common.dart';\n"
        "import 'package:integration_test/integration_test.dart';\n"
        f"import '{scenario}' as scenario;\n\n"
        "void main() {\n  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();\n"
        "  final previousReporter = reportTestException;\n"
        "  reportTestException = (details, description) {\n"
        "    previousReporter(details, description);\n"
        "    binding.results[description] = Failure(description, '${details.exception}\\n${details.stack}');\n"
        "  };\n  scenario.main();\n}\n",
        encoding="utf-8", newline="\n")
    evidence = ctx.directory / "results/windows-web-driver-targets.json"
    records = read_json(evidence) if evidence.exists() else {}
    records[relative] = {"target": target.relative_to(ctx.workspace).as_posix(), "sha256": digest(target),
                         "test_sha256": digest(test), "binding": "IntegrationTestWidgetsFlutterBinding",
                         **({"test_compatibility": compatibility} if compatibility else {})}
    atomic_json(evidence, records)
    return target.relative_to(ctx.workspace).as_posix()


def prepare_android_fixture(ctx, device):
    from .android_release import dependencies
    dependencies(ctx)
    from ..native_fixture import MODULES
    avd = ctx.config.get("android_avd_name")
    if not device.startswith("emulator-") or not avd:
        raise ReleaseError("Android fixtures require this release's explicitly configured isolated emulator")
    sdk = Path(ctx.config["android_sdk"])
    adb = sdk / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    actual = ctx.command([adb, "-s", device, "emu", "avd", "name"])
    if avd not in actual.splitlines():
        raise ReleaseError("Android fixture emulator identity differs from configured AVD")
    ctx.command(["flutter", "build", "apk", "--debug", "--target=lib/main.dart", "--target-platform=android-x64"], cwd=ctx.workspace)
    ctx.command([adb, "-s", device, "install", "-r", ctx.workspace / "build/app/outputs/flutter-apk/app-debug.apk"])
    ctx.command([adb, "-s", device, "shell", "run-as ai11.link.revelation mkdir -p app_flutter/revelation/db"])
    records = {}
    for name in MODULES:
        source = ctx.workspace / "web/db" / name
        remote = "app_flutter/revelation/db/" + name
        with source.open("rb") as stream:
            # On Windows adb shell treats stdin as text and stops at DOS EOF
            # (0x1a), corrupting SQLite fixtures. exec-in uses binary copy_to_file.
            ctx.command([adb, "-s", device, "exec-in", "run-as", "ai11.link.revelation",
                         "sh", "-c", "cat > " + remote], stdin=stream)
        records[name] = wait_android_fixture(ctx, adb, device, source, remote)
    atomic_json(ctx.directory / "results/android-fixtures.json", {"avd": avd, "serial": device, "module_sha256": records})


def wait_android_fixture(ctx, adb, device, source, remote):
    # exec-in has no remote exit acknowledgment: it may return while Android
    # is still writing buffered input. Confirm the full size before hashing.
    expected, size = digest(source), source.stat().st_size
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        output = ctx.command([adb, "-s", device, "shell", "run-as ai11.link.revelation wc -c " + remote], success_codes=(0, 1))
        fields = output.split()
        if fields and fields[0].isdigit() and int(fields[0]) == size:
            actual = ctx.command([adb, "-s", device, "shell", "run-as ai11.link.revelation sha256sum " + remote])
            if actual.split()[0] != expected:
                raise ReleaseError("Android integration module digest mismatch after complete binary transfer")
            return expected
        time.sleep(.5)
    raise ReleaseError("Android integration module transfer did not finish within 60 seconds")


def copy_artifact(ctx, source, suffix):
    name = next(n for n in ctx.job["artifacts"] if n.endswith(suffix))
    path = inside(ctx.workspace, source)
    if not path.is_file() or path.stat().st_size == 0:
        raise ReleaseError("Missing build artifact: " + source)
    # A distributed package has exactly one canonical local file.
    os.replace(path, ctx.output / name)


def output_for(ctx, suffix):
    return "packages/" + next(n for n in ctx.job["artifacts"] if n.endswith(suffix))


def build_windows(ctx):
    targets = set(ctx.config.get("build_targets", ["android", "windows", "web"]))
    defines = ["--release", "--target=lib/main.dart", "--dart-define-from-file=api-keys.json"]
    if "android" in targets:
        from .android_release import dependencies, recover_cache
        if ctx.result["steps"].get("android-cache-recovery", {}).get("status") == "failed":
            recover_cache(ctx)
        else:
            dependencies(ctx)
        ctx.stage("signing-preflight", lambda: validate_signing(ctx), ["results/windows-signing.json"], always=True)
    for target, source, suffix in [
        ("apk", "build/app/outputs/flutter-apk/app-release.apk", ".apk"),
        ("appbundle", "build/app/outputs/bundle/release/app-release.aab", ".aab"),
    ]:
        if "android" not in targets:
            continue
        name = "apk" if target == "apk" else "aab"
        def action(target=target, source=source, suffix=suffix):
            # Kotlin incremental caches require the project and Pub cache on
            # the same physical drive; the short SUBST alias is for MSBuild.
            ctx.command(["flutter", "build", target, *defines], cwd=ctx.workspace)
            copy_artifact(ctx, source, suffix)
        ctx.stage(name, action, [output_for(ctx, suffix)])
    if "windows" in targets:
        build_native_windows(ctx, defines)
    if "web" in targets:
        build_web(ctx, defines)
    if all((ctx.directory / output_for(ctx, suffix)).is_file() for suffix in (".apk", ".aab", ".exe", ".msix", ".zip")):
        ctx.stage("verify-windows", lambda: verify_windows(ctx), ["results/windows-packages.json"])


def validate_signing(ctx):
    with tempfile.TemporaryDirectory(prefix="local-release-signing-") as temporary:
        folder = Path(temporary)
        store = Path(ctx.config["signing_store_file"]) if ctx.config.get("signing_store_file") else folder / "release.jks"
        if ctx.config.get("signing_store_file") and not store.is_file():
            raise ReleaseError("Configured host-local signing file does not exist")
        if not ctx.config.get("signing_store_file"):
            store.write_bytes(base64.b64decode(ctx.env["SIGNING_STORE_FILE_BASE64"], validate=True))
        common = ["-keystore", store, "-alias", ctx.env["SIGNING_KEY_ALIAS"], "-storepass:env", "SIGNING_STORE_PASSWORD"]
        ctx.command(["keytool", "-certreq", *common, "-keypass:env", "SIGNING_KEY_PASSWORD", "-file", folder / "request.csr"])
        certificate = folder / "certificate.der"
        ctx.command(["keytool", "-exportcert", *common, "-file", certificate])
        actual = digest(certificate)
        expected = ctx.config.get("expected_signing_certificate_sha256")
        if expected and actual != expected:
            raise ReleaseError("Configured signing certificate differs from the pinned release certificate")
        atomic_json(ctx.directory / "results/windows-signing.json", {
            "certificate_sha256": actual, "private_key_password_verified": True,
            "expected_certificate_matched": actual == expected if expected else None,
        })


def build_native_windows(ctx, defines):
    ctx.stage("windows", lambda: ctx.command(["flutter", "build", "windows", "--no-tree-shake-icons", *defines]),
              always=not (ctx.workspace / "build/windows/x64/runner/Release/revelation.exe").is_file())
    def installer():
        ctx.command([ctx.config["inno_setup"], "setup.iss"])
        name = next(n for n in ctx.job["artifacts"] if n.endswith(".exe"))
        copy_artifact(ctx, "build/windows/" + name, ".exe")
    ctx.stage("installer", installer, [output_for(ctx, ".exe")])
    def msix():
        ctx.command(["dart", "run", "msix:create", "--build-windows", "false"])
        copy_artifact(ctx, "build/windows/x64/runner/Release/revelation.msix", ".msix")
    ctx.stage("msix", msix, [output_for(ctx, ".msix")])


def build_web(ctx, defines):
    name = output_for(ctx, ".zip")
    packaged = ctx.directory / name
    previous = ctx.result["steps"].get("web-zip", {})
    if (previous.get("status") == "passed" and packaged.is_file()
            and previous.get("outputs", {}).get(name) == digest(packaged)):
        return
    recover_web_cache(ctx)
    # Integration builds may have replaced build/web. If the distribution ZIP
    # needs rebuilding, always rebuild lib/main.dart and its dependent steps.
    ctx.result["steps"].pop("web", None)
    ctx.invalidate_dependents("web")
    ctx.stage("web", lambda: ctx.command(["flutter", "build", "web", "--source-maps", *defines], cwd=ctx.workspace),
              always=True)
    def sentry_web():
        ctx.command(["dart", "run", "scripts/prepare_sentry_web_source_maps.dart", "--web-build-dir", "build/web"], cwd=ctx.workspace)
        ctx.command(["dart", "run", "sentry_dart_plugin"], cwd=ctx.workspace)
    ctx.stage("sentry-web", sentry_web)
    ctx.stage("web-manifest", lambda: ctx.command(["python", "scripts/generate_web_loader_manifest.py", "--web-build-dir", "build/web"], cwd=ctx.workspace),
              always=not (ctx.workspace / "build/web/loader_manifest.json").is_file())
    def web_zip():
        # Keep private symbol files in the builder for resumption; omit from distribution.
        root = ctx.workspace / "build/web"
        path = ctx.directory / output_for(ctx, ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(root.rglob("*")):
                if item.is_file() and item.suffix != ".map":
                    archive.write(item, item.relative_to(root).as_posix())
    ctx.stage("web-zip", web_zip, [output_for(ctx, ".zip")])


def verify_windows(ctx):
    """Check signed packages and embedded version metadata before accepting assets."""
    import xml.etree.ElementTree as ET
    sdk = Path(ctx.config.get("android_sdk", os.environ.get("ANDROID_SDK_ROOT", str(Path.home() / "AppData/Local/Android/sdk"))))
    tools = sorted((sdk / "build-tools").glob("*"), key=lambda p: tuple(int(n) if n.isdigit() else 0 for n in re.split(r"[.-]", p.name)))
    if not tools:
        raise ReleaseError("Android build-tools are required for package verification")
    tool = tools[-1]
    apk = ctx.directory / output_for(ctx, ".apk")
    badging = ctx.command([tool / "aapt.exe", "dump", "badging", apk])
    if f"versionCode='{ctx.job['build']}'" not in badging or f"versionName='{ctx.job['version']}'" not in badging:
        raise ReleaseError("APK version differs from job")
    signing = ctx.command([tool / "apksigner.bat", "verify", "--verbose", "--print-certs", apk])
    # Derive the expected release certificate from the configured keystore.
    with tempfile.TemporaryDirectory(prefix="release-signing-") as temporary:
        store = Path(temporary) / "release.jks"
        store.write_bytes(base64.b64decode(ctx.env["SIGNING_STORE_FILE_BASE64"], validate=True))
        certificate = Path(temporary) / "release.der"
        ctx.command(["keytool", "-exportcert", "-keystore", store, "-alias", ctx.env["SIGNING_KEY_ALIAS"],
                     "-storepass:env", "SIGNING_STORE_PASSWORD", "-file", certificate])
        expected = digest(certificate)
    if expected.lower() not in signing.lower().replace(":", ""):
        raise ReleaseError("APK certificate differs from the release keystore")
    aab = ctx.directory / output_for(ctx, ".aab")
    verified = ctx.command(["jarsigner", "-verify", "-verbose", "-certs", aab])
    if "jar verified." not in verified:
        raise ReleaseError("AAB signature could not be verified")
    aab_certificate = ctx.command(["keytool", "-printcert", "-jarfile", aab])
    if expected.lower() not in aab_certificate.lower().replace(":", ""):
        raise ReleaseError("AAB certificate differs from the release keystore")
    with zipfile.ZipFile(ctx.directory / output_for(ctx, ".msix")) as archive:
        manifest = ET.fromstring(archive.read("AppxManifest.xml"))
        identity = next(e for e in manifest.iter() if e.tag.endswith("}Identity"))
        major, minor, patch = map(int, ctx.job["version"].split("."))
        if identity.attrib["Version"] != f"{major}.{minor}.{patch + ctx.job['build']}.0":
            raise ReleaseError("MSIX version differs from job")
        if identity.attrib["Name"] != "AI11.RevelationWin":
            raise ReleaseError("MSIX identity changed")
    with zipfile.ZipFile(ctx.directory / output_for(ctx, ".zip")) as archive:
        if any(n.endswith(".map") for n in archive.namelist()) or "main.dart.js" not in archive.namelist():
            raise ReleaseError("Web ZIP is incomplete or exposes source maps")
    atomic_json(ctx.directory / "results/windows-packages.json", {
        "sha": ctx.job["sha"], "version": ctx.job["version"], "build": ctx.job["build"],
        "apk_release_certificate_sha256": expected, "aab_signature": "verified",
        "msix": "Store identity/version verified; Store package is unsigned as configured",
        "exe": "Inno Setup compiler succeeded; Authenticode is not configured in the existing workflow",
        "web": "JavaScript entrypoint present; source maps excluded after Sentry upload",
    })


def build_linux(ctx):
    from .linux_release import build
    build(ctx)


def run(ctx):
    if ctx.host not in ctx.job["required_steps"]:
        raise ReleaseError("This profile does not target this OS")
    # Preflight always rechecks this host's credentials and restores host-local defines.
    ctx.stage("preflight", lambda: preflight(ctx), always=True)
    phases = set(ctx.config.get("phases", ["quality", "integration", "build"]))
    failures = []
    for name, action in (("quality", quality), ("integration", integration),
                         ("build", build_windows if ctx.host == "windows" else build_linux)):
        if name not in phases:
            continue
        try:
            action(ctx)
        except (ReleaseError, OSError) as error:
            from ..processes import JobStopped
            if isinstance(error, JobStopped):
                raise
            if ctx.host != "linux":
                raise
            failures.append(name)
    if failures:
        raise ReleaseError("Linux phases remain incomplete: " + ", ".join(failures))
