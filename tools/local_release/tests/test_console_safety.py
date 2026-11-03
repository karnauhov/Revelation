import os
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release import console_safety
from local_release.core import ReleaseError


@unittest.skipUnless(os.name == 'nt', 'native Windows console safety gate')
class ConsoleSafetyTest(unittest.TestCase):
    def test_observer_scopes_events_to_the_owned_process_tree(self):
        self.assertTrue(console_safety._is_descendant(os.getpid(), {os.getpid()}))
        self.assertFalse(console_safety._is_descendant(os.getpid(), {0}))
        from local_release.core import hidden_flags
        from local_release.processes import terminate_tree
        code = ('import subprocess,sys,time; '
                'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(10)"],'
                'creationflags=subprocess.CREATE_NO_WINDOW); print(p.pid,flush=True); time.sleep(10)')
        child = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.PIPE,
            text=True, creationflags=hidden_flags())
        try:
            grandchild = int(child.stdout.readline())
            self.assertTrue(console_safety._is_descendant(child.pid, {os.getpid()}))
            self.assertTrue(console_safety._is_descendant(grandchild, {os.getpid()}))
            self.assertFalse(console_safety._is_descendant(grandchild, {0}))
        finally:
            terminate_tree(child)
            child.wait(timeout=10)
            child.stdout.close()

    def test_unsafe_primitive_is_rejected_without_starting_any_process(self):
        with patch.object(console_safety, '_verified', None), \
                patch('local_release.core.cli_launch_options', return_value={}), \
                patch.object(console_safety.subprocess, 'Popen') as launch:
            with self.assertRaisesRegex(ReleaseError, 'Unsafe console creation policy'):
                console_safety.verify_console_safety()
            launch.assert_not_called()

    def test_repeated_native_descendants_never_show_or_steal_focus(self):
        with patch.object(console_safety, '_verified', None):
            result = console_safety.verify_console_safety()
        self.assertTrue(result['passed'])
        self.assertEqual(result['nested_cycles'], 24)
        self.assertEqual(result['visible_consoles'], 0)
        self.assertEqual(result['transient_show_events'], 0)
        self.assertEqual(result['foreground_steals'], 0)


if __name__ == '__main__':
    unittest.main()
