"""Stable graphical-login entrypoint; update main before loading job dispatch code."""

import os
import sys

# Load the guard from source before importing potentially damaged .pyc files.
_guard = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      'tools', 'local_release', 'python_bootstrap.py')
with open(_guard, 'rb') as _source:
    exec(compile(_source.read(), _guard, 'exec'), {'__name__': '_ai11_python_startup'})

import argparse
from pathlib import Path
import subprocess

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
        from local_release.host_reports import report_failure
        report_failure({'project': 'revelation', 'profile': str(REPO / 'scripts/local_release/revelation.json'),
                        'config': str(Path.home() / '.config/ai11-local-release/revelation.json'),
                        'catalogue': str(REPO / '.local-releases')}, error, phase='git-update')
        print(f"Startup failed: {error}", flush=True)
    finally:
        if args.hold and sys.stdin.isatty():
            input("\nFinished. You may reboot to Windows, or press Enter to close this terminal. ")
    return code


if __name__ == "__main__":
    sys.exit(main())
