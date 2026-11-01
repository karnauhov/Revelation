"""Revelation entrypoint to the shared coordinator."""

import os
import sys

# Load the guard from source before importing potentially damaged .pyc files.
_guard = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      'tools', 'local_release', 'python_bootstrap.py')
with open(_guard, 'rb') as _source:
    exec(compile(_source.read(), _guard, 'exec'), {'__name__': '_ai11_python_startup'})

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from local_release.cli import main
from local_release.core import ReleaseError


if __name__ == "__main__":
    try:
        main()
    except (ReleaseError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
