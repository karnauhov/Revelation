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


class AdbCleanupTest(unittest.TestCase):
    def setup_fixture(self,root):
        config={'android_sdk':str(root/'sdk'),'adb_server_port':5043}
        details={'ExecutablePath':str(root/'sdk/platform-tools/adb.exe'),
                 'CommandLine':'fixture','CreationDate':'same-start'}
        args=['adb.exe','-L','tcp:127.0.0.1:5043','fork-server','server']
        return config,details,args

    def test_verified_idle_non_global_adb_server_can_release_a_managed_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);config,details,args=self.setup_fixture(root)
            with patch.object(locks,'adb_server_pid',return_value=123),patch.object(locks,'process_details',return_value=details),patch.object(locks,'command_arguments',return_value=args),patch.object(locks,'capture',side_effect=['List of devices attached','']) as command:
                self.assertTrue(locks.release_idle_project_adb(config,root))
                self.assertEqual(command.call_args_list[-1].args[0][-1],'kill-server')
                self.assertTrue(all(c.kwargs['cwd']==root for c in command.call_args_list))

    def test_global_port_unknown_binary_and_connected_devices_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);config,details,args=self.setup_fixture(root)
            with patch.object(locks,'adb_server_pid') as listener:
                self.assertFalse(locks.release_idle_project_adb(dict(config,adb_server_port=5037),root))
                listener.assert_not_called()
            with patch.object(locks,'adb_server_pid',return_value=123),patch.object(locks,'process_details',return_value=dict(details,ExecutablePath=str(root/'other.exe'))),patch.object(locks,'capture') as command:
                self.assertFalse(locks.release_idle_project_adb(config,root));command.assert_not_called()
            with patch.object(locks,'adb_server_pid',return_value=123),patch.object(locks,'process_details',return_value=details),patch.object(locks,'command_arguments',return_value=args),patch.object(locks,'capture',return_value='List of devices attached\nfixture-phone device') as command:
                with self.assertRaisesRegex(ReleaseError,'server preserved'):locks.release_idle_project_adb(config,root)
                self.assertEqual(command.call_count,1)

    def test_reused_adb_pid_cannot_stop_a_new_server(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);config,details,args=self.setup_fixture(root)
            with patch.object(locks,'adb_server_pid',return_value=123),patch.object(locks,'process_details',side_effect=[details,dict(details,CreationDate='new-start')]),patch.object(locks,'command_arguments',return_value=args),patch.object(locks,'capture',return_value='List of devices attached') as command:
                with self.assertRaisesRegex(ReleaseError,'identity changed'):locks.release_idle_project_adb(config,root)
                self.assertEqual(command.call_count,1)

    @unittest.skipUnless(os.name=='nt' and os.environ.get('AI11_TEST_ADB'),'Explicit owned Windows ADB fixture required')
    def test_real_adb_directory_handle_is_recovered_without_global_server(self):
        import socket
        adb=Path(os.environ['AI11_TEST_ADB']).resolve();sdk=adb.parents[1]
        with tempfile.TemporaryDirectory(prefix='AI11-owned-adb-') as folder:
            root=Path(folder);target=root/'w'/('b'*12);cwd=target/'w';cwd.mkdir(parents=True)
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            self.assertNotEqual(port,5037)
            env=dict(os.environ,ANDROID_ADB_SERVER_PORT=str(port),ADB_SERVER_SOCKET='tcp:127.0.0.1:'+str(port))
            subprocess.run([str(adb),'--one-device','AI11-disposable-fixture','-P',str(port),'start-server'],cwd=cwd,env=env,check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                with self.assertRaises(PermissionError):cwd.rmdir()
                safe_remove(root,target,Path('w')/('b'*12),config={'android_sdk':str(sdk),'adb_server_port':port})
                self.assertFalse(target.exists())
                self.assertIsNone(locks.adb_server_pid(port))
            finally:
                subprocess.run([str(adb),'-P',str(port),'kill-server'],cwd=root,env=env,check=False,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
