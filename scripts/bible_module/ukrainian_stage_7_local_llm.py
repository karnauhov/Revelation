"""Prepare and run resumable local-LLM blind review tasks for stage 7."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import time
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.bible_module.ukrainian_stage_7_gold_compact import (
    COMPACT_REVIEW_VERSION,
    _validate_group,
    _validate_target_null,
    check_compact_review,
    expand_compact_review,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


LOCAL_LLM_WORKFLOW_VERSION = "ukrainian-stage-7-local-llm-review-v1"
DEFAULT_ENDPOINT = "http://127.0.0.1:8080"
SYSTEM_PROMPT = """You are an independent blind linguistic reviewer for Ukrainian Bible alignment.
For the supplied single verse, link exact original Hebrew/Greek local indices to exact OH1988 Ukrainian local indices. Do not use position, nearest-neighbor, frequency, verse-bag, another translation, Strong numbers, candidates, legacy results, or an unseen review pass as ground truth.

Return exactly one JSON object with exactly two keys: groups and target_nulls.
Every original index must occur exactly once across groups. Every target index must occur exactly once either in a group's target_indices or in target_nulls. Do not invent or alter indices.

Each group must contain exactly: original_indices, target_indices, relation, null_reason, severity, phenomena, evidence, rationale.
Allowed relation and exact cardinality: one_to_one = 1 original + 1 target; one_to_many = 1 original + at least 2 targets; many_to_one = at least 2 originals + 1 target; many_to_many = at least 2 originals + at least 2 targets; grouped_expression = any other nonempty original/target grouping; original_omitted = exactly 1 original + 0 targets.
Never put two or more originals into one original_omitted group: emit one omission group per original. original_omitted requires null_reason from: translation_omission, grammatical_function_not_overt, absorbed_by_grouped_expression, repetition_not_rendered, source_text_not_rendered. Every non-null relation requires null_reason=null.
Use the smallest linguistically defensible groups. Never collapse a whole verse merely to satisfy exact accounting. Distinguish repeated identical original forms by their syntax, morphology, and the inflected Ukrainian context.
Allowed severity: normal, high, critical.
phenomena must be a nonempty list of one or two relevant labels. evidence must be a nonempty list of objects with exactly kind and evidence_id; use kind=local_llm_token_context and stable local indices in evidence_id. Keep rationale factual and concise, at most twelve words.

