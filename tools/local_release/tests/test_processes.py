from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, atomic_json
from local_release.processes import JobStopped


class ProcessControlTest(unittest.TestCase):
    def test_stop_interrupts_silent_owned_process_without_stopping_another_process(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {})
            ctx.workspace.mkdir(parents=True)
            other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
            def stop():
                time.sleep(0.5)
                atomic_json(job / "stop-request.json", {"action": "stop"})
            thread = threading.Thread(target=stop)
            thread.start()
            try:
                started = time.monotonic()
                with self.assertRaises(JobStopped):
                    ctx.stage("silent-build", lambda: ctx.command([sys.executable, "-c", "import time; time.sleep(60)"]))
                self.assertLess(time.monotonic() - started, 10)
                self.assertIsNone(other.poll())
                self.assertEqual(ctx.result["status"], "stopped")
            finally:
                other.terminate()
                other.wait()
                thread.join()


if __name__ == "__main__":
    unittest.main()
