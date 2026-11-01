"""Real truncated bytecode reproducer, with no changes to owner/system caches."""

import importlib.util
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from local_release.core import hidden_flags


class PythonBootstrapTest(unittest.TestCase):
    def test_source_guard_bypasses_truncated_package_cache_where_B_alone_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = Path(__file__).resolve().parents[3]
            source = project / 'tools/local_release'
            target = root / 'tools/local_release'
            shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', 'tests'))
            (root / 'scripts').mkdir()
            shutil.copytree(project / 'scripts/local_release', root / 'scripts/local_release',
                            ignore=shutil.ignore_patterns('__pycache__'))
            poisoned = []
            for module in ('__init__.py', 'core.py', 'agent.py'):
                path = target / module
                old = sys.pycache_prefix
                try:
                    sys.pycache_prefix = None
                    cache = Path(importlib.util.cache_from_source(str(path)))
                finally:
                    sys.pycache_prefix = old
                py_compile.compile(str(path), cfile=str(cache), doraise=True,
                                   invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
                cache.write_bytes(cache.read_bytes()[:16] + b'\xe3')
                poisoned.append((cache, cache.read_bytes()))
            environment = dict(os.environ)
            environment.pop('PYTHONPYCACHEPREFIX', None)
            environment['PYTHONPATH'] = str(root / 'tools')
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            def run(arguments):
                return subprocess.run([sys.executable, '-B', *map(str, arguments)], cwd=root,
                    env=environment, capture_output=True, text=True, creationflags=hidden_flags(), timeout=30)
            failure = run(['-c', 'import local_release.core'])
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn('marshal data too short', failure.stderr)
            for entry in ('scripts/local_release/release.py', 'scripts/local_release/linux_bootstrap.py',
                          'scripts/local_release/agent_bootstrap.py', 'tools/local_release/cli.py'):
                with self.subTest(entry=entry):
                    result = run([root / entry, '--help'])
                    self.assertEqual(result.returncode, 0, result.stderr)
            # No broad cleanup: unrelated bytecode remains byte-identical and no
            # replacement cache directory is created by the guarded processes.
            for cache, original in poisoned:
                self.assertEqual(cache.read_bytes(), original)
            self.assertEqual(len(list(target.rglob('*.pyc'))), len(poisoned))


if __name__ == '__main__':
    unittest.main()
