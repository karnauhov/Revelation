"""Run a small sealed local-LLM benchmark and compare link/null decisions."""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time
from typing import Any, Mapping, Sequence

from scripts.bible_module.ukrainian_stage_7_local_llm import (
    LOCAL_LLM_WORKFLOW_VERSION,
    SYSTEM_PROMPT,
    _canonicalize_answer_format,
    _completion_messages,
    _http_json,
    _model_id,
    _parse_response_json,
    _prompt_view,
    _response_content,
    _response_reasoning_content,
    _validate_answer,
)
from scripts.bible_module.ukrainian_stage_7_local_llm_batch import (
    _load_expanded_shard,
)
from scripts.bible_module.ukrainian_stage_7_model import (
    CONTRACT_VERSION,
    SCHEMA_VERSION,
    stable_json,
)


BENCHMARK_VERSION = "ukrainian-stage-7-local-llm-sealed-benchmark-v1"
DEFAULT_REFS = ("Ruth.4.18", "Ruth.3.5", "Ruth.4.8")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Non-object JSONL row in {path}")
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


def _local_signatures(
    *, template: Mapping[str, Any], answer: Mapping[str, Any]
) -> dict[str, tuple[Any, ...]]:
    signatures: dict[str, tuple[Any, ...]] = {}
    for group in answer["groups"]:
        signature = (
            group["relation"],
            tuple(sorted(group["original_indices"])),
            tuple(sorted(group["target_indices"])),
            group.get("null_reason"),
        )
        for index in group["original_indices"]:
            signatures["original:" + index] = signature
        target_signature = ("aligned", tuple(sorted(group["original_indices"])))
        for index in group["target_indices"]:
            signatures["target:" + index] = target_signature
    for target_null in answer["target_nulls"]:
        signatures["target:" + target_null["target_index"]] = (
            target_null["target_status"],
            (),
        )
    expected = {
        *("original:" + str(row["index"]) for row in template["original_index"]),
        *("target:" + str(row["index"]) for row in template["target_index"]),
    }
    if set(signatures) != expected:
        raise ValueError("Local benchmark signature accounting differs")
    return signatures


def _reference_signatures(
    *, template: Mapping[str, Any], reference: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, tuple[Any, ...]], set[str]]:
    original_by_token = {
        str(row["original_token_id"]): str(row["index"])
        for row in template["original_index"]
    }
    target_by_token = {
        str(row["target_token_id"]): str(row["index"])
        for row in template["target_index"]
    }
    signatures: dict[str, tuple[Any, ...]] = {}
    critical: set[str] = set()
    for item in template["original_index"]:
        local = str(item["index"])
        row = reference["original:" + str(item["decision_id"])]
        signatures["original:" + local] = (
            row["relation"],
            tuple(sorted(original_by_token[str(value)] for value in row["group_original_token_ids"])),
            tuple(sorted(target_by_token[str(value)] for value in row["target_token_ids"])),
            row.get("null_reason"),
        )
        if row.get("severity") == "critical":
            critical.add("original:" + local)
    for item in template["target_index"]:
        local = str(item["index"])
        row = reference["target:" + str(item["accounting_id"])]
        signatures["target:" + local] = (
            row["target_status"],
            tuple(sorted(original_by_token[str(value)] for value in row["linked_original_token_ids"])),
        )
        if row.get("severity") == "critical":
            critical.add("target:" + local)
    return signatures, critical


def _same_index(answer: Mapping[str, Any]) -> tuple[int, int]:
    groups = [group for group in answer["groups"] if group["relation"] == "one_to_one"]
    same = sum(
        str(group["original_indices"][0])[1:]
        == str(group["target_indices"][0])[1:]
        for group in groups
    )
    return same, len(groups)


