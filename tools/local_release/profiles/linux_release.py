"""Revelation's independent Linux bundle and Snap build/inspection stages."""

import hashlib
import os
from pathlib import Path
import re
import shutil
import tarfile

from ..core import ReleaseError, atomic_json, digest, git

OLD_LOOP = '''foreach(bundled_library ${PLUGIN_BUNDLED_LIBRARIES})
  install(FILES "${bundled_library}"
    DESTINATION "${INSTALL_BUNDLE_LIB_DIR}"
    COMPONENT Runtime)
endforeach(bundled_library)'''
NEW_LOOP = '''foreach(bundled_library ${PLUGIN_BUNDLED_LIBRARIES})
  if("${bundled_library}" MATCHES "crashpad_handler")
    install(PROGRAMS "${bundled_library}"
      DESTINATION "${INSTALL_BUNDLE_LIB_DIR}" COMPONENT Runtime)
  else()
    install(FILES "${bundled_library}"
      DESTINATION "${INSTALL_BUNDLE_LIB_DIR}" COMPONENT Runtime)
  endif()
endforeach(bundled_library)'''


def overlays(repo, sha, profile):
    cmake = git(repo, "show", f"{sha}:linux/CMakeLists.txt") + "\n"
    if OLD_LOOP in cmake:
        cmake = cmake.replace(OLD_LOOP, NEW_LOOP)
    elif 'install(PROGRAMS "${bundled_library}"' not in cmake:
        raise ReleaseError("Review the changed Linux bundled-library installation recipe")
    snap = git(repo, "show", f"{sha}:snap/snapcraft.yaml") + "\n"
    snap = snap.replace("git clone https://github.com/flutter/flutter.git -b stable /usr/local/flutter",
                        "git clone --depth 1 --branch " + profile["flutter"] + " https://github.com/flutter/flutter.git /usr/local/flutter")
    return {"linux/CMakeLists.txt": cmake, "snap/snapcraft.yaml": snap}


def apply_overlays(ctx, workspace=None):
    workspace = workspace or ctx.workspace
    records = {}
    for relative, content in overlays(ctx.workspace, ctx.job["sha"], ctx.job["profile"]).items():
        expected = hashlib.sha256(content.encode()).hexdigest()
        if ctx.job.get("generated_source_overlays", {}).get(relative) != expected:
            raise ReleaseError("Linux packaging correction is not pinned in this job; receive its runtime update")
        path = workspace / relative
        path.write_text(content, encoding="utf-8", newline="\n")
        records[relative] = expected
    atomic_json(ctx.directory / "results/linux-build-overlays.json", records)


def provision_flutter(ctx):
    if not ctx.config.get("auto_provision_flutter", False):
        return
    from ..core import capture
    import json
    try:
        current = json.loads(capture(["flutter", "--version", "--machine"], env=ctx.env))["frameworkVersion"]
    except (ReleaseError, OSError, ValueError):
        current = None
    if current == ctx.job["profile"]["flutter"]:
        return
    sdk = Path.home() / ".cache/ai11-local-release/flutter" / ctx.job["profile"]["flutter"]
    sdk.parent.mkdir(parents=True, exist_ok=True)
    if not sdk.exists():
        ctx.command(["git", "clone", "--depth", "1", "--branch", ctx.job["profile"]["flutter"],
                     "https://github.com/flutter/flutter.git", sdk], cwd=sdk.parent)
    ctx.env["PATH"] = str(sdk / "bin") + os.pathsep + ctx.env.get("PATH", "")


def package_path(ctx, suffix):
    return ctx.output / next(name for name in ctx.job["artifacts"] if name.endswith(suffix))


def inspect_tar(ctx):
    path = package_path(ctx, ".tar.gz")
    with tarfile.open(path) as archive:
        members = {member.name.removeprefix("./"): member for member in archive.getmembers()}
        for name in ("revelation", "lib/crashpad_handler"):
            member = members.get(name)
            if not member or not member.isfile() or not member.mode & 0o111:
                raise ReleaseError("Linux TAR has a missing/nonexecutable program: " + name)
        header = archive.extractfile(members["revelation"]).read(64)
        if header[:4] != b"\x7fELF" or int.from_bytes(header[18:20], "little") != 62:
            raise ReleaseError("Linux TAR executable is not x86_64 ELF")
        if not any(name.startswith("data/flutter_assets/") for name in members):
            raise ReleaseError("Linux TAR is missing Flutter assets")
    atomic_json(ctx.directory / "results/linux-tar-package.json", {"sha256": digest(path), "architecture": "x86_64", "programs_executable": True})


