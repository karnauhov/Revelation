import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import capture, git
from local_release.profiles.revelation import quality_steps


class WorkflowGuardTest(unittest.TestCase):
    def test_quality_guard_depends_on_committed_snapshot_not_working_tree(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            capture(["git", "init", root])
            git(root, "config", "user.name", "Fixture")
            git(root, "config", "user.email", "fixture@example.invalid")
            git(root, "commit", "--allow-empty", "-m", "historical source")
            old = git(root, "rev-parse", "HEAD")
            script = root / "scripts/local_release/inventory.py"
            script.parent.mkdir(parents=True)
            script.write_text("fixture")
            git(root, "add", ".")
            git(root, "commit", "-m", "coordinator source")
            self.assertNotIn("workflow-parity", quality_steps(root, old))
            self.assertIn("workflow-parity", quality_steps(root, "HEAD"))

    def test_cutover_keeps_legacy_parity_but_detects_workflow_reintroduction(self):
        script = Path(__file__).resolve().parents[3] / "scripts/local_release/inventory.py"
        spec = importlib.util.spec_from_file_location("workflow_inventory_fixture", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = capture(["git", "-C", script.parents[2], "cat-file", "blob", module.LEGACY_WORKFLOW_BLOB]) + "\n"
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            workflow = root / ".github/workflows/flutter_build.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(original, encoding="utf-8")
            with patch.object(module, "ROOT", root):
                before = module.inventory()
                workflow.unlink()
                with patch.object(module.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=original)):
                    after = module.inventory()
                self.assertFalse(after["hosted_workflow_present"])
                self.assertEqual(before["jobs"], after["jobs"])
                self.assertEqual(after["git_blob"], module.LEGACY_WORKFLOW_BLOB)
                workflow.write_text(original, encoding="utf-8")
                self.assertNotEqual(module.inventory(), after)
