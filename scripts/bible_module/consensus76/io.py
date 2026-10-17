"""Strict physical locks and deterministic serialization (stdlib only)."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import sysconfig
from pathlib import Path

from . import VERSION

PACKAGE = Path(__file__).resolve().parent
WORK = Path("scripts/bible_module/work/ukrainian_stage_7_20260801")
REPORT = Path("scripts/bible_module/reports/ukrainian_stage_7_20260801")
GOLD_HASH = "265ac4f336ca6260d211628666a977d7b1805c413b789007cca09afce90a89c9"
ANNOTATION_HASH = "547c67517fa466682b5cfe602cc669fa35f3a0420d813bad3a41670d0e880d67"
MASK_HASH = "d99436f6dedb48c6d7ec99acbaf4631fc009723fdc411851e2dc587e84f844db"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def rows(path):
    with Path(path).open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                raise ValueError(f"Blank JSONL row: {path}:{i}")
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"Non-object JSONL row: {path}:{i}")
            yield row


def write(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(canonical(value) + "\n", encoding="utf-8", newline="\n")


def spec(path, repo=None):
    p = Path(path).resolve()
    return {"path": p.relative_to(repo).as_posix() if repo else str(p),
            "bytes": p.stat().st_size, "sha256": sha(p)}


def verify(item, repo):
    p = Path(item["path"])
    if not p.is_absolute():
        p = repo / p
    if not p.is_file() or p.stat().st_size != item["bytes"] or sha(p) != item["sha256"]:
        raise ValueError("Missing/stale/tampered physical dependency: " + str(p))
    return p


def source_roster():
    result = {p for p in PACKAGE.rglob("*") if p.is_file() and p.suffix in {".py", ".json"}}
    # Python executes parent package initializers before this package's CLI.
    # Namespace ancestors also enter the roster if an initializer is introduced.
    result.update(p / "__init__.py" for p in (PACKAGE.parent, PACKAGE.parent.parent)
                  if (p / "__init__.py").is_file())
    return sorted(result)


def runtime_roster():
    """Lock interpreter, stdlib source and extension binaries, excluding installed packages."""
    paths = {Path(sys.executable).resolve()}
    root = Path(sysconfig.get_path("stdlib")).resolve()
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if "site-packages" in rel.parts or "__pycache__" in rel.parts:
            continue
        if p.is_file() and p.suffix.lower() in {".py", ".pyd", ".dll", ".so", ".zip"}:
            paths.add(p)
    dlls = Path(sys.base_prefix) / "DLLs"
    if dlls.exists():
        paths.update(p for p in dlls.iterdir() if p.is_file() and p.suffix in {".pyd", ".dll"})
    paths.update(p for p in Path(sys.base_prefix).glob("*.dll") if p.is_file())
    return sorted(paths)


def baseline_roster(repo):
    baseline_root = repo / WORK / "session_global_20261017_evaluation_author_01"
    return [baseline_root / f"{name}.evaluation.{partition}.v3" / ("candidate_gold_evaluation.v3" + extension)
            for name in ("fixed", "legacy") for partition in ("unsealed", "sealed") for extension in (".jsonl", ".manifest.json")]


def lock_inputs(repo, out=None):
    gold_path = repo / REPORT / "gold_alignment.finalized.v2.lock.json"
    if sha(gold_path) != GOLD_HASH:
        raise ValueError("Unexpected finalized gold lock")
    gold = read(gold_path)
    dependencies = {entry["path"]: entry for entry in gold["physical_dependencies"]}
    def add_path(p):
        item = spec(p, repo)
        previous = dependencies.get(item["path"])
        if previous is not None and previous != item:
            raise ValueError("Pinned dependency changed: " + item["path"])
        dependencies[item["path"]] = item
    for key in ("annotations", "eligibility", "registry", "manifest"):
        entry = gold[key]
        dependencies[entry["path"]] = entry
    dependencies[str((REPORT / gold_path.name).as_posix())] = spec(gold_path, repo)
    paths = {
        "originals": WORK / "fingerprint_selected_original_layer.jsonl",
        "targets": WORK / "ukrainian_token_inventory.jsonl",
        "source_universe": WORK / "original_token_universe.jsonl",
        "gold_originals": WORK / "gold_selected_original_layer.jsonl",
        "annotations": Path(gold["annotations"]["path"]),
        "mask": Path(gold["eligibility"]["path"]),
        "first_party": WORK / "first_party_candidates/alignment_candidates.first_party.jsonl",
        "statistical": WORK / "statistical_candidates/alignment_candidates.statistical.jsonl",
        "contextual": WORK / "contextual_candidates/alignment_candidates.contextual.jsonl",
    }
    pinned = {"originals": "a2f8b017b702b8217ce4242e2578082f134b615be64968f190c066c0d4692c82",
              "targets": "62caa29ff269c9ca8dad4b64c656728a645b3d09210034ddcc953c5363c567e1",
              "source_universe": "c891e29cedf8ac040418d8f052c94a3d21e2b39ea18ed96f122dc79853899242",
              "gold_originals": "500482d4b1ce58f9749fe9e53b58bf8bce6be1558df926dacfbe0df29cf09ca4",
              "annotations": ANNOTATION_HASH, "mask": MASK_HASH,
              "first_party": "246f3d53af7a6d788cad5707d7fce7e9ccb0d38b2c1f1cd829449c7f3ef9687f",
              "statistical": "5be192bcddadec9699befa554654e0184886b38e1aeae8ef0903439ef0d663ad",
              "contextual": "0e1e90dd1c2ffa2c907861a5eeba551bed00038015a0823ebc673446198a3881"}
    for role, p in paths.items():
        item = spec(repo / p, repo)
        if item["sha256"] != pinned[role]:
            raise ValueError("Pinned input role digest changed: " + role)
        if p.as_posix() in dependencies and dependencies[p.as_posix()] != item:
            raise ValueError("Gold physical dependency conflicts: " + str(p))
        dependencies[p.as_posix()] = item
    for p in (repo / REPORT).glob("*policy*.json"):
        add_path(p)
    for name in ("candidate_generator_registry.json", "source_registry.json", "alignment_candidates.manifest.json",
                 "original_token_universe.manifest.json", "gold_completion_registry.v28.manifest.json"):
        p = repo / REPORT / name
        add_path(p)
    candidate_manifest = read(repo / REPORT / "alignment_candidates.manifest.json")
    for name, expected_sha in candidate_manifest["output_sha256"].items():
        p = repo / (REPORT if name == "candidate_generator_registry.json" else WORK) / name
        if sha(p) != expected_sha:
            raise ValueError("Candidate manifest chain changed: " + name)
        add_path(p)
    for p in sorted((repo / "scripts/bible_module").glob("ukrainian_stage_7*.py")):
        add_path(p)
    for p in (repo / "scripts/__init__.py", repo / "scripts/bible_module/__init__.py"):
        if p.is_file():
            add_path(p)
    consumer_names = []
    for name in ("fixed", "legacy"):
        p = repo / WORK / f"session_global_20261017_evaluation_author_01/{name}.evaluation_pipeline.v1.json"
        add_path(p)
        pipeline = read(p)
        for tool, expected in pipeline["consumer_specs"].items():
            relative = Path("scripts/bible_module") / tool
            verify({"path": relative.as_posix(), **expected}, repo)
            consumer_names.append(tool)
    if sorted(set(consumer_names)) != sorted(p.name for p in (repo / "scripts/bible_module").glob("ukrainian_stage_7*.py")):
        raise ValueError("Frozen consumer roster changed")
    for item in dependencies.values():
        verify(item, repo)
    if sha(repo / paths["annotations"]) != ANNOTATION_HASH or sha(repo / paths["mask"]) != MASK_HASH:
        raise ValueError("Gold/mask pinned digest mismatch")
    result = {"version": VERSION, "artifact": "consensus76_input_lock", "paths": {k: v.as_posix() for k, v in paths.items()},
              "dependencies": sorted(dependencies.values(), key=lambda v: v["path"]),
              "consumer_roster": sorted(set(consumer_names)), "gold_lock_sha256": GOLD_HASH}
    if out is not None:
        write(out, result)
    return result


def check_inputs(path, repo):
    lock = read(path)
    if lock.get("version") != VERSION or lock.get("gold_lock_sha256") != GOLD_HASH:
        raise ValueError("Wrong input lock version/gold")
    # Reconstruct mandatory role paths and the entire normative closure. A caller
    # cannot weaken a lock by deleting entries or redirecting a role to an unlocked file.
    expected = lock_inputs(repo)
    if lock != expected:
        raise ValueError("Input lock missing/duplicated/stale/redirected dependency or role")
    current = sorted(p.name for p in (repo / "scripts/bible_module").glob("ukrainian_stage_7*.py"))
    if current != lock["consumer_roster"]:
        raise ValueError("Stale frozen consumer source roster")
    return lock


def freeze(repo, inputs, build_dir, out):
    check_inputs(inputs, repo)
    from .core import validate_build
    validate_build(repo, inputs, build_dir)
    baseline = baseline_roster(repo)
    if not all(p.is_file() for p in baseline):
        raise ValueError("Frozen baseline artifact roster is incomplete")
    result = {"version": VERSION, "artifact": "consensus76_pipeline_freeze", "author": "/root/consensus_author",
              "source": [spec(p, repo) for p in source_roster()],
              "runtime": [spec(p) for p in runtime_roster()],
              "python": platform.python_version(), "input_lock": spec(inputs, repo),
              "build_dir": build_dir.relative_to(repo).as_posix(),
              "build": [spec(build_dir / n, repo) for n in ("graph.v1.jsonl", "prior.v1.json", "build.v1.manifest.json")],
              "preserved_baseline_artifacts": [spec(p, repo) for p in baseline],
              "protocol": read(PACKAGE / "protocol.v1.json"), "config": read(PACKAGE / "config.v1.json")}
    write(out, result)
    return result


def check_freeze(path, repo):
    lock = read(path)
    if lock.get("artifact") != "consensus76_pipeline_freeze" or lock.get("version") != VERSION:
        raise ValueError("Wrong pipeline freeze")
    if len(lock["source"]) != len(source_roster()) or {item["path"] for item in lock["source"]} != {p.relative_to(repo).as_posix() for p in source_roster()}:
        raise ValueError("Source roster missing or stale")
    if len(lock["runtime"]) != len(runtime_roster()) or {item["path"] for item in lock["runtime"]} != {str(p.resolve()) for p in runtime_roster()}:
        raise ValueError("Runtime roster missing or stale")
    expected_build = {(Path(lock["build_dir"]) / n).as_posix() for n in ("graph.v1.jsonl", "prior.v1.json", "build.v1.manifest.json")}
    if len(lock["build"]) != 3 or {item["path"] for item in lock["build"]} != expected_build:
        raise ValueError("Build dependency roster missing/duplicate/redirected")
    if len(lock["preserved_baseline_artifacts"]) != 8 or {item["path"] for item in lock["preserved_baseline_artifacts"]} != {p.relative_to(repo).as_posix() for p in baseline_roster(repo)}:
        raise ValueError("Preserved baseline dependency roster missing/duplicate/redirected")
    if lock["config"] != read(PACKAGE / "config.v1.json") or lock["protocol"] != read(PACKAGE / "protocol.v1.json"):
        raise ValueError("Embedded protocol/config differs from source lock")
    for item in lock["source"] + lock["runtime"] + lock["build"] + lock["preserved_baseline_artifacts"] + [lock["input_lock"]]:
        verify(item, repo)
    check_inputs(repo / lock["input_lock"]["path"], repo)
    return lock
