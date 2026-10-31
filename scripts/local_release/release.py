"""Revelation entrypoint to the shared coordinator."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from local_release.cli import main
from local_release.core import ReleaseError


if __name__ == "__main__":
    try:
        main()
    except (ReleaseError, OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
