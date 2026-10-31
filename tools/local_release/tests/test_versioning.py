from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import ReleaseError, atomic_json, capture, git
from local_release.versioning import install, remove


class VersioningTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo with spaces"
        self.repo.mkdir()
        capture(["git", "init", self.repo])
        git(self.repo, "config", "user.name", "Fixture")
        git(self.repo, "config", "user.email", "fixture@example.invalid")
        git(self.repo, "config", "core.autocrlf", "false")
        helper = self.repo / "helper.py"
        source = Path(__file__).resolve().parents[3] / ".agents/skills/revelation/scripts/update_release_version.py"
        shutil.copy2(source, helper)
        (self.repo / "pubspec.yaml").write_text("version: 1.0.8+173\nmsix_version: 1.0.181.0\n")
        (self.repo / "setup.iss").write_text('#define MyAppVersion "1.0.8"\n#define MyAppBuild "173"\n')
        (self.repo / "snap/gui").mkdir(parents=True)
        (self.repo / "snap/snapcraft.yaml").write_text("version: '1.0.8.173'\n")
        (self.repo / "snap/gui/revelation-x.desktop").write_text("Version=1.0.8.173\n")
        self.profile = self.repo / "profile.json"
        atomic_json(self.profile, {"versioning": {"helper": "helper.py", "files": ["pubspec.yaml", "setup.iss", "snap/snapcraft.yaml", "snap/gui/revelation-x.desktop"]}})
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "baseline")
        install(self.repo, self.profile)

    def build(self):
        return git(self.repo, "show", "HEAD:pubspec.yaml")

    def test_normal_commit_contains_one_synchronized_increment(self):
        git(self.repo, "commit", "--allow-empty", "-m", "normal")
        self.assertIn("1.0.8+174", self.build())
        self.assertIn("1.0.182.0", self.build())
        self.assertEqual(git(self.repo, "rev-list", "--count", "HEAD"), "2")
        self.assertIn("174", git(self.repo, "show", "HEAD:setup.iss"))
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_skip_in_title_or_body_does_not_increment(self):
        for message in ("[skip ci] maintenance", "maintenance\n\n[skip ci]"):
            git(self.repo, "commit", "--allow-empty", "-m", message)
            self.assertIn("1.0.8+173", self.build())

    def test_failed_signing_retry_does_not_increment_twice(self):
        with self.assertRaises(ReleaseError):
            git(self.repo, "-c", "commit.gpgsign=true", "-c", "gpg.program=false", "commit", "--allow-empty", "-m", "signing failure")
        self.assertIn("1.0.8+174", (self.repo / "pubspec.yaml").read_text())
        git(self.repo, "-c", "commit.gpgsign=false", "commit", "-m", "retry")
        self.assertIn("1.0.8+174", self.build())

    def test_unstaged_version_edit_is_not_overwritten(self):
        path = self.repo / "pubspec.yaml"
        path.write_text(path.read_text() + "# owner edit\n")
        with self.assertRaises(ReleaseError):
            git(self.repo, "commit", "--allow-empty", "-m", "normal")
        self.assertTrue(path.read_text().endswith("# owner edit\n"))
        self.assertIn("1.0.8+173", self.build())

    def test_skip_retry_after_failed_signing_restores_automatic_increment(self):
        with self.assertRaises(ReleaseError):
            git(self.repo, "-c", "commit.gpgsign=true", "-c", "gpg.program=false", "commit", "--allow-empty", "-m", "signing failure")
        git(self.repo, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "retry [skip ci]")
        self.assertIn("1.0.8+173", self.build())
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_removal_restores_owner_hook_and_install_is_idempotent(self):
        remove(self.repo)
        directory = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        hook = directory / "commit-msg"
        owner = "#!/bin/sh\nexit 9\n"
        hook.write_text(owner)
        hook.chmod(0o755)
        install(self.repo, self.profile)
        install(self.repo, self.profile)
        with self.assertRaises(ReleaseError):
            git(self.repo, "commit", "--allow-empty", "-m", "normal")
        self.assertIn("1.0.8+173", (self.repo / "pubspec.yaml").read_text())
        remove(self.repo)
        self.assertEqual(hook.read_text(), owner)


if __name__ == "__main__":
    unittest.main()
