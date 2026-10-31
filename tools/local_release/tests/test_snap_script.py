from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, ReleaseError, atomic_json, capture, git
from local_release.snap_script import QuitGate, flutter_debug, run


class SnapScriptTest(unittest.TestCase):
    def test_q_requires_both_flutter_tool_and_app_startup_and_is_sent_only_once(self):
        gate = QuitGate(delay=5)
        gate.observe("Flutter run key ", 0)
        gate.observe("commands.\r\n", 1)
        self.assertFalse(gate.ready(20))
        gate.observe("Started on TargetPlatform.", 21)
        gate.observe("linux\n", 22)
        self.assertFalse(gate.ready(26))
        self.assertTrue(gate.ready(27))
        self.assertFalse(gate.ready(100))

    def test_original_committed_script_is_executed_whole_and_modified_script_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshot = root / "w/snap-input"
            snapshot.mkdir(parents=True)
            script = snapshot / "snapcraft_build.sh"
            original = "#!/bin/bash\nset -euo pipefail\nrm -rf build\nflutter clean\nflutter pub get\nflutter run -d linux --debug --dart-define-from-file=api-keys.json\nsnapcraft clean\nsnapcraft pack\necho 'Build complete'\n"
            script.write_text(original)
            capture(["git", "init", snapshot])
            git(snapshot, "config", "user.name", "Fixture")
            git(snapshot, "config", "user.email", "fixture@example.invalid")
            git(snapshot, "add", ".")
            git(snapshot, "commit", "-m", "original owner script")
            sha = git(snapshot, "rev-parse", "HEAD")
            directory = root / "releases/fixture/1.0.0+1" / sha
            atomic_json(directory / "job.json", {"schema": 1, "sha": sha, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(directory, {}, host="linux")
            def execute(*args, **kwargs):
                atomic_json(ctx.root / "w" / sha[:12] / "snap-cli/debug-state/result.json", {
                    "exit_code": 0, "automatic_q": True, "startup_observed": True})
            with patch.object(ctx, "command", side_effect=execute) as command, patch("local_release.snap_script.shutil.which", return_value="/sdk/bin/flutter"):
                run(ctx, snapshot)
                argv = command.call_args.args[0]
                self.assertEqual(argv, ["bash", str(script)])
                self.assertEqual(command.call_args.kwargs["cwd"], snapshot)
                self.assertEqual(script.read_text(), original)
                self.assertTrue((directory / "results/linux-snap-script.json").exists())
                script.write_text(original.replace("flutter clean\n", ""))
                with self.assertRaisesRegex(ReleaseError, "differs"):
                    run(ctx, snapshot)
                self.assertEqual(command.call_count, 1)

    @unittest.skipUnless(sys.platform == "linux", "Requires a native Linux PTY")
    def test_real_pty_debug_session_receives_q_and_exits(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "flutter"
            fixture.write_text("#!/usr/bin/env python3\nimport sys,tty\ntty.setraw(sys.stdin.fileno())\nprint('Flutter run key commands.',flush=True)\nprint('Started on TargetPlatform.linux',flush=True)\nassert sys.stdin.read(1)=='q'\n")
            fixture.chmod(0o755)
            self.assertEqual(flutter_debug([str(fixture)], timeout=15), 0)

    @unittest.skipUnless(sys.platform == "linux", "Requires native Linux process groups")
    def test_hung_debug_session_times_out_and_is_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / "flutter"
            fixture.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(60)\n")
            fixture.chmod(0o755)
            with self.assertRaisesRegex(ReleaseError, "Timed out"):
                flutter_debug([str(fixture)], timeout=.2)
