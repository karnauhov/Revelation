import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json
from local_release.profiles.linux_release import inspect_tar


class LinuxPolicyTest(unittest.TestCase):
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
            subprocess.run([cmake, "-S", str(root), "-B", str(root / "build")], capture_output=True, check=True)
            installed = (root / "build/cmake_install.cmake").read_text()
            self.assertRegex(installed, r'TYPE PROGRAM FILES "[^"\n]*/crashpad_handler"')
            self.assertRegex(installed, r'TYPE FILE FILES "[^"\n]*/libfixture.so"')


if __name__ == "__main__":
    unittest.main()
