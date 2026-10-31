"""Stable graphical-login entrypoint; update main before loading job dispatch code."""

import argparse
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))


def main():
    from local_release.agent import registry_path, open_linux_terminal, update_main
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=registry_path())
    parser.add_argument("--terminal", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--hold", action="store_true")
    args = parser.parse_args()
    if args.terminal:
        open_linux_terminal(Path(__file__).resolve(), args.registry)
        return 0
    code = 1
    try:
        update_main({"repo": str(REPO)})
        code = subprocess.run([sys.executable, str(REPO / "scripts/local_release/linux_bootstrap.py"),
                               "--registry", str(args.registry)], check=False).returncode
    except Exception as error:
        print(f"Startup failed: {error}", flush=True)
    finally:
        if args.hold and sys.stdin.isatty():
            input("\nFinished. You may reboot to Windows, or press Enter to close this terminal. ")
    return code


if __name__ == "__main__":
    sys.exit(main())
