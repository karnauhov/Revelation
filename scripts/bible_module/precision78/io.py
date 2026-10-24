"""Exclusive evidence writes and physical preservation checks."""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scripts.bible_module.consensus76.io import canonical, read, runtime_roster, sha, spec, verify

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_7_20260801"
REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_7_20260801"
SESSION = WORK / "session_precision78_20261017_root_01"
SUPPORT = WORK / "session_calibration77_20261017_author_01/support.v1.json"
FREEZE = WORK / "session_consensus76_20261017_author_01/pipeline.v3.lock.json"


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf8", newline="\n") as stream:
        stream.write(canonical(value) + "\n")


def rows(path):
    with Path(path).open(encoding="utf8") as stream:
        for line in stream:
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError("Expected JSONL object")
            yield value


def sources():
    files = set(PACKAGE.rglob("*.py")) | set(PACKAGE.rglob("*.json"))
    files.update((ROOT / "scripts/bible_module/consensus76").glob("*.py"))
    files.update((ROOT / "scripts/bible_module/calibration77").glob("*.py"))
    return [spec(p, ROOT) for p in sorted(files)]


def preservation(baseline):
    checked = 0
    for item in read(baseline)["entries"]:
        path = (REPORT if item["root"] == "report" else WORK) / item["path"]
        verify({**item, "path": str(path)}, ROOT)
        checked += 1
    return {"status": "PASS", "immutable_entries_checked": checked}


def preflight():
    SESSION.mkdir(parents=True, exist_ok=False)
    inventory = REPORT / "artifact_inventory.manifest.json"
    (SESSION / "baseline_inventory.json").write_bytes(inventory.read_bytes())
    write(SESSION / "baseline_controls.json", [spec(p, ROOT) for p in [inventory, REPORT / "HANDOFF.ru.md", *sorted((ROOT / "scripts/bible_module").glob("ukrainian_stage_7*.py"))]])
    result = preservation(SESSION / "baseline_inventory.json")
    jobs = [("stage3", [sys.executable, "-X", "utf8", "-B", "-m", "scripts.bible_module.ukrainian_stage_3_sources", "--check", "--offline"])]
    jobs += [("stage" + str(n), [sys.executable, "-X", "utf8", "-B", "-m", "scripts.bible_module.ukrainian_stage_" + str(n), "--check"]) for n in (4, 5, 6, 7)]

    def run(job):
        name, args = job
        completed = subprocess.run(args, cwd=ROOT, capture_output=True)
        (SESSION / (name + ".stdout.log")).write_bytes(completed.stdout)
        (SESSION / (name + ".stderr.log")).write_bytes(completed.stderr)
        print(name, completed.returncode, flush=True)
        return {"name": name, "command": args, "exit_code": completed.returncode}

    with ThreadPoolExecutor(max_workers=2) as pool:
        result["checks"] = list(pool.map(run, jobs))
    result["status"] = "PASS" if all(v["exit_code"] == 0 for v in result["checks"]) else "FAIL"
    result["labels_read"] = False
    write(SESSION / "preflight.v1.json", result)
    if result["status"] != "PASS":
        raise ValueError("Preflight failed")


def lock():
    if read(SESSION / "preflight.v1.json")["status"] != "PASS":
        raise ValueError("Preflight required")
    from scripts.bible_module.calibration77.io import predecessor
    paths = predecessor(ROOT)  # Physical lock verification only; no evaluation.
    dependencies = [FREEZE, SUPPORT, REPORT / "consensus76.v1.ru.md", REPORT / "calibration77.v1.manifest.json", REPORT / "calibration77_independent_validation.v1.manifest.json"]
    dependencies += list(paths.values())
    inputs = {str(p): spec(p, ROOT) for p in dependencies}
    write(SESSION / "inputs.v1.lock.json", {"paths": {k: p.relative_to(ROOT).as_posix() for k, p in paths.items()}, "dependencies": list(inputs.values())})
    write(SESSION / "source_runtime.v1.lock.json", {"source": sources(), "runtime": [spec(p) for p in runtime_roster()], "python": sys.version})
    write(SESSION / "protocol.v1.lock.json", {"protocol": read(PACKAGE / "protocol.v1.json"), "source_runtime": spec(SESSION / "source_runtime.v1.lock.json", ROOT), "inputs": spec(SESSION / "inputs.v1.lock.json", ROOT), "preflight": spec(SESSION / "preflight.v1.json", ROOT)})


def checked_paths():
    locked = read(SESSION / "source_runtime.v1.lock.json")
    if sources() != locked["source"]:
        raise ValueError("Analysis source changed after lock")
    for item in locked["runtime"]:
        verify(item, ROOT)
    protocol = read(SESSION / "protocol.v1.lock.json")
    for key in ("source_runtime", "inputs", "preflight"):
        verify(protocol[key], ROOT)
    inputs = read(SESSION / "inputs.v1.lock.json")
    for item in inputs["dependencies"]:
        verify(item, ROOT)
    return {k: ROOT / p for k, p in inputs["paths"].items()}