Each target_null must contain exactly: target_index, target_status, severity, phenomena, evidence, rationale.
target_status must be translation_addition or function_token.
Output JSON only, with no Markdown or commentary."""


ProgressCallback = Callable[[Mapping[str, Any]], None]
PROMPT_DISPLAY_FIELDS = (
    "surface_raw",
    "surface_normalized",
    "transliteration_raw",
    "lemma_raw",
    "gloss_raw",
    "morphology_raw",
    "order",
    "reading_status",
    "projection_status",
    "component_group",
    "component_kind",
    "textual_variant_raw",
    "textual_witnesses",
    "source_family",
    "source_locator",
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


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


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _prompt_view(template: Mapping[str, Any]) -> dict[str, Any]:
    """Keep linguistic context while removing hashes, IDs, and Strong leakage."""

    originals: list[dict[str, Any]] = []
    for row in template.get("original_index", []):
        display = row.get("display", {})
        originals.append(
            {
                "index": row["index"],
                "display": {
                    key: display.get(key)
                    for key in PROMPT_DISPLAY_FIELDS
                    if key in display
                },
            }
        )
    targets = [
        {
            key: row[key]
            for key in ("index", "order", "surface", "comparison")
            if key in row
        }
        for row in template.get("target_index", [])
    ]
    return {
        key: template[key]
        for key in ("target_ref", "book", "testament", "plain_text_nfc", "target_comment")
        if key in template
    } | {"original_index": originals, "target_index": targets}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_run_progress(
    *,
    run_dir: Path,
    task: Mapping[str, Any],
    run_id: str,
    total: int,
    completed: int,
    failed: int,
    current_ref: str | None,
    started: float,
    status: str,
) -> dict[str, Any]:
    elapsed = max(0.0, time.time() - started)
    average = elapsed / completed if completed else None
    remaining = average * (total - completed) if average is not None else None
    progress = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "status": status,
        "task_id": task["task_id"],
        "run_id": run_id,
        "review_pass": task["review_pass"],
        "reviewer_id": task["reviewer_id"],
        "current_ref": current_ref,
        "counts": {
            "verses_total": total,
            "verses_completed": completed,
            "verses_remaining": total - completed,
            "verses_failed": failed,
        },
        "percent_complete": round(100.0 * completed / total, 3) if total else 100.0,
        "elapsed_seconds": round(elapsed, 3),
        "average_seconds_per_completed_verse": (
            round(average, 3) if average is not None else None
        ),
        "estimated_remaining_seconds": (
            round(remaining, 3) if remaining is not None else None
        ),
        "updated_at_utc": _utc_now(),
        "processed_count": completed,
        "skipped_count": total - completed,
        "error_count": failed,
    }
    _write_json(run_dir / "progress.json", progress)
    status_lines = [
        "# Прогресс локальной модели",
        "",
        f"- Задание: `{task['task_id']}`",
        f"- Запуск: `{run_id}`",
        f"- Состояние: `{status}`",
        f"- Стихов готово: **{completed} / {total}** ({progress['percent_complete']:.3f}%)",
        f"- Осталось стихов: **{total - completed}**",
        f"- Ошибок: **{failed}**",
        f"- Сейчас: `{current_ref or '—'}`",
        f"- Прошло секунд: {progress['elapsed_seconds']}",
        f"- Среднее секунд на готовый стих: {progress['average_seconds_per_completed_verse'] or '—'}",
        f"- Оценка оставшихся секунд: {progress['estimated_remaining_seconds'] or '—'}",
        f"- Обновлено UTC: `{progress['updated_at_utc']}`",
        "",
        "Файл обновляется после каждого принятого стиха; ответы вручную не редактировать.",
        "",
    ]
    (run_dir / "STATUS.ru.md").write_text(
        "\n".join(status_lines), encoding="utf-8", newline="\n"
    )
    return progress


def _metadata(
    compact: Mapping[str, Any], *, reviewer_id: str, compact_manifest_sha: str
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "compact_review_version": COMPACT_REVIEW_VERSION,
        "record_type": "compact_review_metadata",
        "review_pass": compact["review_pass"],
        "reviewer_id": reviewer_id,
        "blind_to_other_pass": True,
        "packet_sha256": compact["input_sha256"]["review_packet"],
        "packet_manifest_sha256": compact["input_sha256"][
            "review_packet_manifest"
        ],
        "input_sha256": compact["parent_input_sha256"],
        "compact_template_sha256": compact["output_sha256"][
            compact["template_name"]
        ],
        "compact_manifest_sha256": compact_manifest_sha,
        "shard_contract_version": compact["shard_contract_version"],
        "shard_id": compact["shard_id"],
        "shard_manifest_sha256": compact["shard_manifest_sha256"],
        "shard_ordinal": compact["shard_ordinal"],
        "shard_packet_sha256": compact["shard_packet_sha256"],
        "parent_packet_sha256": compact["parent_packet_sha256"],
        "parent_packet_manifest_sha256": compact[
            "parent_packet_manifest_sha256"
        ],
    }


def prepare_local_review_task(
    *,
    template_path: Path,
    compact_manifest_path: Path,
    shard_manifest_path: Path,
    task_dir: Path,
    reviewer_id: str,
) -> dict[str, Any]:
    if task_dir.exists():
        raise FileExistsError(f"Local LLM task already exists: {task_dir}")
    if not reviewer_id or any(character.isspace() for character in reviewer_id):
        raise ValueError("Local reviewer ID must be nonempty and contain no whitespace")
    compact = _read_json(compact_manifest_path)
    template_rows = _read_jsonl(template_path)
    if (
        compact.get("schema_version") != SCHEMA_VERSION
        or compact.get("contract_version") != CONTRACT_VERSION
        or compact.get("compact_review_version") != COMPACT_REVIEW_VERSION
        or compact.get("review_scope") != "shard"
        or compact.get("error_count") != 0
        or compact.get("output_sha256")
        != {template_path.name: _sha256_file(template_path)}
        or compact.get("processed_count") != len(template_rows)
    ):
        raise ValueError("Local LLM source compact bundle is stale or invalid")
    for row in template_rows:
        if (
            row.get("record_type") != "compact_review_verse_template"
            or row.get("reviewer_answers") != {"groups": [], "target_nulls": []}
            or row.get("review_pass") != compact.get("review_pass")
            or row.get("shard_id") != compact.get("shard_id")
        ):
            raise ValueError("Local LLM source contains answers or stale identity")

    inputs = task_dir / "inputs"
    inputs.mkdir(parents=True)
    task_template = inputs / template_path.name
    task_compact = inputs / compact_manifest_path.name
    shutil.copyfile(template_path, task_template)
    shutil.copyfile(compact_manifest_path, task_compact)
    metadata = _metadata(
        compact,
        reviewer_id=reviewer_id,
        compact_manifest_sha=_sha256_file(task_compact),
    )
    _write_jsonl(inputs / "completed_metadata.template.jsonl", [metadata])
    request_path = task_dir / "request.md"
    request_path.write_text(
        "# Local blind review task\n\n"
        "Run `run_local_llm.ps1` while the approved llama-server is available at "
        "127.0.0.1:8080. Do not add pass-1, candidates, legacy or completed gold "
        "to this directory. The runner is resumable and validates every verse.\n",
        encoding="utf-8",
        newline="\n",
    )
    source_paths = {
        "template": str(template_path.resolve()),
        "compact_manifest": str(compact_manifest_path.resolve()),
        "shard_manifest": str(shard_manifest_path.resolve()),
    }
    task = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "status": "prepared_answer_free_local_llm_task",
        "task_id": f"uk7local:{compact['shard_id']}:pass:{compact['review_pass']}",
        "review_pass": compact["review_pass"],
        "reviewer_id": reviewer_id,
        "shard_id": compact["shard_id"],
        "source_paths": source_paths,
        "input_sha256": {
            "compact_template": _sha256_file(task_template),
            "compact_manifest": _sha256_file(task_compact),
            "shard_manifest": _sha256_file(shard_manifest_path),
            "metadata_template": _sha256_file(
                inputs / "completed_metadata.template.jsonl"
            ),
            "system_prompt": _sha256_text(SYSTEM_PROMPT),
        },
        "counts": {
            "selected_verses": len(template_rows),
            "original_decisions": compact["counts"]["primary_original_decisions"],
            "target_accounting_decisions": compact["counts"][
                "target_token_accounting_decisions"
            ],
        },
        "forbidden_channels": [
            "pass_1",
            "other_completed_answers",
            "alignment_candidates",
            "legacy_experiment",
            "strong_alignment",
            "finalized_gold",
        ],
        "processed_count": len(template_rows),
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(task_dir / "task_manifest.json", task)
    runner = task_dir / "run_local_llm.ps1"
    runner.write_text(
        "$ErrorActionPreference = 'Stop'\n"
        "$project = 'C:\\Users\\karna\\Projects\\Revelation'\n"
        "Set-Location -LiteralPath $project\n"
        f"python -B -m scripts.bible_module.ukrainian_stage_7_local_llm run "
        f"--task-dir '{task_dir.resolve()}' --run-id run_1\n"
        "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }\n",
        encoding="utf-8-sig",
        newline="\r\n",
    )
    return task


def _validate_answer(
    answer: Mapping[str, Any], template: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if set(answer) != {"groups", "target_nulls"}:
        raise ValueError("Answer must contain exactly groups and target_nulls")
    groups = answer.get("groups")
    target_nulls = answer.get("target_nulls")
    if not isinstance(groups, list) or not isinstance(target_nulls, list):
        raise ValueError("Answer groups and target_nulls must be lists")
    originals = {
        str(row["index"]): row for row in template.get("original_index", [])
    }
    targets = {str(row["index"]): row for row in template.get("target_index", [])}
    seen_originals: set[str] = set()
    seen_targets: set[str] = set()
    canonical_groups: list[dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("Answer group is not an object")
        original_indices, target_indices = _validate_group(
            group, originals=originals, targets=targets
        )
        if not group["phenomena"]:
            raise ValueError("Local LLM group phenomena must be nonempty")
        if seen_originals.intersection(original_indices):
            raise ValueError("Original local index occurs in multiple groups")
        if seen_targets.intersection(target_indices):
            raise ValueError("Target local index occurs in multiple groups")
        seen_originals.update(original_indices)
        seen_targets.update(target_indices)
        canonical_groups.append(dict(group))
    canonical_nulls: list[dict[str, Any]] = []
    for target_null in target_nulls:
        if not isinstance(target_null, dict):
            raise ValueError("Answer target null is not an object")
        target_index = _validate_target_null(target_null, targets)
        if not target_null["phenomena"]:
            raise ValueError("Local LLM target-null phenomena must be nonempty")
        if target_index in seen_targets:
            raise ValueError("Target local index is both aligned and null")
        seen_targets.add(target_index)
        canonical_nulls.append(dict(target_null))
    if seen_originals != set(originals):
        missing = sorted(set(originals) - seen_originals)
        extra = sorted(seen_originals - set(originals))
        raise ValueError(f"Original exact accounting differs; missing={missing}, extra={extra}")
    if seen_targets != set(targets):
        missing = sorted(set(targets) - seen_targets)
        extra = sorted(seen_targets - set(targets))
        raise ValueError(f"Target exact accounting differs; missing={missing}, extra={extra}")
    return canonical_groups, canonical_nulls


def _canonicalize_answer_format(
    answer: Mapping[str, Any],
) -> tuple[dict[str, Any], Counter[str]]:
    """Repair only schema/cardinality labels without changing any selected link."""

    repairs: Counter[str] = Counter()
    groups = answer.get("groups")
    target_nulls = answer.get("target_nulls")
    if not isinstance(groups, list) or not isinstance(target_nulls, list):
        return dict(answer), repairs
    normalized_groups: list[Any] = []
    cardinal_relations = {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}
    for raw_group in groups:
        if not isinstance(raw_group, dict):
            normalized_groups.append(raw_group)
            continue
        group = dict(raw_group)
        originals = group.get("original_indices")
        targets = group.get("target_indices")
        relation = group.get("relation")
        if not isinstance(originals, list) or not isinstance(targets, list):
            normalized_groups.append(group)
            continue
        if relation == "original_omitted" and not targets and len(originals) > 1:
            for original in originals:
                split = dict(group)
                split["original_indices"] = [original]
                _canonicalize_evidence_ids(split, repairs)
                normalized_groups.append(split)
            repairs["split_multi_original_omission"] += len(originals) - 1
            continue
        if relation in cardinal_relations and originals and targets:
            cardinality = (len(originals), len(targets))
            expected = (
                "one_to_one"
                if cardinality == (1, 1)
                else "one_to_many"
                if cardinality[0] == 1
                else "many_to_one"
                if cardinality[1] == 1
                else "many_to_many"
            )
            if relation != expected:
                repairs[f"relation_{relation}_to_{expected}"] += 1
                group["relation"] = expected
        _canonicalize_evidence_ids(group, repairs)
        normalized_groups.append(group)
    normalized_nulls: list[Any] = []
    for raw_null in target_nulls:
        if not isinstance(raw_null, dict):
            normalized_nulls.append(raw_null)
            continue
        target_null = dict(raw_null)
        _canonicalize_evidence_ids(target_null, repairs)
        normalized_nulls.append(target_null)
    return {"groups": normalized_groups, "target_nulls": normalized_nulls}, repairs


def _canonicalize_evidence_ids(
    row: dict[str, Any], repairs: Counter[str]
) -> None:
    """Join only nonempty string evidence-ID lists; never infer evidence or links."""

    evidence = row.get("evidence")
    if not isinstance(evidence, list):
        return
    normalized: list[Any] = []
    for raw_item in evidence:
        if not isinstance(raw_item, dict):
            normalized.append(raw_item)
            continue
        item = dict(raw_item)
        evidence_id = item.get("evidence_id")
        if (
            isinstance(evidence_id, list)
            and evidence_id
            and all(isinstance(value, str) and value.strip() for value in evidence_id)
        ):
            item["evidence_id"] = "|".join(value.strip() for value in evidence_id)
            repairs["evidence_id_string_list_joined"] += 1
        normalized.append(item)
    row["evidence"] = normalized


def _parse_response_json(content: str) -> tuple[dict[str, Any], Counter[str]]:
    """Parse a completion after removing only recognized non-semantic wrappers."""

    repairs: Counter[str] = Counter()
    candidate = content.strip()
    if "</think>" in candidate:
        suffix = candidate.rsplit("</think>", 1)[1].strip()
        if suffix:
            candidate = suffix
            repairs["reasoning_prefix_removed"] += 1
    lines = candidate.splitlines()
    if (
        len(lines) >= 3
        and lines[0].strip().lower() in {"```", "```json"}
        and lines[-1].strip() == "```"
    ):
        candidate = "\n".join(lines[1:-1]).strip()
        repairs["markdown_json_fence_removed"] += 1
    parsed = json.loads(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("Completion JSON is not an object")
    return parsed, repairs


def _submission_row(
    template: Mapping[str, Any],
    *,
    reviewer_id: str,
    groups: Sequence[Mapping[str, Any]],
    target_nulls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": template["schema_version"],
        "contract_version": template["contract_version"],
        "compact_review_version": template["compact_review_version"],
        "record_type": "compact_review_verse_submission",
        "selection_id": template["selection_id"],
        "target_ref": template["target_ref"],
        "template_row_sha256": template["template_row_sha256"],
        "reviewer_id": reviewer_id,
        "groups": list(groups),
        "target_nulls": list(target_nulls),
    }


def _http_json(
    url: str, *, method: str = "GET", payload: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    data = None if payload is None else stable_json(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=3600) as response:
            value = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Local llama-server request failed: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Local llama-server response is not an object")
    return value


def _model_id(endpoint: str) -> str:
    models = _http_json(endpoint.rstrip("/") + "/v1/models")
    data = models.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError("Local llama-server returned no model identity")
    model_id = data[0].get("id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("Local llama-server model ID is invalid")
    return model_id


def _response_content(response: Mapping[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("Local completion must contain exactly one choice")
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise ValueError("Local completion lacks text content")
    return message["content"].strip()


def _response_reasoning_content(response: Mapping[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        return ""
    message = choices[0].get("message")
    if not isinstance(message, dict):
        return ""
    value = message.get("reasoning_content")
    return value if isinstance(value, str) else ""


def _response_token_counts(responses_dir: Path) -> dict[str, int]:
    counts = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}
    for path in sorted(responses_dir.glob("*.json")):
        row = _read_json(path)
        usage = row.get("response_usage", {})
        if not isinstance(usage, dict):
            continue
        counts["prompt_tokens"] += int(usage.get("prompt_tokens", 0))
        counts["completion_tokens"] += int(usage.get("completion_tokens", 0))
        details = usage.get("completion_tokens_details", {})
        if isinstance(details, dict):
            counts["reasoning_tokens"] += int(details.get("reasoning_tokens", 0))
    return counts


def _completion_messages(
    *, user_prompt: str, validation_error: str = "", previous_content: str = ""
) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    if validation_error:
        if not previous_content:
            raise ValueError("Retry requires the previous completion content")
        messages.extend(
            [
                {"role": "assistant", "content": previous_content},
                {
                    "role": "user",
                    "content": (
                        "Your previous JSON failed deterministic validation: "
                        + validation_error
                        + ". Preserve its defensible linguistic links, correct the stated "
                        "problem, and return one complete JSON object only."
                    ),
                },
            ]
        )
    return messages


def run_local_review_task(
    *,
    task_dir: Path,
    run_id: str,
    endpoint: str = DEFAULT_ENDPOINT,
    seed: int = 7,
    max_tokens: int = 12288,
    max_attempts: int = 3,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    if not run_id or any(character.isspace() for character in run_id):
        raise ValueError("Run ID must be nonempty and contain no whitespace")
    task = _read_json(task_dir / "task_manifest.json")
    if (
        task.get("schema_version") != SCHEMA_VERSION
        or task.get("contract_version") != CONTRACT_VERSION
        or task.get("local_llm_workflow_version") != LOCAL_LLM_WORKFLOW_VERSION
        or task.get("status") != "prepared_answer_free_local_llm_task"
    ):
        raise ValueError("Local LLM task manifest is stale")
    template_path = task_dir / "inputs" / Path(task["source_paths"]["template"]).name
    compact_manifest_path = task_dir / "inputs" / Path(
        task["source_paths"]["compact_manifest"]
    ).name
    metadata_path = task_dir / "inputs" / "completed_metadata.template.jsonl"
    if (
        _sha256_file(template_path) != task["input_sha256"]["compact_template"]
        or _sha256_file(compact_manifest_path)
        != task["input_sha256"]["compact_manifest"]
        or _sha256_file(metadata_path) != task["input_sha256"]["metadata_template"]
        or _sha256_text(SYSTEM_PROMPT) != task["input_sha256"]["system_prompt"]
    ):
        raise ValueError("Local LLM task input SHA locks differ")
    shard_manifest_path = Path(task["source_paths"]["shard_manifest"])
    if _sha256_file(shard_manifest_path) != task["input_sha256"]["shard_manifest"]:
        raise ValueError("Local LLM shard manifest SHA lock differs")
    template_rows = _read_jsonl(template_path)
    metadata_rows = _read_jsonl(metadata_path)
    if len(metadata_rows) != 1:
        raise ValueError("Local LLM task metadata template differs")
    run_dir = task_dir / "completed" / run_id
    decisions_dir = run_dir / "decisions"
    responses_dir = run_dir / "responses"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    model_id = _model_id(endpoint)
    started = time.time()
    attempts_total = 0
    format_repairs: Counter[str] = Counter()
    completed: list[dict[str, Any]] = []
    initial_progress = _write_run_progress(
        run_dir=run_dir,
        task=task,
        run_id=run_id,
        total=len(template_rows),
        completed=len(list(decisions_dir.glob("*.json"))),
        failed=0,
        current_ref=None,
        started=started,
        status="running_local_blind_review",
    )
    if progress_callback is not None:
        progress_callback(initial_progress)
    for ordinal, template in enumerate(template_rows, 1):
        decision_path = decisions_dir / f"{ordinal:04d}.json"
        if decision_path.is_file():
            submission = _read_json(decision_path)
            groups, target_nulls = _validate_answer(
                {"groups": submission.get("groups"), "target_nulls": submission.get("target_nulls")},
                template,
            )
            expected = _submission_row(
                template,
                reviewer_id=task["reviewer_id"],
                groups=groups,
                target_nulls=target_nulls,
            )
            if submission != expected:
                raise ValueError(f"Stored local decision is stale: {decision_path}")
            completed.append(submission)
            continue
        verse_input = _prompt_view(template)
        user_prompt = (
            "Review this frozen single-verse input. Return complete exact accounting "
            "as the required JSON object.\n\n" + stable_json(verse_input)
        )
        validation_error = ""
        previous_content = ""
        accepted: dict[str, Any] | None = None
        for attempt in range(1, max_attempts + 1):
            attempts_total += 1
            messages = _completion_messages(
                user_prompt=user_prompt,
                validation_error=validation_error,
                previous_content=previous_content,
            )
            request_payload = {
                "model": model_id,
                "messages": messages,
                "temperature": 0,
                "seed": seed,
                "max_tokens": max_tokens,
                "stream": False,
                "response_format": {"type": "json_object"},
            }
            response = _http_json(
                endpoint.rstrip("/") + "/v1/chat/completions",
                method="POST",
                payload=request_payload,
            )
            content = _response_content(response)
            previous_content = content
            response_record = {
                "schema_version": SCHEMA_VERSION,
                "contract_version": CONTRACT_VERSION,
                "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
                "selection_id": template["selection_id"],
                "target_ref": template["target_ref"],
                "attempt": attempt,
                "model_id": model_id,
                "request_sha256": _sha256_text(stable_json(request_payload) + "\n"),
                "content": content,
                "reasoning_content": _response_reasoning_content(response),
                "response_usage": response.get("usage", {}),
                "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
                "timings": response.get("timings", {}),
            }
            _write_json(responses_dir / f"{ordinal:04d}.attempt-{attempt}.json", response_record)
            try:
                if response_record["finish_reason"] != "stop":
                    raise ValueError(
                        "Completion was truncated or did not stop normally: "
                        + str(response_record["finish_reason"])
                    )
                answer, parse_repairs = _parse_response_json(content)
                answer, format_only_repairs = _canonicalize_answer_format(answer)
                repairs = parse_repairs + format_only_repairs
                format_repairs.update(repairs)
                response_record["format_repairs"] = dict(sorted(repairs.items()))
                _write_json(
                    responses_dir / f"{ordinal:04d}.attempt-{attempt}.json",
                    response_record,
                )
                groups, target_nulls = _validate_answer(answer, template)
                accepted = _submission_row(
                    template,
                    reviewer_id=task["reviewer_id"],
                    groups=groups,
                    target_nulls=target_nulls,
                )
            except (json.JSONDecodeError, ValueError) as exc:
                validation_error = str(exc)[:1000]
                continue
            break
        if accepted is None:
            raise ValueError(
                f"Local model could not produce valid accounting for "
                f"{template['target_ref']} after {max_attempts} attempts: {validation_error}"
            )
        _write_json(decision_path, accepted)
        completed.append(accepted)
        progress = _write_run_progress(
            run_dir=run_dir,
            task=task,
            run_id=run_id,
            total=len(template_rows),
            completed=len(completed),
            failed=0,
            current_ref=str(template["target_ref"]),
            started=started,
            status="running_local_blind_review",
        )
        if progress_callback is not None:
            progress_callback(progress)

    compact_output = run_dir / "compact.completed.local.jsonl"
    if compact_output.exists():
        existing = _read_jsonl(compact_output)
        if existing != metadata_rows + completed:
            raise ValueError("Existing local compact output differs")
    else:
        _write_jsonl(compact_output, metadata_rows + completed)
    expanded_output = run_dir / "raw.local.jsonl"
    compact = _read_json(compact_manifest_path)
    if not expanded_output.exists():
        expand_compact_review(
            shard_manifest_path=shard_manifest_path,
            shard_id=task["shard_id"],
            template_path=template_path,
            compact_manifest_path=compact_manifest_path,
            filled_path=compact_output,
            output_path=expanded_output,
        )
    check = check_compact_review(
        shard_manifest_path=shard_manifest_path,
        shard_id=task["shard_id"],
        template_path=template_path,
        compact_manifest_path=compact_manifest_path,
        expanded_path=expanded_output,
    )
    elapsed = time.time() - started
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "status": "complete_merge_ready_local_blind_submission_pending_gold_comparison",
        "task_id": task["task_id"],
        "run_id": run_id,
        "review_pass": compact["review_pass"],
        "reviewer_id": task["reviewer_id"],
        "model_id": model_id,
        "endpoint": endpoint,
        "sampling": {
            "temperature": 0,
            "seed": seed,
            "max_tokens": max_tokens,
            "max_attempts": max_attempts,
        },
        "input_sha256": task["input_sha256"],
        "output_sha256": {
            compact_output.name: _sha256_file(compact_output),
            expanded_output.name: _sha256_file(expanded_output),
            Path(str(expanded_output) + ".manifest.json").name: _sha256_file(
                Path(str(expanded_output) + ".manifest.json")
            ),
        },
        "counts": {
            **task["counts"],
            "attempts": attempts_total,
            "format_repairs": dict(sorted(format_repairs.items())),
            **_response_token_counts(responses_dir),
        },
        "elapsed_seconds": elapsed,
        "compact_check_status": check["status"],
        "serialization": "UTF-8, source codepoints preserved, sorted keys, compact JSON, LF",
        "processed_count": len(completed),
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(run_dir / "receipt.json", receipt)
    progress = _write_run_progress(
        run_dir=run_dir,
        task=task,
        run_id=run_id,
        total=len(template_rows),
        completed=len(completed),
        failed=0,
        current_ref=None,
        started=started,
        status="complete_pending_gold_comparison",
    )
    if progress_callback is not None:
        progress_callback(progress)
    return receipt


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--template", type=Path, required=True)
    prepare.add_argument("--compact-manifest", type=Path, required=True)
    prepare.add_argument("--shard-manifest", type=Path, required=True)
    prepare.add_argument("--task-dir", type=Path, required=True)
    prepare.add_argument("--reviewer-id", required=True)
    run = commands.add_parser("run")
    run.add_argument("--task-dir", type=Path, required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    run.add_argument("--seed", type=int, default=7)
    run.add_argument("--max-tokens", type=int, default=12288)
    run.add_argument("--max-attempts", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "prepare":
        result = prepare_local_review_task(
            template_path=args.template,
            compact_manifest_path=args.compact_manifest,
            shard_manifest_path=args.shard_manifest,
            task_dir=args.task_dir,
            reviewer_id=args.reviewer_id,
        )
    else:
        result = run_local_review_task(
            task_dir=args.task_dir,
            run_id=args.run_id,
            endpoint=args.endpoint,
            seed=args.seed,
            max_tokens=args.max_tokens,
            max_attempts=args.max_attempts,
        )
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