def run_benchmark(
    *,
    template_path: Path,
    reference_path: Path,
    output_dir: Path,
    endpoint: str,
    variant_id: str,
    refs: Sequence[str],
    seed: int,
    max_tokens: int,
    max_attempts: int,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"Benchmark output already exists: {output_dir}")
    templates = {str(row["target_ref"]): row for row in _read_jsonl(template_path)}
    if len(set(refs)) != len(refs) or any(ref not in templates for ref in refs):
        raise ValueError("Benchmark refs are duplicate or outside the frozen template")
    _, reference = _load_expanded_shard(reference_path)
    model_id = _model_id(endpoint)
    output_dir.mkdir(parents=True)
    accepted_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    response_count = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_reasoning_tokens = 0
    repair_counts: Counter[str] = Counter()
    started = time.time()
    for verse_ordinal, ref in enumerate(refs, 1):
        template = templates[ref]
        verse_input = _prompt_view(template)
        user_prompt = (
            "Review this frozen single-verse input. Return complete exact accounting "
            "as the required JSON object.\n\n" + stable_json(verse_input)
        )
        validation_error = ""
        previous_content = ""
        answer: dict[str, Any] | None = None
        for attempt in range(1, max_attempts + 1):
            messages = _completion_messages(
                user_prompt=user_prompt,
                validation_error=validation_error,
                previous_content=previous_content,
            )
            payload = {
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
                payload=payload,
            )
            response_count += 1
            usage = response.get("usage", {})
            total_prompt_tokens += int(usage.get("prompt_tokens", 0))
            total_completion_tokens += int(usage.get("completion_tokens", 0))
            completion_details = usage.get("completion_tokens_details", {})
            if isinstance(completion_details, dict):
                total_reasoning_tokens += int(
                    completion_details.get("reasoning_tokens", 0)
                )
            content = _response_content(response)
            previous_content = content
            _write_json(
                output_dir / "responses" / f"{verse_ordinal:03d}.attempt-{attempt}.json",
                {
                    "target_ref": ref,
                    "attempt": attempt,
                    "model_id": model_id,
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
                    "content": content,
                    "reasoning_content": _response_reasoning_content(response),
                    "usage": usage,
                    "timings": response.get("timings", {}),
                },
            )
            try:
                if response.get("choices", [{}])[0].get("finish_reason") != "stop":
                    raise ValueError("completion did not stop normally")
                parsed, parse_repairs = _parse_response_json(content)
                parsed, format_only_repairs = _canonicalize_answer_format(parsed)
                repairs = parse_repairs + format_only_repairs
                repair_counts.update(repairs)
                groups, nulls = _validate_answer(parsed, template)
                answer = {"groups": groups, "target_nulls": nulls}
            except (json.JSONDecodeError, ValueError) as exc:
                validation_error = str(exc)[:1000]
                continue
            break
        if answer is None:
            raise ValueError(f"Benchmark failed at {ref}: {validation_error}")
        accepted_rows.append({"target_ref": ref, "answer": answer})
        local = _local_signatures(template=template, answer=answer)
        expected, critical = _reference_signatures(template=template, reference=reference)
        matched = {key for key in local if local[key] == expected[key]}
        same, one_to_one = _same_index(answer)
        comparison_rows.append(
            {
                "target_ref": ref,
                "decisions": len(local),
                "matching_decisions": len(matched),
                "agreement": len(matched) / len(local),
                "critical_decisions": len(critical),
                "matching_critical_decisions": len(critical & matched),
                "same_local_index_one_to_one": same,
                "one_to_one": one_to_one,
            }
        )
    _write_jsonl(output_dir / "accepted_answers.jsonl", accepted_rows)
    total = sum(row["decisions"] for row in comparison_rows)
    matched = sum(row["matching_decisions"] for row in comparison_rows)
    critical_total = sum(row["critical_decisions"] for row in comparison_rows)
    critical_matched = sum(row["matching_critical_decisions"] for row in comparison_rows)
    same_total = sum(row["same_local_index_one_to_one"] for row in comparison_rows)
    one_to_one_total = sum(row["one_to_one"] for row in comparison_rows)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "contract_version": CONTRACT_VERSION,
        "local_llm_workflow_version": LOCAL_LLM_WORKFLOW_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "status": "complete_sealed_sample_benchmark",
        "variant_id": variant_id,
        "model_id": model_id,
        "endpoint": endpoint,
        "sampling": {
            "temperature": 0,
            "seed": seed,
            "max_tokens": max_tokens,
            "max_attempts": max_attempts,
        },
        "target_refs": list(refs),
        "per_verse": comparison_rows,
        "metrics": {
            "decisions": total,
            "matching_decisions": matched,
            "link_null_agreement": matched / total,
            "critical_decisions": critical_total,
            "matching_critical_decisions": critical_matched,
            "critical_recall": critical_matched / critical_total if critical_total else 1.0,
            "one_to_one": one_to_one_total,
            "same_local_index_one_to_one": same_total,
            "same_local_index_ratio": same_total / one_to_one_total if one_to_one_total else 0.0,
            "response_count": response_count,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "reasoning_tokens": total_reasoning_tokens,
            "elapsed_seconds": time.time() - started,
            "format_repairs": dict(sorted(repair_counts.items())),
        },
        "input_sha256": {
            "template": _sha256_file(template_path),
            "reference": _sha256_file(reference_path),
            "system_prompt": sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest(),
        },
        "output_sha256": {
            "accepted_answers.jsonl": _sha256_file(output_dir / "accepted_answers.jsonl")
        },
        "processed_count": len(refs),
        "skipped_count": 0,
        "error_count": 0,
    }
    _write_json(output_dir / "benchmark.manifest.json", manifest)
    return manifest


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080")
    parser.add_argument("--variant-id", required=True)
    parser.add_argument("--refs", default=",".join(DEFAULT_REFS))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-tokens", type=int, default=6144)
    parser.add_argument("--max-attempts", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_benchmark(
        template_path=args.template,
        reference_path=args.reference,
        output_dir=args.output_dir,
        endpoint=args.endpoint,
        variant_id=args.variant_id,
        refs=[value.strip() for value in args.refs.split(",") if value.strip()],
        seed=args.seed,
        max_tokens=args.max_tokens,
        max_attempts=args.max_attempts,
    )
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
