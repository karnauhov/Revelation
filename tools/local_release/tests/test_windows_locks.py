import ctypes
from ctypes import wintypes as w
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import windows_locks as locks
from local_release.core import ReleaseError, atomic_json, Context
from local_release.retention import safe_remove


class LocksTest(unittest.TestCase):
    def test_only_idle_gradle_owners_can_be_stopped(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jar = root / 'cache.jar'
            owner = {'pid': 123, 'started': 456}
            with patch.object(locks, 'locking_processes', return_value=[owner]), \
                    patch.object(locks, 'process_details', return_value={}), \
                    patch.object(locks, 'idle_gradle', return_value=False), \
                    patch.object(locks, 'stop_same_process') as stop:
                with self.assertRaisesRegex(ReleaseError, 'process preserved'):
                    locks.release_managed_jar(jar, root)
                stop.assert_not_called()
            with patch.object(locks, 'locking_processes', return_value=[owner]), \
                    patch.object(locks, 'process_details', return_value={}), \
                    patch.object(locks, 'idle_gradle', return_value=True), \
                    patch.object(locks, 'stop_same_process') as stop:
                self.assertEqual(locks.release_managed_jar(jar, root), [123])
                stop.assert_called_once_with(owner)
            with self.assertRaisesRegex(ReleaseError, 'limited to JAR'):
                locks.release_managed_jar(root.parent / 'outside.jar', root)

    def test_persistent_daemon_is_disabled_only_for_windows_builders(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / 'releases/fixture/1.0.0+1' / ('a' * 40)
            atomic_json(directory / 'job.json', {'schema': 1, 'sha': 'a' * 40, 'run_id': 'fixture', 'project': 'fixture'})
            config = {'environment': {'GRADLE_OPTS': '-Xmx2g'}}
            windows = Context(directory, config, host='windows')
            self.assertEqual(windows.env['GRADLE_OPTS'], '-Xmx2g -Dorg.gradle.daemon=false')
            linux = Context(directory, config, host='linux')
            self.assertEqual(linux.env['GRADLE_OPTS'], '-Xmx2g')

    @unittest.skipUnless(os.name == 'nt', 'Windows real sharing lock and process identity')
    def test_real_non_gradle_lock_and_reused_pid_are_preserved_then_retry_succeeds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'w' / ('a' * 12)
            target.mkdir(parents=True)
            jar = target / 'cache.jar'
            jar.write_bytes(b'fixture')
            keep = root / 'keep.txt'
            keep.write_text('neighbour')
            code = """import ctypes,sys,time
from ctypes import wintypes as w
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,w.LPVOID,w.DWORD,w.DWORD,w.HANDLE]
k.CreateFileW.restype=w.HANDLE
h=k.CreateFileW(sys.argv[1],0x80000000,1,None,3,0,None)
assert h not in (None,ctypes.c_void_p(-1).value)
print('locked',flush=True)
time.sleep(60)
"""
            child = subprocess.Popen([sys.executable, '-c', code, str(jar)], stdout=subprocess.PIPE,
                                     text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                self.assertEqual(child.stdout.readline().strip(), 'locked')
                owner = next(o for o in locks.locking_processes(jar) if o['pid'] == child.pid)
                with self.assertRaisesRegex(ReleaseError, 'PID was reused'):
                    locks.stop_same_process({**owner, 'started': owner['started'] + 1})
                with self.assertRaisesRegex(ReleaseError, 'process preserved'):
                    safe_remove(root, target, Path('w') / ('a' * 12))
                self.assertIsNone(child.poll())
                self.assertTrue(jar.exists())
                self.assertEqual(keep.read_text(), 'neighbour')
            finally:
                child.terminate()
                child.wait(timeout=10)
                child.stdout.close()
            safe_remove(root, target, Path('w') / ('a' * 12))
            self.assertFalse(target.exists())
            self.assertEqual(keep.read_text(), 'neighbour')
