"""Bounded Windows snapshot read recovery without hiding invalid state."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import read_json


class SnapshotReadTest(unittest.TestCase):
    def test_transient_windows_replace_handle_is_retried(self):
        path = Path('fixture.json')
        with patch('local_release.core.os.name', 'nt'), patch('local_release.core.time.sleep') as sleep, patch.object(Path, 'read_text', side_effect=[PermissionError(), PermissionError(), '{"status":"complete"}']) as read:
            self.assertEqual(read_json(path), {'status': 'complete'})
            self.assertEqual(read.call_count, 3)
            self.assertEqual(sleep.call_count, 2)

    def test_permanent_permission_denial_is_bounded(self):
        path = Path('fixture.json')
        with patch('local_release.core.os.name', 'nt'), patch('local_release.core.time.sleep') as sleep, patch.object(Path, 'read_text', side_effect=PermissionError()) as read:
            with self.assertRaises(PermissionError):
                read_json(path)
            self.assertEqual(read.call_count, 8)
            self.assertEqual(sleep.call_count, 7)

    def test_non_windows_permission_and_malformed_json_are_not_retried(self):
        path = Path('fixture.json')
        with patch('local_release.core.os.name', 'posix'), patch('local_release.core.time.sleep') as sleep, patch.object(Path, 'read_text', side_effect=PermissionError()):
            with self.assertRaises(PermissionError):
                read_json(path)
            sleep.assert_not_called()
        with patch('local_release.core.time.sleep') as sleep, patch.object(Path, 'read_text', return_value='{invalid'):
            with self.assertRaises(ValueError):
                read_json(path)
            sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
