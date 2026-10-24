"""python -B -m scripts.bible_module.precision78 COMMAND."""
import sys

from . import io

command = sys.argv[1]
if command == "preflight":
    io.preflight()
elif command == "lock":
    io.lock()
elif command in {"feasibility", "taxonomy"}:
    from . import analysis
    getattr(analysis, command)(io.checked_paths())
elif command == "preservation":
    print(io.canonical(io.preservation(io.SESSION / "baseline_inventory.json")))
else:
    raise ValueError("Unknown command")
