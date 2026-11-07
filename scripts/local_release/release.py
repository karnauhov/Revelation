"""Revelation entrypoint to the shared AI11 release coordinator."""
import os
from pathlib import Path
import runpy

engine = Path(os.environ.get('AI11_LOCAL_RELEASE_ENGINE',
    str(Path(__file__).resolve().parents[3] / 'ai11/tools/local_release')))
if not (engine / 'cli.py').is_file():
    raise SystemExit('Shared local release engine is missing: ' + str(engine))
if __name__ == '__main__':
    runpy.run_path(str(engine / 'cli.py'), run_name='__main__')
