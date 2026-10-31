import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, hidden_flags
from local_release.profiles.linux_release import inspect_tar, unsquashfs_version


class LinuxPolicyTest(unittest.TestCase):
    def test_repaired_snap_replaces_one_local_package_only_with_a_remote_backup(self):
        from local_release.profiles.linux_release import build_snap
        from local_release.core import digest, read_json
        for backed_up in (False, True):
            with self.subTest(backed_up=backed_up), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                job = root / "releases/fixture/1.0.0+1" / ("a" * 40)
                atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture",
                    "version": "1.0.0", "build": 1, "artifacts": ["fixture.snap"]})
                ctx = Context(job, {}, host="linux")
                ctx.workspace.mkdir(parents=True)
                (ctx.workspace / "api-keys.json").write_text('{}')
                snapshot = ctx.root / "w" / ("a" * 12) / "snap-input"
                snapshot.mkdir(parents=True)
                (snapshot / "revelation-x_1.0.0.1_amd64.snap").write_bytes(b"new build using the entire original script")
                destination = ctx.output / "fixture.snap"
                destination.write_bytes(b"old build")
                previous = {"sha256": digest(destination), **({"source_asset_id": 123} if backed_up else {})}
                atomic_json(job / "manifest.json", {"unverified_packages": {"fixture.snap": previous}})
                def script(*args):
                    atomic_json(job / "results/linux-snap-script.json", {"original_script_executed": True})
                with patch("local_release.native_fixture.application_running", return_value=False), \
                        patch("local_release.profiles.linux_release.apply_overlays"), \
                        patch("local_release.profiles.linux_release.git", return_value="a" * 40), \
                        patch("local_release.snap_script.run", side_effect=script), patch.object(ctx, "command"):
                    if backed_up:
                        build_snap(ctx)
                        self.assertEqual(destination.read_bytes(), b"new build using the entire original script")
                        self.assertEqual(read_json(job / "results/linux-snap-script.json")["superseded_package"]["source_asset_id"], 123)
                    else:
                        with self.assertRaisesRegex(ReleaseError, "Existing local Snap differs"):
                            build_snap(ctx)
                        self.assertEqual(destination.read_bytes(), b"old build")

    def test_unsquashfs_version_exit_one_is_valid_only_with_its_banner(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(directory / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(directory, {}, host="linux")
            ctx.workspace.mkdir(parents=True)
            command = ctx.command
            fixture = root / "unsquashfs_fixture.py"
            def invoke(argv, **kwargs):
                self.assertEqual(argv, ["unsquashfs", "-version"])
                return command([sys.executable, str(fixture)], **kwargs)
            with patch.object(ctx, "command", side_effect=invoke):
                for code in (0, 1):
                    fixture.write_text("print('unsquashfs version 4.6.1 (2023/03/25)')\nraise SystemExit(" + str(code) + ")")
                    versions = []
                    ctx.stage("inspect-snap", lambda: versions.append(unsquashfs_version(ctx)), always=True)
                    self.assertEqual(versions, ["4.6.1"])
                    self.assertEqual(ctx.result["steps"]["inspect-snap"]["status"], "passed")
                for content in ("print('broken executable')\nraise SystemExit(1)",
                                "print('unsquashfs version 4.6.1')\nraise SystemExit(2)"):
                    fixture.write_text(content)
                    with self.assertRaises(ReleaseError):
                        ctx.stage("inspect-snap", lambda: unsquashfs_version(ctx), always=True)
                    self.assertEqual(ctx.result["steps"]["inspect-snap"]["status"], "failed")
            with self.assertRaises(ReleaseError):
                command([sys.executable, "-c", "raise SystemExit(1)"])

    def test_linux_preflight_defers_optional_snap_tools_to_their_stages(self):
        from local_release.profiles import revelation
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(directory / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture",
                "profile": {"flutter": "3.47.2"}, "version": "1.0.0", "build": 1, "release_notes": "Fixture"})
            ctx = Context(directory, {}, host="linux")
            def command(argv, **kwargs):
                if argv[0] in ("snapcraft", "unsquashfs"):
                    self.fail("Optional Snap tool blocked native preflight")
                return '{"frameworkVersion":"3.47.2"}' if "--machine" in argv else "fixture"
            with patch("local_release.profiles.linux_release.provision_flutter"), patch("local_release.profiles.linux_release.apply_overlays"), \
                    patch.object(revelation, "collect_snap_history"), patch.object(revelation, "verify_versions"), \
                    patch.object(revelation, "configured_secrets"), patch.object(revelation, "capture", return_value="x86_64"), \
                    patch.object(ctx, "command", side_effect=command), patch.object(revelation.shutil, "which", return_value="available-but-broken"):
                ctx.stage("preflight", lambda: revelation.preflight(ctx))
            self.assertTrue((directory / "results/linux-environment.json").is_file())
            self.assertEqual(ctx.result["steps"]["preflight"]["status"], "passed")

    def test_tar_rejects_the_reported_crashpad_permission_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job = root / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture", "artifacts": ["linux.tar.gz"]})
            ctx = Context(job, {}, host="linux")
            import io
            def make_tar(permission):
                with tarfile.open(ctx.output / "linux.tar.gz", "w:gz") as archive:
                    for name, mode in (("./revelation", 0o755), ("./lib/crashpad_handler", permission), ("./data/flutter_assets/asset", 0o644)):
                        payload = bytearray(64)
                        payload[:4] = b"\x7fELF"
                        payload[18:20] = (62).to_bytes(2, "little")
                        member = tarfile.TarInfo(name)
                        member.size, member.mode = len(payload), mode
                        archive.addfile(member, io.BytesIO(payload))
            make_tar(0o644)
            with self.assertRaisesRegex(ReleaseError, "nonexecutable"):
                inspect_tar(ctx)
            make_tar(0o755)
            inspect_tar(ctx)
            self.assertTrue((job / "results/linux-tar-package.json").is_file())

    def test_cmake_installs_handler_as_program_and_shared_library_as_file(self):
        cmake = shutil.which("cmake")
        if not cmake:
            candidates = list(Path("C:/Program Files/Microsoft Visual Studio/2022").glob("*/Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe"))
            cmake = str(candidates[0]) if candidates else None
        if not cmake:
            self.skipTest("CMake is unavailable")
        text = (Path(__file__).resolve().parents[3] / "linux/CMakeLists.txt").read_text()
        loop = text[text.index("foreach(bundled_library"):text.index("endforeach(bundled_library)") + len("endforeach(bundled_library)")]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "crashpad_handler").write_bytes(b"fixture")
            (root / "libfixture.so").write_bytes(b"fixture")
            recipe = 'cmake_minimum_required(VERSION 3.14)\nproject(permission_fixture NONE)\n'
            recipe += 'set(INSTALL_BUNDLE_LIB_DIR "${CMAKE_BINARY_DIR}/bundle/lib")\n'
            recipe += 'set(PLUGIN_BUNDLED_LIBRARIES "${CMAKE_SOURCE_DIR}/crashpad_handler" "${CMAKE_SOURCE_DIR}/libfixture.so")\n' + loop
            (root / "CMakeLists.txt").write_text(recipe)
            subprocess.run([cmake, "-S", str(root), "-B", str(root / "build")], capture_output=True, check=True, creationflags=hidden_flags())
            installed = (root / "build/cmake_install.cmake").read_text()
            self.assertRegex(installed, r'TYPE PROGRAM FILES "[^"\n]*/crashpad_handler"')
            self.assertRegex(installed, r'TYPE FILE FILES "[^"\n]*/libfixture.so"')


if __name__ == "__main__":
    unittest.main()
