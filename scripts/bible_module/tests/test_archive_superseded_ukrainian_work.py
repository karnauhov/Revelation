from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.bible_module import archive_superseded_ukrainian_work as cleanup


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.work = self.root / "work"
        for name in cleanup.DIRECTORIES:
            path = self.work / name
            path.mkdir(parents=True)
            (path / "test.jsonl").write_bytes((name + "\n").encode() * 3)
        self.archive = self.root / "backup.zip"
        self.receipt = self.root / "backup.json"

    def test_verified_archive_restores_exact_bytes_and_preserves_canonical_work(self):
        canonical = self.work / "ukrainian_stage_7_20260801"
        canonical.mkdir()
        (canonical / "keep").write_bytes(b"canonical evidence")
        originals = {p.relative_to(self.work).as_posix(): p.read_bytes()
                     for _, files in [cleanup.selected_files(self.work)] for p in files}
        result = cleanup.archive_and_remove(self.work, self.archive, self.receipt)
        self.assertEqual(result["status"], "archived_and_removed")
        self.assertEqual((canonical / "keep").read_bytes(), b"canonical evidence")
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual({name: archive.read(name) for name in archive.namelist()}, originals)
            archive.extractall(self.work)
        self.assertEqual({name: (self.work / name).read_bytes() for name in originals}, originals)

    def test_verification_failure_preserves_all_sources(self):
        with patch.object(cleanup.zipfile.ZipFile, "namelist", return_value=[]):
            with self.assertRaises(ValueError):
                cleanup.archive_and_remove(self.work, self.archive, self.receipt)
        self.assertFalse(self.archive.exists())
        self.assertEqual(len(cleanup.selected_files(self.work)[1]), 2)

    def test_archive_inside_work_and_existing_archive_are_rejected(self):
        with self.assertRaises(ValueError):
            cleanup.archive_and_remove(self.work, self.work / "backup.zip", self.receipt)
        self.archive.write_bytes(b"earlier backup")
        with self.assertRaises(FileExistsError):
            cleanup.archive_and_remove(self.work, self.archive, self.receipt)
        self.assertEqual(self.archive.read_bytes(), b"earlier backup")
        self.assertEqual(len(cleanup.selected_files(self.work)[1]), 2)


if __name__ == "__main__":
    unittest.main()
