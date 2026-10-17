"""Additive calibration locks. Frozen predecessor consumers are never invoked."""
from __future__ import annotations

from pathlib import Path

from scripts.bible_module.consensus76 import io as predecessor_io

from . import VERSION

canonical = predecessor_io.canonical
digest = predecessor_io.digest
read = predecessor_io.read
rows = predecessor_io.rows
sha = predecessor_io.sha
spec = predecessor_io.spec
verify = predecessor_io.verify
runtime_roster = predecessor_io.runtime_roster

PACKAGE = Path(__file__).resolve().parent
WORK = Path("scripts/bible_module/work/ukrainian_stage_7_20260801")
PREDECESSOR = WORK / "session_consensus76_20261017_author_01/pipeline.v3.lock.json"
PREDECESSOR_SHA = "230d671d431763bac09873cd5f90a9b237a667fe6805cdc1556f45ca5764ab80"
PREDECESSOR_COMPLETION = Path("scripts/bible_module/reports/ukrainian_stage_7_20260801/consensus76.v1.manifest.json")
PREDECESSOR_COMPLETION_SHA = "1a136aa2e7142464301a3c0365b06025f5755716fe92ffb15c37cb1d06ff8e09"
PREDECESSOR_QC = Path("scripts/bible_module/reports/ukrainian_stage_7_20260801/consensus76_independent_validation.v1.manifest.json")
PREDECESSOR_QC_SHA = "7dbb56fc9849c1836089b5f477bc53c589592b7d86ca7522875130a0a9486d18"
ROOT_PROTOCOL = WORK / "session_calibration77_20261017_root_01/execution_protocol.v1.lock.json"
ROOT_FEASIBILITY = WORK / "session_calibration77_20261017_root_01/prefit_structural_feasibility.v1.json"
AUTHOR_SESSION = WORK / "session_calibration77_20261017_author_01"
CANONICAL_PROTOCOL = AUTHOR_SESSION / "protocol.v1.lock.json"
CANONICAL_FREEZE = AUTHOR_SESSION / "pipeline.v1.lock.json"
GUARDS = {"candidate_only": True, "resolver_eligible": False, "auto_acceptance": False,
          "automatic_strong_promotions": 0, "production_accepted_links": 0}


def write(path, value):
    """Exclusive writes make a partial run visible and prohibit silent reruns."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical(value) + "\n")


def source_roster():
    result = {p for p in PACKAGE.rglob("*") if p.is_file() and p.suffix in {".py", ".json"}}
    result.update(p / "__init__.py" for p in (PACKAGE.parent, PACKAGE.parent.parent)
                  if (p / "__init__.py").is_file())
    return sorted(result)


def current_code(repo):
    return {"source": [spec(p, repo) for p in source_roster()],
            "runtime": [spec(p) for p in runtime_roster()]}


def check_code(value, repo):
    expected = current_code(repo)
    if any(value.get(k) != expected[k] for k in expected):
        raise ValueError("Calibration source/runtime roster changed or incomplete")


def predecessor(repo):
    for path, expected in ((PREDECESSOR, PREDECESSOR_SHA),
                           (PREDECESSOR_COMPLETION, PREDECESSOR_COMPLETION_SHA),
                           (PREDECESSOR_QC, PREDECESSOR_QC_SHA)):
        if sha(repo / path) != expected:
            raise ValueError("Frozen predecessor digest changed: " + str(path))
    # Pure physical lock verifier, not a build, evaluation or data-regeneration command.
    frozen = predecessor_io.check_freeze(repo / PREDECESSOR, repo)
    inputs = read(repo / frozen["input_lock"]["path"])
    paths = {k: repo / v for k, v in inputs["paths"].items()}
    paths["graph"] = next(repo / v["path"] for v in frozen["build"] if v["path"].endswith("graph.v1.jsonl"))
    paths["gold_contract"] = repo / predecessor_io.REPORT / "gold_alignment.finalized.v2.lock.json"
    return paths


def protocol_lock(repo, out, preflight, support):
    if out.resolve() != (repo / CANONICAL_PROTOCOL).resolve() or support.resolve() != (repo / AUTHOR_SESSION / "support.v1.json").resolve():
        raise ValueError("Protocol/support must use preregistered canonical session paths")
    receipt = read(preflight)
    if receipt.get("status") != "PASS":
        raise ValueError("Root preflight PASS required before full corpus processing")
    feasibility = read(support)
    if feasibility.get("artifact") != "calibration77_prefit_support" or feasibility.get("labels_read") is not False or feasibility.get("certification_status") != "NO_GO":
        raise ValueError("Label-free pre-fit support NO_GO required")
    result = {"version": VERSION, "artifact": "calibration77_protocol_lock",
              "author": "/root/calibration_author", "preflight": spec(preflight, repo),
              "root_protocol": spec(repo / ROOT_PROTOCOL, repo), "support": spec(support, repo),
              "root_feasibility": spec(repo / ROOT_FEASIBILITY, repo),
              "predecessor": spec(repo / PREDECESSOR, repo),
              "config": read(PACKAGE / "config.v1.json"),
              "protocol": read(PACKAGE / "protocol.v1.json"), **current_code(repo), **GUARDS}
    write(out, result)
    return result


def check_protocol(repo, path, full_inputs=True):
    if path.resolve() != (repo / CANONICAL_PROTOCOL).resolve():
        raise ValueError("Copied/redirected protocol lock path forbidden")
    value = read(path)
    if value.get("artifact") != "calibration77_protocol_lock" or value.get("version") != VERSION:
        raise ValueError("Wrong calibration protocol lock")
    if value.get("predecessor") != spec(repo / PREDECESSOR, repo):
        raise ValueError("Redirected/missing predecessor lock")
    verify(value["preflight"], repo)
    if value.get("root_protocol") != spec(repo / ROOT_PROTOCOL, repo):
        raise ValueError("Root execution protocol changed or redirected")
    if value.get("root_feasibility") != spec(repo / ROOT_FEASIBILITY, repo):
        raise ValueError("Root pre-fit feasibility changed or redirected")
    verify(value["support"], repo)
    if read(repo / value["preflight"]["path"]).get("status") != "PASS":
        raise ValueError("Preflight no longer PASS")
    if value.get("config") != read(PACKAGE / "config.v1.json") or value.get("protocol") != read(PACKAGE / "protocol.v1.json"):
        raise ValueError("Protocol/config changed after preregistration")
    check_code(value, repo)
    return predecessor(repo) if full_inputs else value


def claim(repo, stage, value):
    if stage not in {"development", "validation3"}:
        raise ValueError("Unknown one-time claim stage")
    write(repo / AUTHOR_SESSION / (stage + ".claim.v1.json"), value)


def validate_guards(value):
    for key, expected in GUARDS.items():
        if type(value.get(key)) is not type(expected) or value[key] != expected:
            raise ValueError("Calibration artifact claims forbidden acceptance")