def inspect_snap(ctx):
    snap = package_path(ctx, ".snap")
    meta = ctx.command(["unsquashfs", "-cat", snap, "meta/snap.yaml"])
    if not re.search(r"^name:\s*revelation-x\s*$", meta, re.M):
        raise ReleaseError("Snap identity differs from the profile")
    if not re.search(r"^version:\s*['\"]?" + re.escape(f"{ctx.job['version']}.{ctx.job['build']}") + r"['\"]?\s*$", meta, re.M):
        raise ReleaseError("Snap version differs from the immutable job")
    if not re.search(r"^\s*-\s*amd64\s*$", meta, re.M):
        raise ReleaseError("Snap architecture is not amd64")
    listing = ctx.command(["unsquashfs", "-ll", snap, "lib/crashpad_handler"])
    if not re.search(r"^-rwx[^\n]*lib/crashpad_handler\s*$", listing, re.M):
        raise ReleaseError("Snap Crashpad helper has no executable permission")
    atomic_json(ctx.directory / "results/linux-snap-package.json", {"sha256": digest(snap), "architecture": "amd64", "identity": "revelation-x", "crashpad_executable": True})


def build_snap(ctx):
    # Preserve the owner's confirmed clean -> pack order, with no interactive
    # flutter run. Snap's override-build already performs the release build.
    snapshot = ctx.root / "w" / ctx.job["sha"][:12] / "snap-input"
    if not snapshot.exists():
        hooks = (snapshot / ".git/ai11-no-hooks").as_posix()
        ctx.command(["git", "-c", "core.hooksPath=" + hooks, "clone", "--shared", "--no-checkout", ctx.workspace, snapshot], cwd=ctx.root)
        git(snapshot, "config", "core.hooksPath", hooks)
        ctx.command(["git", "checkout", "--detach", ctx.job["sha"]], cwd=snapshot)
    if git(snapshot, "rev-parse", "HEAD") != ctx.job["sha"]:
        raise ReleaseError("Snap input checkout differs from the job")
    apply_overlays(ctx, snapshot)
    shutil.copy2(ctx.workspace / "api-keys.json", snapshot / "api-keys.json")
    ctx.command(["snapcraft", "clean"], cwd=snapshot)
    ctx.command(["snapcraft", "pack"], cwd=snapshot)
    expected = snapshot / f"revelation-x_{ctx.job['version']}.{ctx.job['build']}_amd64.snap"
    if not expected.is_file():
        raise ReleaseError("Snapcraft did not produce the expected amd64 package")
    destination = package_path(ctx, ".snap")
    if destination.exists() and digest(destination) != digest(expected):
        from ..core import read_json
        manifest_path = ctx.directory / "manifest.json"
        pending = read_json(manifest_path).get("unverified_packages", {}).get(destination.name, {}) if manifest_path.exists() else {}
        if pending.get("sha256") != digest(destination) or not pending.get("source_asset_id"):
            raise ReleaseError("Existing local Snap differs; preserve it and reconcile the catalogue")
        # Its exact previous bytes are already backed up in the owned draft.
        expected.replace(destination)
        return
    if destination.exists():
        expected.unlink()
    else:
        expected.replace(destination)


def build(ctx):
    failures = []
    def attempt(name, action, outputs=()):
        try:
            ctx.stage(name, action, outputs)
            return True
        except (ReleaseError, OSError) as error:
            from ..processes import JobStopped
            if isinstance(error, JobStopped):
                raise
            failures.append(name)
            print(ctx.redact(f"FAILED {name}: {error}"), flush=True)
            return False
    if not (ctx.workspace / "build/linux/x64/release/bundle/revelation").is_file():
        ctx.result["steps"].pop("linux", None)
    native = attempt("linux", lambda: ctx.command(["flutter", "build", "linux", "--release", "--target=lib/main.dart", "--dart-define-from-file=api-keys.json"]))
    if native:
        attempt("sentry-linux", lambda: ctx.command(["dart", "run", "sentry_dart_plugin", "--sentry-define=upload_source_maps=false"]))
        def archive():
            with tarfile.open(package_path(ctx, ".tar.gz"), "w:gz") as output:
                output.add(ctx.workspace / "build/linux/x64/release/bundle", arcname=".")
        if attempt("linux-tar", archive, ["packages/" + package_path(ctx, ".tar.gz").name]):
            attempt("inspect-linux-tar", lambda: inspect_tar(ctx), ["results/linux-tar-package.json"])
    if attempt("snap", lambda: build_snap(ctx), ["packages/" + package_path(ctx, ".snap").name]):
        attempt("inspect-snap", lambda: inspect_snap(ctx), ["results/linux-snap-package.json"])
    def acceptance():
        script, expected = ctx.config.get("snap_verify_script"), ctx.config.get("snap_verify_script_sha256")
        if not script or not expected or digest(Path(script)) != expected:
            raise ReleaseError("Snap install/smoke/restore approval script is not configured; private packages remain available")
        ctx.command(["bash", str(Path(script).resolve())], env={"LOCAL_RELEASE_SNAP_OUTPUT": str(package_path(ctx, ".snap"))})
        atomic_json(ctx.directory / "results/linux-packages.json", {"snap": "install/smoke/restore passed", "verify_script_sha256": expected})
    if not failures:
        attempt("verify-linux", acceptance, ["results/linux-packages.json"])
    if failures:
        raise ReleaseError("Linux stages remain incomplete: " + ", ".join(failures))
