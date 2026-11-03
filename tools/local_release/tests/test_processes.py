from pathlib import Path
import os
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import Context, atomic_json, read_json, hidden_flags, cli_launch_options
from local_release.processes import JobStopped


class ProcessControlTest(unittest.TestCase):
    def test_restore_command_finishes_with_stop_requested_without_losing_request(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder) / "releases/fixture/1.0.0+1" / ("a" * 40)
            atomic_json(job / "job.json", {"schema": 1, "sha": "a" * 40, "run_id": "fixture-a", "project": "fixture"})
            ctx = Context(job, {})
            ctx.workspace.mkdir(parents=True)
            atomic_json(job / "stop-request.json", {"action": "stop"})
            output = ctx.command([sys.executable, "-c", "import time; time.sleep(.6); print('restored')"], cancellable=False)
            self.assertEqual(output.strip(), "restored")
            self.assertTrue((job / "stop-request.json").exists())

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
    def test_pythonw_cli_tree_inherits_console_hidden_from_creation(self):
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
setup="k=ctypes.windll.kernel32; k.GetConsoleWindow.restype=ctypes.c_void_p; h=k.GetConsoleWindow(); data={'console':h,'visible':bool(ctypes.windll.user32.IsWindowVisible(ctypes.c_void_p(h or 0))),'pid':os.getpid()}"
probe="import ctypes,json,os; "+setup+"; print(json.dumps(data))"
code="import ctypes,json,os,subprocess,sys; "+setup+"; probe="+repr(probe)+"; rows=[json.loads(subprocess.check_output([sys.executable,'-c',probe],text=True)) for _ in range(12)]; print(json.dumps({'rows':rows,'parent':data,'executable':sys.executable}))"
captured=capture([str(Path(sys.executable).with_name('python.exe')),'-c',code])
job=Path(sys.argv[1])/'releases/fixture/1.0.0+1'/('a'*40)
atomic_json(job/'job.json',{'schema':1,'sha':'a'*40,'run_id':'fixture-a','project':'fixture'})
ctx=Context(job,{})
ctx.workspace.mkdir(parents=True)
ctx.result['current_step']='silent-check'
command=ctx.command(['python','-c',code])
atomic_json(Path(sys.argv[1])/'result.json',{'capture':__import__('json').loads(captured),'builder':__import__('json').loads(command)})
'''.replace("TOOLS", repr(tools)))
            process = subprocess.Popen([str(pythonw), str(script), str(root)], creationflags=hidden_flags())
            self.assertEqual(process.wait(timeout=30), 0)
            for mode in read_json(result).values():
                self.assertEqual(Path(mode['executable']).name.lower(), 'python.exe')
                self.assertFalse(mode['parent']['visible'])
                self.assertTrue(mode['parent']['console'])
                self.assertEqual(len(mode['rows']), 12)
                self.assertTrue(all(not row['visible'] for row in mode['rows']))
                self.assertTrue(all(row['console'] == mode['parent']['console'] for row in mode['rows']))

    @unittest.skipUnless(os.name == "nt", "Windows process creation policy")
    def test_cli_console_is_hidden_at_creation_not_after_launch(self):
        options = cli_launch_options()
        self.assertEqual(options['creationflags'], subprocess.CREATE_NEW_CONSOLE)
        self.assertFalse(options['creationflags'] & subprocess.CREATE_NO_WINDOW)
        self.assertTrue(options['startupinfo'].dwFlags & subprocess.STARTF_USESHOWWINDOW)
        self.assertEqual(options['startupinfo'].wShowWindow, subprocess.SW_HIDE)


if __name__ == "__main__":
    unittest.main()
