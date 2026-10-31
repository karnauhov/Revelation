from pathlib import Path
import sys
import os
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError
from local_release.native_fixture import installed_modules, MODULES


class NativeFixtureTest(unittest.TestCase):
    def test_failed_test_restores_original_modules_preferences_and_absent_files(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            workspace = base / "source"
            source = workspace / "web/db"
            source.mkdir(parents=True)
            for name in MODULES:
                (source / name).write_text("candidate " + name)
            documents = base / "documents"
            db = documents / "revelation/db"
            db.mkdir(parents=True)
            original = db / MODULES[0]
            original.write_bytes(b"original database")
            preferences = base / "preferences.json"
            preferences.write_bytes(b"original preferences")
            backup = base / "backup"
            with self.assertRaisesRegex(RuntimeError, "failed scenario"):
                with installed_modules(workspace, backup, documents=documents, preferences=preferences, running_probe=lambda: False):
                    self.assertEqual(original.read_text(), "candidate " + MODULES[0])
                    preferences.write_text("test preferences")
                    raise RuntimeError("failed scenario")
            self.assertEqual(original.read_bytes(), b"original database")
            self.assertEqual(preferences.read_bytes(), b"original preferences")
            self.assertFalse((db / MODULES[1]).exists())
            self.assertFalse(backup.exists())

    def test_open_owner_app_prevents_any_fixture_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            with self.assertRaisesRegex(ReleaseError, "already open"):
                with installed_modules(base / "source", base / "backup", documents=base / "documents", running_probe=lambda: True):
                    self.fail("fixture started")
            self.assertEqual(list(base.iterdir()), [])

    def test_identical_module_is_still_protected_if_test_changes_it(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "source/web/db"
            source.mkdir(parents=True)
            db = base / "documents/revelation/db"
            db.mkdir(parents=True)
            for name in MODULES:
                (source / name).write_bytes(b"same initial module")
                (db / name).write_bytes(b"same initial module")
            original = db / MODULES[0]
            os.utime(original, ns=(1_600_000_000_000_000_000, 1_600_000_000_000_000_000))
            timestamp = original.stat().st_mtime_ns
            with installed_modules(base / "source", base / "backup", documents=base / "documents",
                                   preferences=base / "prefs", running_probe=lambda: False):
                original.write_bytes(b"test update")
            self.assertEqual(original.read_bytes(), b"same initial module")
            self.assertEqual(original.stat().st_mtime_ns, timestamp)


if __name__ == "__main__":
    unittest.main()
