"""Versioned stdlib command interface; outputs stay in the requested work area."""
from __future__ import annotations

import argparse
from pathlib import Path

from .core import build, validate_build
from .evaluation import evaluate
from .io import canonical, freeze, lock_inputs


def main():
    parser = argparse.ArgumentParser(description="Stage 7.6 candidate-only consensus and lexical prior")
    parser.add_argument("command", choices=["lock-inputs", "build", "validate", "freeze", "evaluate"])
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--build", type=Path)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--folds", default="0,1,2")
    parser.add_argument("--review-gate", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.command == "lock-inputs":
        result = lock_inputs(repo, args.out.resolve())
        print(canonical({"status": "PASS", "dependencies": len(result["dependencies"])}))
    elif args.command == "build":
        result = build(repo, args.inputs.resolve(), args.out.resolve())
        print(canonical({"status": "PASS", "counts": result["counts"]}))
    elif args.command == "validate":
        print(canonical(validate_build(repo, args.inputs.resolve(), args.build.resolve())))
    elif args.command == "freeze":
        result = freeze(repo, args.inputs.resolve(), args.build.resolve(), args.out.resolve())
        print(canonical({"status": "PASS", "source_files": len(result["source"]), "runtime_files": len(result["runtime"])}))
    else:
        result = evaluate(repo, args.freeze.resolve(), {int(v) for v in args.folds.split(",")}, args.out.resolve(), args.review_gate)
        print(canonical({"status": "PASS", "folds": result["folds"], "support": result["support"], "metrics": result["metrics"]["all"]}))


if __name__ == "__main__":
    main()
