import argparse

from . import build

parser = argparse.ArgumentParser(description="Frozen OH1988 development manual review")
parser.add_argument("command", choices=("lock", "build", "serve"))
parser.add_argument("--port", type=int, default=8878)
args = parser.parse_args()
if args.command == "serve":
    from .server import serve
    serve(port=args.port)
else:
    getattr(build, args.command)()
