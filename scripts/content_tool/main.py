from __future__ import annotations

import argparse
from pathlib import Path

from .app import TopicContentTool
from .helpers import default_work_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Content of Revelation.")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=default_work_dir(),
        help="Path to folder with SQLite DB files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = TopicContentTool(args.work_dir)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # Gracefully exit when launched from a console and interrupted with Ctrl+C.
        return
