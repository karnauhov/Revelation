"""First login can transition from the already-loaded pre-migration launcher."""
from pathlib import Path
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT.parent / 'ai11/tools'))
from local_release.core import ReleaseError


class SharedBootstrapTest(unittest.TestCase):
    def test_updated_linux_child_acquires_engine_before_importing_it(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            script = base / 'Revelation/scripts/local_release/linux_bootstrap.py'
            script.parent.mkdir(parents=True)
            shutil.copy2(ROOT / 'scripts/local_release/linux_bootstrap.py', script)
            engine = base / 'ai11/tools/local_release'
            def acquire():
                engine.mkdir(parents=True)
                (engine / 'cli.py').write_text('# shared coordinator')
                (engine / 'python_bootstrap.py').write_text('# source guard fixture')
            namespace = {'__file__': str(script), '__name__': 'first_login_fixture'}
            with patch('runpy.run_path', return_value={'ensure_engine': acquire}) as compatibility, \
                    patch.dict(os.environ, {'AI11_LOCAL_RELEASE_ENGINE': str(engine)}):
                exec(compile(script.read_bytes(), str(script), 'exec'), namespace)
            compatibility.assert_called_once_with(str(script.with_name('agent_bootstrap.py')))
            self.assertTrue((engine / 'cli.py').is_file())
            self.assertEqual(namespace['ENGINE'], engine)


if __name__ == '__main__':
    unittest.main()
