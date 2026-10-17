"""Isolated stage7.7 diagnostic calibration, using only Python stdlib."""
from __future__ import annotations

import argparse
from pathlib import Path

from .io import canonical, protocol_lock
from .pipeline import develop, freeze, prefit_support, skip_test4, validate


def main():
    parser = argparse.ArgumentParser(description="Stage7.7 fixed diagnostic calibration; NO_GO blocks acceptance/test4")
    parser.add_argument("command", choices=["support", "protocol-lock", "develop", "freeze", "validate3", "skip-test4"])
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    for flag in ("protocol", "preflight", "support", "build", "freeze", "validation", "out"):
        parser.add_argument("--" + flag, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    needed = {"support": ("out", "preflight"), "protocol-lock": ("out", "preflight", "support"),
              "develop": ("protocol", "out"), "freeze": ("protocol", "build", "out"),
              "validate3": ("freeze", "out"), "skip-test4": ("freeze", "validation", "out")}[args.command]
    if any(getattr(args, name) is None for name in needed):
        parser.error("Required for command: " + ", ".join("--" + n for n in needed))
    values = {name: getattr(args, name).resolve() for name in needed}
    if args.command == "support":
        result = prefit_support(repo, **values)
    elif args.command == "protocol-lock":
        result = protocol_lock(repo, **values)
    elif args.command == "develop":
        result = develop(repo, values["protocol"], values["out"])
    elif args.command == "freeze":
        result = freeze(repo, values["protocol"], values["build"], values["out"])
    elif args.command == "validate3":
        result = validate(repo, values["freeze"], values["out"])
    else:
        result = skip_test4(repo, values["freeze"], values["validation"], values["out"])
    print(canonical({"status": "PASS", "artifact": result["artifact"], "certification_status": result.get("certification_status", "NO_GO")}))


if __name__ == "__main__":
    main()
