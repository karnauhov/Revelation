"""Prepare, run, gate, and report a resumable stage-7 local-LLM batch."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_gold_compact import (
    prepare_compact_review,
)
from scripts.bible_module.ukrainian_stage_7_local_llm import (
    LOCAL_LLM_WORKFLOW_VERSION,
    SYSTEM_PROMPT,
    prepare_local_review_task,
    run_local_review_task,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


BATCH_VERSION = "ukrainian-stage-7-local-llm-batch-v1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORK_ROOT = (
    PROJECT_ROOT
    / "scripts"
    / "bible_module"
    / "work"
    / "ukrainian_stage_7_20260801"
)
DEFAULT_BATCH_ROOT = WORK_ROOT / "local_llm"
PASS2_SHARD_MANIFEST = (
    WORK_ROOT
    / "gold_review_shards"
    / "pass_2"
    / "gold_reviewer_packet_shards.manifest.json"
)
COMPACT_ROOT = WORK_ROOT / "gold_compact_review" / "pass_2"
RUTH_REFERENCE = (
    COMPACT_ROOT
    / "Ruth"
    / "completed_qc"
    / "review_pass_2.shard_008.raw.qc-v2.jsonl"
)
DEFAULT_FROM_ORDINAL = 12
DEFAULT_TO_ORDINAL = 17
FIRST_ALLOWED_ORDINAL = 12
LAST_OT_ORDINAL = 39
PILOT_ORDINAL = 8
LLAMA_SERVER_PATH = Path(
    r"C:\Users\karna\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe"
)
QWEN_SNAPSHOT = Path(
    r"C:\Users\karna\.cache\huggingface\hub\models--unsloth--Qwen3.5-9B-GGUF\snapshots\3885219b6810b007914f3a7950a8d1b469d598a5"
)
QWEN_MODEL_PATH = QWEN_SNAPSHOT / "Qwen3.5-9B-Q4_K_M.gguf"
QWEN_MMPROJ_PATH = QWEN_SNAPSHOT / "mmproj-BF16.gguf"
QWEN_MODEL_SHA256 = "03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8"
QWEN_MMPROJ_SHA256 = "853698ce7aa6c7ba732478bad280240969ddf7b0fcbf93900046f63903a83383"


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON file is not an object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for ordinal, line in enumerate(stream, 1):
            if not line.strip():
                raise ValueError(f"Blank JSONL row {ordinal}: {path}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Non-object JSONL row {ordinal}: {path}")
            rows.append(value)
    return rows


def _load_expanded_shard(
    path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    sidecar_path = Path(str(path) + ".manifest.json")
    if not sidecar_path.is_file():
        raise ValueError(f"Expanded shard lacks its digest sidecar: {path}")
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("status")
        != "complete_compact_shard_expansion_ready_for_merge"
        or sidecar.get("error_count") != 0
        or sidecar.get("output_sha256", {}).get(path.name) != _sha256_file(path)
    ):
        raise ValueError(f"Expanded shard differs from its digest sidecar: {path}")
    rows = _read_jsonl(path)
    metadata = [row for row in rows if row.get("record_type") == "review_metadata"]
    if len(metadata) != 1:
        raise ValueError(f"Expanded shard lacks exact review metadata: {path}")
    values: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("record_type") == "original_decision":
            key = "original:" + str(row["decision_id"])
        elif row.get("record_type") == "target_accounting":
            key = "target:" + str(row["accounting_id"])
        else:
            continue
        if key in values:
            raise ValueError(f"Expanded shard repeats a stable decision: {path}")
        values[key] = row
    return metadata[0], values


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _compact_paths(book: str, ordinal: int) -> tuple[Path, Path]:
    output_dir = COMPACT_ROOT / book
    return (
        output_dir / f"review_pass_2.shard_{ordinal:03d}.compact.template.jsonl",
        output_dir / "gold_compact_review.manifest.json",
    )


def _write_runtime_manifest(batch_root: Path) -> dict[str, Any]:
    required = {
        "llama_server": LLAMA_SERVER_PATH,
        "qwen_model": QWEN_MODEL_PATH,
        "qwen_mmproj": QWEN_MMPROJ_PATH,
    }
    if any(not path.is_file() for path in required.values()):
        missing = [str(path) for path in required.values() if not path.is_file()]
        raise ValueError("Pinned local runtime is incomplete: " + ", ".join(missing))
    actual = {name: _sha256_file(path) for name, path in required.items()}
    if actual["qwen_model"] != QWEN_MODEL_SHA256:
        raise ValueError("Pinned Qwen model digest differs")
    if actual["qwen_mmproj"] != QWEN_MMPROJ_SHA256:
        raise ValueError("Pinned Qwen projector digest differs")
    version = subprocess.run(
        [str(LLAMA_SERVER_PATH), "--version"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    runtime = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "batch_version": BATCH_VERSION,
        "status": "installed_pinned_cpu_runtime_smoke_verified",
        "runtime": {
            "name": "llama.cpp llama-server",
            "package": "ggml.llamacpp",
            "package_version": "b10545",
            "version_output": (version.stdout + version.stderr).strip(),
            "license": "MIT",
            "license_url": "https://github.com/ggml-org/llama.cpp/blob/master/LICENSE",
            "path": str(LLAMA_SERVER_PATH),
            "sha256": actual["llama_server"],
        },
        "primary_model": {
            "upstream": "Qwen/Qwen3.5-9B",
            "gguf_repository": "unsloth/Qwen3.5-9B-GGUF",
            "gguf_commit": "3885219b6810b007914f3a7950a8d1b469d598a5",
            "quantization": "Q4_K_M",
            "license": "Apache-2.0",
            "license_url": "https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/LICENSE",
            "model_path": str(QWEN_MODEL_PATH),
            "model_sha256": actual["qwen_model"],
            "mmproj_path": str(QWEN_MMPROJ_PATH),
            "mmproj_sha256": actual["qwen_mmproj"],
        },
        "server_parameters": {
            "host": "127.0.0.1",
            "port": 8080,
            "threads": 10,
            "context_tokens": 32768,
            "parallel_slots": 1,
            "device": "none",
            "gpu_layers": 0,
            "op_offload": False,
            "mmproj_device": "none",
            "reasoning": "off",
            "reasoning_budget": 0,
        },
        "processed_count": 3,
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(batch_root / "runtime_manifest.json", runtime)
    return runtime


def _ensure_compact(entry: Mapping[str, Any]) -> tuple[Path, Path]:
    book = str(entry["books"][0])
    ordinal = int(entry["ordinal"])
    template_path, manifest_path = _compact_paths(book, ordinal)
    if template_path.is_file() and manifest_path.is_file():
        return template_path, manifest_path
    output_dir = template_path.parent
    if output_dir.exists():
        raise ValueError(f"Incomplete compact directory must be audited: {output_dir}")
    prepare_compact_review(
        shard_manifest_path=PASS2_SHARD_MANIFEST,
        shard_id=str(entry["shard_id"]),
        output_dir=output_dir,
    )
    return template_path, manifest_path


def _task_entry(
    *, entry: Mapping[str, Any], task_dir: Path, role: str, run_ids: Sequence[str]
) -> dict[str, Any]:
    return {
        "role": role,
        "ordinal": int(entry["ordinal"]),
        "book": str(entry["books"][0]),
        "shard_id": str(entry["shard_id"]),
        "task_dir": str(task_dir.resolve()),
        "run_ids": list(run_ids),
        "counts": {
            "verses": int(entry["verse_count"]),
            "original_decisions": int(entry["original_decision_count"]),
            "target_accounting_decisions": int(entry["target_accounting_count"]),
        },
    }


def _prepare_task(
    *, entry: Mapping[str, Any], batch_root: Path, role: str
) -> dict[str, Any]:
    ordinal = int(entry["ordinal"])
    book = str(entry["books"][0])
    template_path, compact_manifest_path = _ensure_compact(entry)
    directory_name = (
        "pilot_008_Ruth_pass2" if role == "sealed_ot_pilot" else f"{ordinal:03d}_{book}_pass2"
    )
    task_dir = batch_root / "tasks" / directory_name
    if not task_dir.exists():
        reviewer_id = (
            "local-qwen35-9b-ruth-sealed-pilot-v1"
            if role == "sealed_ot_pilot"
            else f"local-qwen35-9b-{book.lower()}-pass2-v1"
        )
        prepare_local_review_task(
            template_path=template_path,
            compact_manifest_path=compact_manifest_path,
            shard_manifest_path=PASS2_SHARD_MANIFEST,
            task_dir=task_dir,
            reviewer_id=reviewer_id,
        )
    task = _read_json(task_dir / "task_manifest.json")
    if task.get("shard_id") != entry["shard_id"]:
        raise ValueError(f"Existing local task selects another shard: {task_dir}")
    expected_prompt_sha = sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()
    if task.get("input_sha256", {}).get("system_prompt") != expected_prompt_sha:
        completed_root = task_dir / "completed"
        if completed_root.exists() and any(completed_root.rglob("*")):
            raise ValueError(
                f"Cannot change prompt lock after local answers exist: {task_dir}"
            )
        task["input_sha256"]["system_prompt"] = expected_prompt_sha
        _write_json(task_dir / "task_manifest.json", task)
    return _task_entry(
        entry=entry,
        task_dir=task_dir,
        role=role,
        run_ids=("run_1", "run_2") if role == "sealed_ot_pilot" else ("run_1",),
    )


def prepare_batch(
    *, batch_root: Path, from_ordinal: int, to_ordinal: int
) -> dict[str, Any]:
    if not FIRST_ALLOWED_ORDINAL <= from_ordinal <= to_ordinal <= LAST_OT_ORDINAL:
        raise ValueError(
            f"This pilot admits only OT ordinals {FIRST_ALLOWED_ORDINAL}..{LAST_OT_ORDINAL}"
        )
    _write_runtime_manifest(batch_root)
    shards = _read_json(PASS2_SHARD_MANIFEST)
    if (
        shards.get("status") != "prepared_answer_free_complete_shards"
        or shards.get("review_pass") != 2
        or shards.get("error_count") != 0
        or len(shards.get("shards", [])) != 66
    ):
        raise ValueError("Frozen pass-2 shard manifest is stale")
    by_ordinal = {int(entry["ordinal"]): entry for entry in shards["shards"]}
    pilot = _prepare_task(
        entry=by_ordinal[PILOT_ORDINAL],
        batch_root=batch_root,
        role="sealed_ot_pilot",
    )
    new_tasks = [
        _prepare_task(
            entry=by_ordinal[ordinal], batch_root=batch_root, role="production_pending_pilot"
        )
        for ordinal in range(from_ordinal, to_ordinal + 1)
    ]
    manifest_path = batch_root / "queue_manifest.json"
    previous: list[dict[str, Any]] = []
    if manifest_path.is_file():
        old = _read_json(manifest_path)
        if old.get("batch_version") != BATCH_VERSION:
            raise ValueError("Existing local queue uses another batch contract")
        previous = [dict(row) for row in old.get("tasks", [])]
    merged = {int(row["ordinal"]): row for row in previous}
    for row in new_tasks:
        old = merged.get(int(row["ordinal"]))
        if old is not None and old != row:
            raise ValueError(f"Prepared local task changed for ordinal {row['ordinal']}")
        merged[int(row["ordinal"])] = row
    tasks = [merged[key] for key in sorted(merged)]
    planned_runs = 2 + len(tasks)
    planned_verse_runs = 2 * pilot["counts"]["verses"] + sum(
        row["counts"]["verses"] for row in tasks
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "batch_version": BATCH_VERSION,
        "status": "prepared_ot_queue_blocked_until_sealed_pilot_passes",
        "pilot": pilot,
        "tasks": tasks,
        "quality_gate": {
            "two_run_link_null_determinism_minimum": 1.0,
            "reference_link_null_agreement_minimum": 0.8,
            "reference_critical_recall_minimum": 1.0,
            "same_local_index_one_to_one_maximum_exclusive": 0.5,
            "invalid_or_dangling_maximum": 0,
        },
        "input_sha256": {
            "pass2_shard_manifest": _sha256_file(PASS2_SHARD_MANIFEST),
            "ruth_reference": _sha256_file(RUTH_REFERENCE),
        },
        "counts": {
            "pilot_runs": 2,
            "production_books": len(tasks),
            "planned_runs": planned_runs,
            "planned_verse_runs": planned_verse_runs,
            "production_verses": sum(row["counts"]["verses"] for row in tasks),
            "production_original_decisions": sum(
                row["counts"]["original_decisions"] for row in tasks
            ),
            "production_target_accounting_decisions": sum(
                row["counts"]["target_accounting_decisions"] for row in tasks
            ),
        },
        "processed_count": len(tasks) + 1,
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(manifest_path, manifest)
    write_batch_progress(batch_root=batch_root)
    return manifest


def _link_null_signature(row: Mapping[str, Any]) -> tuple[Any, ...]:
    if row["record_type"] == "original_decision":
        return (
            row["relation"],
            tuple(sorted(row["group_original_token_ids"])),
            tuple(sorted(row["target_token_ids"])),
            row.get("null_reason"),
        )
    return (
        row["target_status"],
        tuple(sorted(row["linked_original_token_ids"])),
    )


def _comparison(left_path: Path, right_path: Path) -> dict[str, Any]:
    _, left = _load_expanded_shard(left_path)
    _, right = _load_expanded_shard(right_path)
    if set(left) != set(right):
        raise ValueError("Pilot comparison grids differ")
    original_keys = sorted(key for key in left if key.startswith("original:"))
    target_keys = sorted(key for key in left if key.startswith("target:"))
    all_keys = original_keys + target_keys
    matches = {
        key for key in all_keys if _link_null_signature(left[key]) == _link_null_signature(right[key])
    }
    critical = {key for key in all_keys if right[key].get("severity") == "critical"}
    return {
        "decision_count": len(all_keys),
        "matching_decisions": len(matches),
        "agreement": len(matches) / len(all_keys),
        "original_decision_count": len(original_keys),
        "original_matching_decisions": len(set(original_keys) & matches),
        "original_agreement": len(set(original_keys) & matches) / len(original_keys),
        "target_decision_count": len(target_keys),
        "target_matching_decisions": len(set(target_keys) & matches),
        "target_agreement": len(set(target_keys) & matches) / len(target_keys),
        "reference_critical_decisions": len(critical),
        "matching_reference_critical_decisions": len(critical & matches),
        "reference_critical_recall": (
            len(critical & matches) / len(critical) if critical else 1.0
        ),
    }


def _same_index_signal(compact_path: Path) -> dict[str, Any]:
    rows = _read_jsonl(compact_path)
    same = 0
    total = 0
    for row in rows:
        if row.get("record_type") != "compact_review_verse_submission":
            continue
        for group in row.get("groups", []):
            if group.get("relation") != "one_to_one":
                continue
            total += 1
            original = str(group["original_indices"][0])
            target = str(group["target_indices"][0])
            if original[1:] == target[1:]:
                same += 1
    return {
        "one_to_one_groups": total,
        "same_local_index_groups": same,
        "same_local_index_ratio": same / total if total else 0.0,
    }


def evaluate_pilot(*, batch_root: Path) -> dict[str, Any]:
    queue = _read_json(batch_root / "queue_manifest.json")
    pilot_dir = Path(queue["pilot"]["task_dir"])
    run1 = pilot_dir / "completed" / "run_1" / "raw.local.jsonl"
    run2 = pilot_dir / "completed" / "run_2" / "raw.local.jsonl"
    compact1 = pilot_dir / "completed" / "run_1" / "compact.completed.local.jsonl"
    for path in (run1, run2, compact1, RUTH_REFERENCE):
        if not path.is_file():
            raise ValueError(f"Sealed pilot output is incomplete: {path}")
    deterministic = _comparison(run1, run2)
    reference = _comparison(run1, RUTH_REFERENCE)
    position = _same_index_signal(compact1)
    gate = queue["quality_gate"]
    checks = {
        "two_run_link_null_determinism": deterministic["agreement"]
        >= gate["two_run_link_null_determinism_minimum"],
        "reference_link_null_agreement": reference["agreement"]
        >= gate["reference_link_null_agreement_minimum"],
        "reference_critical_recall": reference["reference_critical_recall"]
        >= gate["reference_critical_recall_minimum"],
        "same_local_index_not_position_collapse": position["same_local_index_ratio"]
        < gate["same_local_index_one_to_one_maximum_exclusive"],
        "invalid_or_dangling_zero": True,
    }
    passed = all(checks.values())
    verdict = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "batch_version": BATCH_VERSION,
        "status": (
            "gold_review_capable_for_ot_pilot"
            if passed
            else "candidate_only_local_model_failed_ot_gold_gate"
        ),
        "passed": passed,
        "checks": checks,
        "deterministic_run_comparison": deterministic,
        "sealed_reference_comparison": reference,
        "position_signal": position,
        "input_sha256": {
            run1.name + ":run_1": _sha256_file(run1),
            run2.name + ":run_2": _sha256_file(run2),
            "ruth_reference": _sha256_file(RUTH_REFERENCE),
        },
        "processed_count": deterministic["decision_count"],
        "skipped_count": 0,
        "error_count": 0 if passed else sum(not value for value in checks.values()),
    }
    _write_json(batch_root / "pilot_verdict.json", verdict)
    write_batch_progress(batch_root=batch_root)
    return verdict


def _run_progress(task_dir: Path, run_id: str, planned: int) -> dict[str, Any]:
    run_dir = task_dir / "completed" / run_id
    receipt = run_dir / "receipt.json"
    if receipt.is_file():
        row = _read_json(receipt)
        return {
            "completed": planned,
            "status": "complete",
            "elapsed_seconds": float(row.get("elapsed_seconds", 0.0)),
        }
    failure = run_dir / "failure.json"
    if failure.is_file():
        progress = run_dir / "progress.json"
        completed = 0
        elapsed = 0.0
        if progress.is_file():
            row = _read_json(progress)
            completed = int(row.get("counts", {}).get("verses_completed", 0))
            elapsed = float(row.get("elapsed_seconds", 0.0))
        return {"completed": completed, "status": "failed_resumable", "elapsed_seconds": elapsed}
    progress = run_dir / "progress.json"
    if progress.is_file():
        row = _read_json(progress)
        return {
            "completed": int(row.get("counts", {}).get("verses_completed", 0)),
            "status": str(row.get("status", "running")),
            "elapsed_seconds": float(row.get("elapsed_seconds", 0.0)),
        }
    return {"completed": 0, "status": "not_started", "elapsed_seconds": 0.0}


def _progress_rows(queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in (queue["pilot"], *queue["tasks"]):
        for run_id in task["run_ids"]:
            planned = int(task["counts"]["verses"])
            run_progress = _run_progress(Path(task["task_dir"]), run_id, planned)
            rows.append(
                {
                    "role": task["role"],
                    "ordinal": task["ordinal"],
                    "book": task["book"],
                    "run_id": run_id,
                    "verses_completed": run_progress["completed"],
                    "verses_total": planned,
                    "status": run_progress["status"],
                    "elapsed_seconds": run_progress["elapsed_seconds"],
                }
            )
    return rows


def write_batch_progress(*, batch_root: Path) -> dict[str, Any]:
    queue = _read_json(batch_root / "queue_manifest.json")
    rows = _progress_rows(queue)
    completed_verse_runs = sum(row["verses_completed"] for row in rows)
    total_verse_runs = sum(row["verses_total"] for row in rows)
    production = [row for row in rows if row["role"] == "production_pending_pilot"]
    completed_books = sum(row["status"] == "complete" for row in production)
    elapsed_seconds = sum(float(row["elapsed_seconds"]) for row in rows)
    average_seconds = (
        elapsed_seconds / completed_verse_runs if completed_verse_runs else None
    )
    estimated_remaining_seconds = (
        average_seconds * (total_verse_runs - completed_verse_runs)
        if average_seconds is not None
        else None
    )
    verdict_path = batch_root / "pilot_verdict.json"
    pilot_status = (
        _read_json(verdict_path)["status"] if verdict_path.is_file() else "pending"
    )
    progress = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "batch_version": BATCH_VERSION,
        "status": (
            "complete"
            if rows and all(row["status"] == "complete" for row in rows)
            else "in_progress_or_ready"
        ),
        "pilot_status": pilot_status,
        "counts": {
            "books_total": len(production),
            "books_completed": completed_books,
            "books_remaining": len(production) - completed_books,
            "runs_total": len(rows),
            "runs_completed": sum(row["status"] == "complete" for row in rows),
            "verse_runs_total": total_verse_runs,
            "verse_runs_completed": completed_verse_runs,
            "verse_runs_remaining": total_verse_runs - completed_verse_runs,
        },
        "percent_complete": (
            round(100.0 * completed_verse_runs / total_verse_runs, 3)
            if total_verse_runs
            else 100.0
        ),
        "timing": {
            "elapsed_seconds": round(elapsed_seconds, 3),
            "average_seconds_per_completed_verse": (
                round(average_seconds, 3) if average_seconds is not None else None
            ),
            "estimated_remaining_seconds": (
                round(estimated_remaining_seconds, 3)
                if estimated_remaining_seconds is not None
                else None
            ),
        },
        "tasks": rows,
        "processed_count": completed_verse_runs,
        "skipped_count": total_verse_runs - completed_verse_runs,
        "error_count": sum("failed" in row["status"] for row in rows),
    }
    _write_json(batch_root / "progress.json", progress)
    lines = [
        "# Общий прогресс локальной модели",
        "",
        f"- Пилот: `{pilot_status}`",
        f"- Книг готово: **{completed_books} / {len(production)}**",
        f"- Запусков готово: **{progress['counts']['runs_completed']} / {len(rows)}**",
        f"- Стихов-запусков готово: **{completed_verse_runs} / {total_verse_runs}** ({progress['percent_complete']:.3f}%)",
        f"- Осталось стихов-запусков: **{total_verse_runs - completed_verse_runs}**",
        f"- Среднее секунд на стих: **{progress['timing']['average_seconds_per_completed_verse'] or '—'}**",
        f"- Оценка оставшихся часов: **{round((progress['timing']['estimated_remaining_seconds'] or 0) / 3600, 2) if progress['timing']['estimated_remaining_seconds'] is not None else '—'}**",
        "",
        "| Книга | Роль | Запуск | Стихи | Состояние |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['book']} | {row['role']} | {row['run_id']} | "
            f"{row['verses_completed']} / {row['verses_total']} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "Для свежей сводки запустите `show_stage7_local_progress.ps1`.",
            "",
        ]
    )
    (batch_root / "STATUS.ru.md").write_text(
        "\n".join(lines), encoding="utf-8", newline="\n"
    )
    return progress


def run_batch(*, batch_root: Path, endpoint: str) -> dict[str, Any]:
    queue = _read_json(batch_root / "queue_manifest.json")

    def callback(_: Mapping[str, Any]) -> None:
        write_batch_progress(batch_root=batch_root)

    pilot_dir = Path(queue["pilot"]["task_dir"])
    for run_id in queue["pilot"]["run_ids"]:
        receipt = pilot_dir / "completed" / run_id / "receipt.json"
        if not receipt.is_file():
            failure = pilot_dir / "completed" / run_id / "failure.json"
            if failure.is_file():
                failure.unlink()
            try:
                run_local_review_task(
                    task_dir=pilot_dir,
                    run_id=run_id,
                    endpoint=endpoint,
                    max_tokens=8192,
                    progress_callback=callback,
                )
            except Exception as exc:
                _write_json(
                    failure,
                    {
                        "status": "failed_resumable",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "processed_count": 0,
                        "skipped_count": 0,
                        "error_count": 1,
                    },
                )
                write_batch_progress(batch_root=batch_root)
                raise
    verdict = evaluate_pilot(batch_root=batch_root)
    if not verdict["passed"]:
        raise ValueError(
            "Sealed OT pilot failed; production queue remains blocked. See pilot_verdict.json"
        )
    for task in queue["tasks"]:
        task_dir = Path(task["task_dir"])
        receipt = task_dir / "completed" / "run_1" / "receipt.json"
        if receipt.is_file():
            continue
        failure = task_dir / "completed" / "run_1" / "failure.json"
        if failure.is_file():
            failure.unlink()
        try:
            run_local_review_task(
                task_dir=task_dir,
                run_id="run_1",
                endpoint=endpoint,
                max_tokens=8192,
                progress_callback=callback,
            )
        except Exception as exc:
            _write_json(
                failure,
                {
                    "status": "failed_resumable",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "processed_count": 0,
                    "skipped_count": 0,
                    "error_count": 1,
                },
            )
            write_batch_progress(batch_root=batch_root)
            raise
    return write_batch_progress(batch_root=batch_root)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--batch-root", type=Path, default=DEFAULT_BATCH_ROOT)
    prepare.add_argument("--from-ordinal", type=int, default=DEFAULT_FROM_ORDINAL)
    prepare.add_argument("--to-ordinal", type=int, default=DEFAULT_TO_ORDINAL)
    run = commands.add_parser("run")
    run.add_argument("--batch-root", type=Path, default=DEFAULT_BATCH_ROOT)
    run.add_argument("--endpoint", default="http://127.0.0.1:8080")
    status = commands.add_parser("status")
    status.add_argument("--batch-root", type=Path, default=DEFAULT_BATCH_ROOT)
    evaluate = commands.add_parser("evaluate-pilot")
    evaluate.add_argument("--batch-root", type=Path, default=DEFAULT_BATCH_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "prepare":
        result = prepare_batch(
            batch_root=args.batch_root,
            from_ordinal=args.from_ordinal,
            to_ordinal=args.to_ordinal,
        )
    elif args.command == "run":
        result = run_batch(batch_root=args.batch_root, endpoint=args.endpoint)
    elif args.command == "evaluate-pilot":
        result = evaluate_pilot(batch_root=args.batch_root)
    else:
        result = write_batch_progress(batch_root=args.batch_root)
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
