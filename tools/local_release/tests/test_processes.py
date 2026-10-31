from pathlib import Path
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, atomic_json, read_json, hidden_flags
from local_release.processes import JobStopped


class ProcessControlTest(unittest.TestCase):
    def test_stop_interrupts_silent_owned_process_without_stopping_another_process(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {})
            ctx.workspace.mkdir(parents=True)
            other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], creationflags=hidden_flags())
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

    @unittest.skipUnless(os.name == "nt", "Windows GUI-parent console regression")
    def test_pythonw_background_children_never_allocate_a_console(self):
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        self.assertTrue(pythonw.is_file())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = root / "gui-parent.py"
            result = root / "result.json"
            tools = str(Path(__file__).resolve().parents[2])
            script.write_text('''import sys
from pathlib import Path
sys.path.insert(0, TOOLS)
from local_release.core import Context, atomic_json, capture
code="import ctypes; print(ctypes.windll.kernel32.GetConsoleWindow())"
captured=capture([str(Path(sys.executable).with_name('python.exe')),'-c',code])
job=Path(sys.argv[1])/'releases/fixture/1.0.0+1'/('a'*40)
atomic_json(job/'job.json',{'schema':1,'sha':'a'*40,'run_id':'fixture-a','project':'fixture'})
ctx=Context(job,{})
ctx.workspace.mkdir(parents=True)
ctx.result['current_step']='silent-check'
command=ctx.command([str(Path(sys.executable).with_name('python.exe')),'-c',code])
atomic_json(Path(sys.argv[1])/'result.json',{'capture_console':int(captured),'builder_console':int(command)})
'''.replace("TOOLS", repr(tools)))
            process = subprocess.Popen([str(pythonw), str(script), str(root)], creationflags=hidden_flags())
            self.assertEqual(process.wait(timeout=15), 0)
            self.assertEqual(read_json(result), {"capture_console": 0, "builder_console": 0})


if __name__ == "__main__":
    unittest.main()
