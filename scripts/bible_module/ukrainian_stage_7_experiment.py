"""Preserve the rejected pre-stage-7 Ukrainian Strong-alignment experiment.

Full derivative corpora are written only below the gitignored ``work`` tree.
Tracked reports contain contracts, hashes, aggregate metrics, safe diffs, and
the small versioned interval override file.  This module is retained as a
reproducible baseline and candidate-evidence producer; it is not the stage 7
implementation and its surface bindings must not be accepted as ground truth.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from scripts.bible_module.ukrainian_stage_7_experiment_model import (
    CONTRACT_VERSION,
    MAPPING_CONTRACT_VERSION,
    MERGE_SEPARATOR,
    SCHEMA_VERSION,
    SynthesisPart,
    alignment_form,
    join_synthesis_parts,
    lexical_score,
    maximum_weight_assignment,
    multiset_metrics,
    rebase_anchor,
    render_strong_markup,
    serialize_comment_uses,
    sha256_text,
    stable_json,
    strip_strong_markup,
    validate_partition,
    validate_strong,
    word_tokens,
)


ROOT = Path(__file__).resolve().parents[2]
STAGE4_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_4_20260801"
STAGE4_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_4_20260801"
STAGE5_WORK = ROOT / "scripts/bible_module/work/ukrainian_stage_5_20260801"
STAGE5_REPORT = ROOT / "scripts/bible_module/reports/ukrainian_stage_5_20260801"
DEFAULT_WORK = (
    ROOT / "scripts/bible_module/work/ukrainian_stage_7_experiment_20260801"
)
DEFAULT_REPORT = (
    ROOT / "scripts/bible_module/reports/ukrainian_stage_7_experiment_20260801"
)
OVERRIDES = DEFAULT_REPORT / "alignment_overrides.jsonl"
BASELINE = ROOT / "scripts/bible_module/reports/ukrainian_stage_2_20260801/baseline_manifest.json"
SOURCE = STAGE4_WORK / "normalized_wikisource_ohienko_1988_revisions.jsonl"
FORWARD = STAGE5_WORK / "source_to_target_map.jsonl"
REVERSE = STAGE5_WORK / "target_to_source_map.jsonl"
FOOTNOTE_PROJECTION = STAGE5_WORK / "footnote_projection.jsonl"
COMMONS_SCAN = ROOT / "scripts/bible_module/source_cache/commons_ohienko_1988.djvu"
STAGE4_PARSER_MANIFEST = STAGE4_REPORT / "parser_manifest.json"
STAGE4_COMMONS_MANIFEST = (
    STAGE4_REPORT / "normalized_commons_ohienko_1988_scan.manifest.json"
)
STAGE4_IA_MANIFEST = (
    STAGE4_REPORT / "normalized_internet_archive_ohienko_1988_scan.manifest.json"
)

EXPECTED_SOURCE_RECORDS = 31_160
EXPECTED_SOURCE_SPANS = 31_171
EXPECTED_TARGETS = 31_102
EXPECTED_RULES = 31_099
EXPECTED_FOOTNOTE_DEFINITIONS = 1_204
EXPECTED_FOOTNOTE_USES = 1_329
EXPECTED_VERSE_USES = 1_318
EXPECTED_HEADING_USES = 11
EXPECTED_OCR_REVIEWS = 149
EXPECTED_FORWARD_SHA = "5959d3af5422dbf8a8bed95e106c4379a55883a4f9972708c330355aed3e866f"
EXPECTED_REVERSE_SHA = "0870dd982d4eed3212610e8d1d127e55015568c11e8c0dcdcb26ddb38a27e40a"
EXPECTED_FOOTNOTE_SHA = "c1e21b8566d1b3fda8328d20374eaefe4c2a547613eb2749bf11b90e69aa678a"
EXPECTED_SCAN_SHA = "0f10b27860d3a902ea9a1b5d494937c4d11b90c57b5ed7f43e0f76462aa0ce34"
TARGET_REUSE_PENALTY = 0.9

# These references are a deterministic, deliberately small safety audit of the
# generated word bindings.  They are not correction overrides: each row records
# an observed counterexample which keeps the stage open until a source-backed
# alignment decision is supplied.
MANUAL_STRONG_AUDIT = (
    {"target_ref": "Isa.53.5", "strongs": ("H2490", "H2250", "H7495")},
    {"target_ref": "Mic.6.8", "strongs": ("H120", "H6213", "H430")},
    {"target_ref": "Luke.2.11", "strongs": ("G5088", "G4771", "G3739", "G1510", "G1138")},
    {"target_ref": "Acts.2.38", "strongs": ("G5346", "G846", "G1519")},
)

CONTROL_FILES = {
    "oshb": [STAGE4_WORK / "normalized_openscriptures_oshb_v2_2.jsonl"],
    "tahot": [
        STAGE4_WORK / "normalized_step_tahot_gen_deu.jsonl",
        STAGE4_WORK / "normalized_step_tahot_jos_est.jsonl",
        STAGE4_WORK / "normalized_step_tahot_job_sng.jsonl",
        STAGE4_WORK / "normalized_step_tahot_isa_mal.jsonl",
    ],
    "uxlc": [STAGE4_WORK / "normalized_tanach_us_uxlc_2_5_27_6.jsonl"],
    "tagnt": [
        STAGE4_WORK / "normalized_step_tagnt_mat_jhn.jsonl",
        STAGE4_WORK / "normalized_step_tagnt_act_rev.jsonl",
    ],
    "ugnt": [STAGE4_WORK / "normalized_unfoldingword_ugnt_v0_34.jsonl"],
}

NT_BOOKS = {
    "Mat",
    "Matt",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Rom",
    "1Cor",
    "2Cor",
    "Gal",
    "Eph",
    "Phil",
    "Col",
    "1Thess",
    "2Thess",
    "1Tim",
    "2Tim",
    "Titus",
    "Phlm",
    "Heb",
    "Jas",
    "1Pet",
    "2Pet",
    "1John",
    "2John",
    "3John",
    "Jude",
    "Rev",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json(value) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            line = stable_json(row) + "\n"
            handle.write(line)
            digest.update(line.encode("utf-8"))
            count += 1
    return count, digest.hexdigest()


def _ref(value: Mapping[str, Any]) -> str:
    book = "Mat" if value["book"] in {"Mat", "Matt"} else str(value["book"])
    return f"{book}.{int(value['chapter'])}.{int(value['verse'])}"


def _target_grid() -> list[dict[str, Any]]:
    grid = _read_json(BASELINE)["target_grid"]
    if grid["canon"] != "protestant_66" or grid["versification"] != "kjv_protestant":
        raise AssertionError("Stage-2 target grid contract changed")
    keys = [str(value) for value in grid["verse_keys"]]
    targets: list[dict[str, Any]] = []
    index = 0
    for book in grid["books"]:
        for chapter, last_verse in enumerate(book["chapters"], 1):
            for verse in range(1, int(last_verse) + 1):
                targets.append(
                    {
                        "order": index + 1,
                        "ref": f"{book['code']}.{chapter}.{verse}",
                        "verse_key": keys[index],
                    }
                )
                index += 1
    if len(targets) != EXPECTED_TARGETS:
        raise AssertionError("Stage-2 target grid count changed")
    return targets


def _load_overrides() -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    rows = _read_jsonl(OVERRIDES)
    if len(rows) != 12:
        raise AssertionError("Expected four split and eight control-reference overrides")
    by_rule: dict[str, dict[str, Any]] = {}
    control_refs: dict[str, str] = {}
    for row in rows:
        if (
            row["schema_version"] != SCHEMA_VERSION
            or row["contract_version"] != CONTRACT_VERSION
            or row["mapping_contract_version"] != MAPPING_CONTRACT_VERSION
        ):
            raise AssertionError("Override contract mismatch")
        if row["decision_type"] == "text_interval_override":
            intervals = [
                (int(item["start_scalar"]), int(item["end_scalar"]))
                for item in row["target_intervals"]
            ]
            separator = row["separator_interval"]
            intervals.append(
                (int(separator["start_scalar"]), int(separator["end_scalar"]))
            )
            validate_partition(int(row["source_length"]), sorted(intervals))
            by_rule[row["rule_id"]] = row
        elif row["decision_type"] == "strong_control_ref_override":
            control_refs[row["target_ref"]] = row["control_ref"]
        else:
            raise AssertionError("Unknown stage-6 override decision type")
    if len(by_rule) != 4 or len(control_refs) != 8:
        raise AssertionError("Override type counts changed")
    return rows, by_rule, control_refs


def _load_source() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
    int,
]:
    records: dict[str, dict[str, Any]] = {}
    definitions: dict[str, dict[str, Any]] = {}
    use_records: dict[str, str] = {}
    line_count = 0
    with SOURCE.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            line_count += 1
            records[record["record_id"]] = {
                "text": record["source_plain_nfc"],
                "provenance": record["provenance"],
                "source_ref": record.get("source_ref_normalized"),
                "source_order": record["source_order"],
            }
            for note in record.get("footnotes", []):
                use_records[note["use_id"]] = record["record_id"]
                current = definitions.get(note["footnote_id"])
                compact = {
                    "definition_order": note["definition_order"],
                    "footnote_id": note["footnote_id"],
                    "full_text_nfc": note["full_text_nfc"],
                    "name": note.get("name"),
                    "provenance": note["provenance"],
                    "source_revision": note["source_revision"],
                }
                if current is not None and current["full_text_nfc"] != compact["full_text_nfc"]:
                    raise AssertionError("Named footnote definition text changed between uses")
                definitions[note["footnote_id"]] = current or compact
    if line_count != EXPECTED_SOURCE_SPANS or len(definitions) != EXPECTED_FOOTNOTE_DEFINITIONS:
        raise AssertionError("Stage-4 source/footnote counts changed")
    return records, definitions, use_records, line_count


def _source_only_rule() -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    with FORWARD.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if not row.get("targets"):
                found.append(row)
    if len(found) != 1 or found[0]["operation"] != "range_transfer":
        raise AssertionError("Expected one source-only range_transfer rule")
    return found[0]


def _synthesize(
    reverse: Sequence[Mapping[str, Any]],
    records: Mapping[str, Mapping[str, Any]],
    overrides: Mapping[str, Mapping[str, Any]],
    source_only_rule: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    synthesized: list[dict[str, Any]] = []
    coverage: dict[str, list[tuple[str, int, int, str]]] = defaultdict(list)
    operation_counts: Counter[str] = Counter()
    separator_count = 0
    for target in reverse:
        raw_parts: list[tuple[str, int, int, str]] = []
        part_meta: list[dict[str, Any]] = []
        for source_part in target["source_parts"]:
            record_id = source_part["record_id"]
            source_text = str(records[record_id]["text"])
            start = int(source_part["span"]["start_scalar"])
            end = int(source_part["span"]["end_scalar"])
            if target["operation"] == "split":
                override = overrides[target["rule_id"]]
                if override["record_id"] != record_id or len(source_text) != override["source_length"]:
                    raise AssertionError("Split override source digest/length mismatch")
                interval = next(
                    item
                    for item in override["target_intervals"]
                    if item["target_ref"] == target["target_ref"]
                )
                start, end = int(interval["start_scalar"]), int(interval["end_scalar"])
            text = source_text[start:end]
            if not text:
                raise AssertionError("Empty synthesis interval")
            raw_parts.append((record_id, start, end, text))
            coverage[source_part["segment_id"]].append(
                (record_id, start, end, target["target_ref"])
            )
            part_meta.append(
                {
                    "effective_ref": source_part["effective_ref"],
                    "provenance": source_part["provenance"],
                    "record_id": record_id,
                    "reported_ref": source_part["reported_ref"],
                    "segment_id": source_part["segment_id"],
                    "source_order": source_part["source_order"],
                    "source_span": {"end_scalar": end, "start_scalar": start},
                    "text_sha256": sha256_text(text),
                }
            )
        text, mapped = join_synthesis_parts(raw_parts)
        if len(raw_parts) > 1:
            separator_count += len(raw_parts) - 1
        operation_counts[target["operation"]] += 1
        synthesized.append(
            {
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "merge_separator": MERGE_SEPARATOR if len(raw_parts) > 1 else None,
                "operation": target["operation"],
                "order": target["order"],
                "plain_text_nfc": text,
                "plain_text_sha256": sha256_text(text),
                "rule_id": target["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "source_parts": [
                    dict(part_meta[index], target_span={
                        "end_scalar": mapped[index].target_end,
                        "start_scalar": mapped[index].target_start,
                    })
                    for index in range(len(mapped))
                ],
                "target_ref": target["target_ref"],
                "verse_key": target["verse_key"],
            }
        )
    source_only: list[dict[str, Any]] = []
    for part in source_only_rule["source_parts"]:
        text = str(records[part["record_id"]]["text"])[
            int(part["span"]["start_scalar"]) : int(part["span"]["end_scalar"])
        ]
        coverage[part["segment_id"]].append(
            (
                part["record_id"],
                int(part["span"]["start_scalar"]),
                int(part["span"]["end_scalar"]),
                "source_only",
            )
        )
        source_only.append(
            {
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "operation": "range_transfer",
                "provenance": part["provenance"],
                "record_id": part["record_id"],
                "rule_id": source_only_rule["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "source_ref": part["effective_ref"],
                "source_span": part["span"],
                "source_text_nfc": text,
                "source_text_sha256": sha256_text(text),
                "status": "non_verse_source_material",
                "target_refs": [],
            }
        )
    if len(synthesized) != EXPECTED_TARGETS or len(coverage) != EXPECTED_SOURCE_SPANS:
        raise AssertionError("Source/target synthesis coverage mismatch")
    if any(not row["plain_text_nfc"] for row in synthesized):
        raise AssertionError("Every target text must be non-empty")
    split_separator_scalars = 0
    duplicate_source_scalars = 0
    for ranges in coverage.values():
        ordered = sorted(ranges, key=lambda item: (item[1], item[2], item[3]))
        if len({item[0] for item in ordered}) != 1:
            raise AssertionError("A source segment crosses source records")
        record_text = str(records[ordered[0][0]]["text"])
        for previous, current in zip(ordered, ordered[1:]):
            if previous[2] > current[1]:
                duplicate_source_scalars += previous[2] - current[1]
                continue
            gap = record_text[previous[2] : current[1]]
            if gap != MERGE_SEPARATOR:
                raise AssertionError(
                    "Split intervals may omit only one documented U+0020 boundary"
                )
            split_separator_scalars += len(gap)
    if duplicate_source_scalars:
        raise AssertionError("Source scalar intervals overlap")
    if split_separator_scalars != 4:
        raise AssertionError("Expected four documented split separator scalars")
    source_word_tokens = 0
    for row in synthesized:
        for part in row["source_parts"]:
            record_text = str(records[part["record_id"]]["text"])
            span = part["source_span"]
            source_word_tokens += len(
                word_tokens(record_text[span["start_scalar"] : span["end_scalar"]])
            )
    source_word_tokens += sum(len(word_tokens(row["source_text_nfc"])) for row in source_only)
    synthesized_word_tokens = sum(len(word_tokens(row["plain_text_nfc"])) for row in synthesized)
    source_only_word_tokens = sum(len(word_tokens(row["source_text_nfc"])) for row in source_only)
    if source_word_tokens != synthesized_word_tokens + source_only_word_tokens:
        raise AssertionError("Source word-token accounting lost or duplicated tokens")
    rules = {row["rule_id"]: row["operation"] for row in reverse}
    rules[source_only_rule["rule_id"]] = source_only_rule["operation"]
    rule_operation_counts = Counter(rules.values())
    stats = {
        "merge_separator": "U+0020",
        "merge_separator_count": separator_count,
        "operation_target_counts": dict(sorted(operation_counts.items())),
        "operation_rule_counts": dict(sorted(rule_operation_counts.items())),
        "source_only_count": len(source_only),
        "source_span_count": len(coverage),
        "source_word_token_count": source_word_tokens,
        "split_separator_scalar_count": split_separator_scalars,
        "duplicate_source_scalar_count": duplicate_source_scalars,
        "lost_source_word_token_count": 0,
        "duplicated_source_word_token_count": 0,
        "synthesized_word_token_count": synthesized_word_tokens,
        "target_count": len(synthesized),
    }
    return synthesized, source_only, stats


def _control_strongs(source: str, token: Mapping[str, Any]) -> list[dict[str, str]]:
    """Resolve control values without losing their exact source encoding.

    TAHOT extended suffixes are reduced only for comparison of base senses;
    those comparison values never become runtime Strong. UGNT's documented
    trailing-zero encoding is decoded exactly and retained with its raw value.
    """

    if source in {"oshb", "tagnt"}:
        alternatives = {
            value.upper()
            for value in re.findall(
                r"[GH]\d+",
                str(
                    token.get("extra", {})
                    .get("fields", {})
                    .get("alternative_strongs", "")
                ),
                flags=re.IGNORECASE,
            )
        }
        return [
            {
                "final": item["normalized"],
                "normalization": item["status"],
                "raw": item["raw"],
            }
            for item in token.get("strong", [])
            if item.get("status") in {"classic", "classic_source_encoding"}
            and validate_strong(item["normalized"])
            and item["normalized"].upper() not in alternatives
        ]
    if source == "ugnt":
        result: list[dict[str, str]] = []
        for raw in token.get("strong_raw", []):
            match = re.fullmatch(r"G(\d{5})", raw)
            if not match or not match.group(1).endswith("0"):
                continue
            value = f"G{int(match.group(1)) // 10}"
            if validate_strong(value):
                result.append(
                    {
                        "final": value,
                        "normalization": "ugnt_trailing_zero_source_encoding",
                        "raw": raw,
                    }
                )
        return result
    if source == "tahot":
        result: list[dict[str, str]] = []
        seen: set[str] = set()
        for raw in token.get("strong_raw", []):
            match = re.fullmatch(r"H0*(\d{1,4})(?:[A-Z])?", raw.strip("{}"))
            if match:
                value = f"H{int(match.group(1))}"
                if validate_strong(value) and value not in seen:
                    seen.add(value)
                    result.append(
                        {
                            "final": value,
                            "normalization": (
                                "classic"
                                if re.fullmatch(r"H0*\d{1,4}", raw.strip("{}"))
                                else "extended_base_sense_comparison_only"
                            ),
                            "raw": raw,
                        }
                    )
        return result
    return []


def _load_controls() -> dict[str, dict[str, list[dict[str, Any]]]]:
    controls: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for source, paths in CONTROL_FILES.items():
        refs: dict[str, list[dict[str, Any]]] = {}
        for path in paths:
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    record = json.loads(line)
                    ref = _ref(record["source_ref_normalized"])
                    refs[ref] = [
                        {
                            "alternative_strong_raw": re.findall(
                                r"[GH]\d+",
                                str(
                                    token.get("extra", {})
                                    .get("fields", {})
                                    .get("alternative_strongs", "")
                                ),
                                flags=re.IGNORECASE,
                            ),
                            "conjoin_word": str(
                                token.get("extra", {})
                                .get("fields", {})
                                .get("conjoin_word", "")
                            ),
                            "gloss": str(
                                token.get("extra", {})
                                .get("fields", {})
                                .get("english_translation", "")
                            ),
                            "strong_details": _control_strongs(source, token),
                            "surface": token["surface_nfc"],
                            "token_id": token["token_id"],
                        }
                        for token in record["tokens"]
                    ]
                    for token in refs[ref]:
                        token["strong"] = [
                            item["final"] for item in token["strong_details"]
                        ]
        controls[source] = refs
    return controls


def _candidate_refs(row: Mapping[str, Any]) -> list[str]:
    result = [row["target_ref"]]
    for part in row["source_parts"]:
        result.extend([part["effective_ref"], part["reported_ref"]])
    return list(dict.fromkeys(result))


def _select_control(
    row: Mapping[str, Any],
    controls: Mapping[str, Mapping[str, list[dict[str, Any]]]],
    control_ref_overrides: Mapping[str, str],
) -> tuple[str, str | None, list[dict[str, Any]], str, list[dict[str, Any]]]:
    is_nt = row["target_ref"].split(".", 1)[0] in NT_BOOKS
    primary_order = ["tagnt", "ugnt"] if is_nt else ["oshb", "tahot"]
    secondary = "ugnt" if is_nt else "tahot"
    refs = _candidate_refs(row)
    if row["target_ref"] in control_ref_overrides:
        refs.insert(0, control_ref_overrides[row["target_ref"]])
    for source in primary_order:
        for ref in refs:
            tokens = controls[source].get(ref, [])
            if any(token["strong"] for token in tokens):
                secondary_tokens: list[dict[str, Any]] = []
                secondary_ref: str | None = None
                for candidate in refs:
                    if controls[secondary].get(candidate):
                        secondary_tokens = controls[secondary][candidate]
                        secondary_ref = candidate
                        break
                return source, ref, tokens, secondary_ref or "", secondary_tokens
    return primary_order[0], None, [], "", []


GREEK_MAP = str.maketrans(
    {
        "α": "а", "β": "в", "γ": "г", "δ": "д", "ε": "е", "ζ": "з", "η": "і",
        "θ": "т", "ι": "і", "κ": "к", "λ": "л", "μ": "м", "ν": "н", "ξ": "кс",
        "ο": "о", "π": "п", "ρ": "р", "σ": "с", "ς": "с", "τ": "т", "υ": "у",
        "φ": "ф", "χ": "х", "ψ": "пс", "ω": "о",
    }
)
HEBREW_MAP = {
    "א": "а", "ב": "в", "ג": "г", "ד": "д", "ה": "г", "ו": "в", "ז": "з",
    "ח": "х", "ט": "т", "י": "й", "כ": "к", "ך": "к", "ל": "л", "מ": "м",
    "ם": "м", "נ": "н", "ן": "н", "ס": "с", "ע": "а", "פ": "ф", "ף": "ф",
    "צ": "ц", "ץ": "ц", "ק": "к", "ר": "р", "ש": "ш", "ת": "т",
}


def _transliterate(surface: str) -> str:
    surface = surface.split(" (", 1)[0].casefold()
    plain = "".join(
        char for char in unicodedata.normalize("NFD", surface) if unicodedata.category(char) != "Mn"
    )
    if any("\u0370" <= char <= "\u03ff" for char in plain):
        return plain.translate(GREEK_MAP)
    return "".join(HEBREW_MAP.get(char, "") for char in plain)


def _control_surface_form(surface: str) -> str:
    value = alignment_form(surface.split(" (", 1)[0])
    return "".join(char for char in value if unicodedata.category(char)[0] in {"L", "N"})


def _sequence_severity(metrics: Mapping[str, float | int]) -> str:
    if metrics["f1"] < 0.5 or metrics["jaccard"] < 0.35:
        severity = "high"
    elif metrics["f1"] < 0.75:
        severity = "medium"
    elif metrics["f1"] < 0.9:
        severity = "low"
    else:
        severity = "info"
    if metrics["ordered_f1"] < 0.45:
        severity = {
            "info": "low",
            "low": "medium",
            "medium": "high",
            "high": "high",
        }[severity]
    return severity


def _strong_sequence(tokens: Sequence[Mapping[str, Any]]) -> list[str]:
    return [strong for token in tokens for strong in token["strong"]]


def _align(
    synthesized: Sequence[dict[str, Any]],
    controls: Mapping[str, Mapping[str, list[dict[str, Any]]]],
    control_ref_overrides: Mapping[str, str],
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    selected: list[dict[str, Any]] = []
    word_frequency: Counter[str] = Counter()
    strong_frequency: Counter[str] = Counter()
    verse_words: list[set[str]] = []
    verse_strongs: list[set[str]] = []
    source_counts: Counter[str] = Counter()
    no_control: list[str] = []
    for row in synthesized:
        source, primary_ref, primary, secondary_ref, secondary = _select_control(
            row, controls, control_ref_overrides
        )
        words = word_tokens(row["plain_text_nfc"])
        word_set = {alignment_form(token.surface) for token in words}
        strong_set = {strong for token in primary for strong in token["strong"]}
        word_frequency.update(word_set)
        strong_frequency.update(strong_set)
        verse_words.append(word_set)
        verse_strongs.append(strong_set)
        source_counts[source] += 1
        if not strong_set:
            no_control.append(row["target_ref"])
        selected.append(
            {
                "primary_ref": primary_ref,
                "primary_source": source,
                "primary_tokens": primary,
                "secondary_ref": secondary_ref,
                "secondary_tokens": secondary,
            }
        )
    joint: dict[str, Counter[str]] = defaultdict(Counter)
    for words, strongs in zip(verse_words, verse_strongs, strict=True):
        for strong in strongs:
            joint[strong].update(words)
    aligned: list[dict[str, Any]] = []
    confidence_counts: Counter[str] = Counter()
    testament_markers: dict[str, int] = {"OT": 0, "NT": 0}
    testament_targets: dict[str, int] = {"OT": 0, "NT": 0}
    multi_strong_tokens = 0
    reordered_targets = 0
    repeated_strong_targets = 0
    secondary_triage: Counter[str] = Counter()
    uxlc_triage: Counter[str] = Counter()
    source_diff: list[dict[str, Any]] = []
    control_audits: list[dict[str, Any]] = []
    unaligned_tokens: list[dict[str, Any]] = []
    coverage_by_book: dict[str, Counter[str]] = defaultdict(Counter)
    coverage_by_chapter: dict[str, Counter[str]] = defaultdict(Counter)
    raw_normalization_counts: Counter[str] = Counter()
    alignment_method_counts: Counter[str] = Counter()
    manual_review_required_by_testament: Counter[str] = Counter()
    manual_review_required_targets: set[str] = set()
    excluded_alternative_strong_count = 0
    for verse_index, (row, control) in enumerate(zip(synthesized, selected, strict=True)):
        tokens = word_tokens(row["plain_text_nfc"])
        if not tokens:
            raise AssertionError("Synthesized verse has no Ukrainian surface token")
        control_occurrences: list[tuple[int, str, str, dict[str, str]]] = []
        groups: list[dict[str, Any]] = []
        for source_index, source_token in enumerate(control["primary_tokens"]):
            excluded_alternative_strong_count += len(
                source_token["alternative_strong_raw"]
            )
            if source_token["strong_details"]:
                exact_companion_index: int | None = None
                near_companion_index: int | None = None
                companion_method: str | None = None
                gloss = source_token["gloss"].casefold().strip("<>[]() .,;:")
                conjoin_numbers = re.findall(r"\d+", source_token["conjoin_word"])
                if len(conjoin_numbers) > 1:
                    documented_companion = int(conjoin_numbers[1]) - 1
                    if documented_companion != source_index:
                        if gloss == "the":
                            exact_companion_index = documented_companion
                            companion_method = "tagnt_documented_article_companion"
                        else:
                            near_companion_index = documented_companion
                            companion_method = "tagnt_documented_conjoin_near"
                groups.append(
                    {
                        "companion_method": companion_method,
                        "details": source_token["strong_details"],
                        "exact_companion_index": exact_companion_index,
                        "near_companion_index": near_companion_index,
                        "source_index": source_index,
                        "source_token": source_token,
                    }
                )
            for detail in source_token["strong_details"]:
                control_occurrences.append(
                    (
                        source_index,
                        detail["final"],
                        source_token["surface"],
                        detail,
                    )
                )
        group_indices = {group["source_index"] for group in groups}
        groups_by_index = {group["source_index"]: group for group in groups}

        def companion_of(group: Mapping[str, Any]) -> int | None:
            return (
                group["exact_companion_index"]
                if group["exact_companion_index"] is not None
                else group["near_companion_index"]
            )

        for group in groups:
            companion_index = companion_of(group)
            if companion_index is not None and companion_index not in group_indices:
                group["exact_companion_index"] = None
                group["near_companion_index"] = None
                group["companion_method"] = None
        while True:
            cycle: list[int] | None = None
            for start in group_indices:
                path: list[int] = []
                current = start
                while current in groups_by_index and companion_of(
                    groups_by_index[current]
                ) is not None:
                    if current in path:
                        cycle = path[path.index(current) :]
                        break
                    path.append(current)
                    current = int(companion_of(groups_by_index[current]))
                if cycle:
                    break
            if not cycle:
                break
            breaker = groups_by_index[min(cycle)]
            breaker["exact_companion_index"] = None
            breaker["near_companion_index"] = None
            breaker["companion_method"] = None
        for group in groups:
            if (
                [item["final"] for item in group["details"]] != ["H853"]
                or _control_surface_form(group["source_token"]["surface"])
                not in {"את", "ואת"}
            ):
                continue
            following = next(
                (
                    candidate
                    for candidate in groups
                    if candidate["source_index"] > group["source_index"]
                    and [item["final"] for item in candidate["details"]] != ["H853"]
                ),
                None,
            )
            if following is None:
                continue
            group["exact_companion_index"] = following["source_index"]
            group["near_companion_index"] = None
            group["companion_method"] = "hebrew_object_marker_companion"
        strong_by_token: dict[int, list[str]] = defaultdict(list)
        alignments: list[dict[str, Any]] = []
        assigned_load: Counter[int] = Counter()
        group_assignments: dict[int, dict[str, Any]] = {}

        def group_scores(group: Mapping[str, Any]) -> list[float]:
            source_index = group["source_index"]
            source_token = group["source_token"]
            source_surface = source_token["surface"]
            source_position = (source_index + 0.5) / max(len(control["primary_tokens"]), 1)
            transliteration = alignment_form(_transliterate(source_surface))
            result: list[float] = []
            for target_index, token in enumerate(tokens):
                form = alignment_form(token.surface)
                similarity = (
                    SequenceMatcher(None, transliteration, form).ratio()
                    if transliteration and len(form) > 2
                    else 0.0
                )
                score = sum(
                    lexical_score(
                        joint=joint[detail["final"]][form],
                        strong_frequency=strong_frequency[detail["final"]],
                        word_frequency=word_frequency[form],
                        verse_count=len(synthesized),
                        source_position=source_position,
                        target_position=(target_index + 0.5) / len(tokens),
                        transliteration_similarity=similarity,
                    )
                    for detail in group["details"]
                ) / len(group["details"])
                result.append(score)
            return result

        core_groups = [
            group
            for group in groups
            if group["exact_companion_index"] is None
            and group["near_companion_index"] is None
        ]
        if core_groups:
            slot_levels = max(1, (len(core_groups) + len(tokens) - 1) // len(tokens))
            slots = [
                (target_index, load)
                for load in range(slot_levels)
                for target_index in range(len(tokens))
            ]
            base_scores = [group_scores(group) for group in core_groups]
            weights = [
                [
                    scores[target_index] - TARGET_REUSE_PENALTY * load
                    for target_index, load in slots
                ]
                for scores in base_scores
            ]
            columns = maximum_weight_assignment(weights)
            for group, row_weights, column in zip(
                core_groups, weights, columns, strict=True
            ):
                target_index, _ = slots[column]
                alternatives = [
                    value
                    for candidate, value in enumerate(row_weights)
                    if candidate != column
                ]
                margin = row_weights[column] - max(alternatives) if alternatives else 9.0
                confidence = (
                    "high" if margin >= 0.75 else "medium" if margin >= 0.2 else "low"
                )
                assigned_load[target_index] += 1
                group_assignments[group["source_index"]] = {
                    "confidence": confidence,
                    "margin": margin,
                    "method": "global_corpus_lexical_assignment",
                    "target_index": target_index,
                }
        pending = [group for group in groups if group not in core_groups]
        while pending:
            progress = False
            for group in list(pending):
                companion_index = (
                    group["exact_companion_index"]
                    if group["exact_companion_index"] is not None
                    else group["near_companion_index"]
                )
                if companion_index not in group_assignments:
                    continue
                head_target = group_assignments[companion_index]["target_index"]
                if group["exact_companion_index"] is not None:
                    target_index = head_target
                    margin = 9.0
                    confidence = "high"
                else:
                    direction = 1 if group["source_index"] > companion_index else -1
                    candidates = [
                        index
                        for index in (
                            head_target + direction,
                            head_target + 2 * direction,
                            head_target,
                        )
                        if 0 <= index < len(tokens)
                    ]
                    scores = group_scores(group)
                    ranked = sorted(
                        [
                            (
                                scores[index]
                                - TARGET_REUSE_PENALTY * assigned_load[index],
                                index,
                            )
                            for index in candidates
                        ],
                        key=lambda item: (-item[0], item[1]),
                    )
                    best_score, target_index = ranked[0]
                    margin = best_score - ranked[1][0] if len(ranked) > 1 else 9.0
                    confidence = (
                        "high"
                        if margin >= 0.75
                        else "medium"
                        if margin >= 0.2
                        else "low"
                    )
                assigned_load[target_index] += 1
                group_assignments[group["source_index"]] = {
                    "confidence": confidence,
                    "margin": margin,
                    "method": group["companion_method"],
                    "target_index": target_index,
                }
                pending.remove(group)
                progress = True
            if not progress:
                raise AssertionError(
                    f"Unresolvable original-language companion chain: {row['target_ref']}"
                )
        previous_target_index = -1
        reordered = False
        for group in sorted(groups, key=lambda item: item["source_index"]):
            source_index = group["source_index"]
            source_token = group["source_token"]
            source_surface = source_token["surface"]
            assignment = group_assignments[source_index]
            target_index = assignment["target_index"]
            if previous_target_index > target_index:
                reordered = True
            previous_target_index = target_index
            for strong_detail in group["details"]:
                strong = strong_detail["final"]
                confidence = assignment["confidence"]
                confidence_counts[confidence] += 1
                alignment_method_counts[assignment["method"]] += 1
                if confidence == "low":
                    manual_review_required_targets.add(row["target_ref"])
                    manual_review_required_by_testament[
                        "NT"
                        if row["target_ref"].split(".", 1)[0] in NT_BOOKS
                        else "OT"
                    ] += 1
                strong_by_token[tokens[target_index].order].append(strong)
                raw_normalization_counts[strong_detail["normalization"]] += 1
                alignments.append(
                    {
                        "confidence": confidence,
                        "control_surface": source_surface,
                        "evidence": {
                            "alignment_method": assignment["method"],
                            "corpus_joint_verse_count": joint[strong][
                                alignment_form(tokens[target_index].surface)
                            ],
                            "excluded_alternative_strong_raw": source_token[
                                "alternative_strong_raw"
                            ],
                            "lexical_margin": round(assignment["margin"], 6),
                            "primary_control": control["primary_source"],
                            "primary_ref": control["primary_ref"],
                            "source_token_id": source_token["token_id"],
                        },
                        "control_strong_raw": strong_detail["raw"],
                        "normalization": strong_detail["normalization"],
                        "source_token_order": source_index + 1,
                        "strong": strong,
                        "strong_source_ids": [control["primary_source"]],
                        "target_token_order": tokens[target_index].order,
                    }
                )
        if reordered:
            reordered_targets += 1
        if len([item[1] for item in control_occurrences]) != len(
            set(item[1] for item in control_occurrences)
        ):
            repeated_strong_targets += 1
        multi_strong_tokens += sum(1 for values in strong_by_token.values() if len(values) > 1)
        marked = render_strong_markup(row["plain_text_nfc"], tokens, strong_by_token)
        if strip_strong_markup(marked) != row["plain_text_nfc"]:
            raise AssertionError("Plain-text round trip changed synthesized text")
        primary_sequence = [item[1] for item in control_occurrences]
        runtime_sequence = [
            strong
            for token in tokens
            for strong in strong_by_token.get(token.order, [])
        ]
        secondary_sequence = _strong_sequence(control["secondary_tokens"])
        primary_metrics = multiset_metrics(runtime_sequence, primary_sequence)
        metrics = multiset_metrics(runtime_sequence, secondary_sequence)
        severity = _sequence_severity(metrics) if secondary_sequence else "high"
        secondary_triage[severity] += 1
        if severity != "info":
            source_diff.append(
                {
                    "detail": "locked runtime authority retained; raw secondary textual/segmentation variant recorded",
                    "primary_ref": control["primary_ref"] or "",
                    "primary_source": control["primary_source"],
                    "rule_id": row["rule_id"],
                    "secondary_ref": control["secondary_ref"],
                    "severity": severity,
                    "status": "resolved_by_locked_runtime_authority_contract",
                    "target_ref": row["target_ref"],
                    "type": "strong_control_sequence_difference",
                }
            )
        testament = "NT" if row["target_ref"].split(".", 1)[0] in NT_BOOKS else "OT"
        book, chapter, _ = row["target_ref"].split(".")
        aligned_token_count = sum(
            1 for token in tokens if strong_by_token.get(token.order)
        )
        coverage_values = {
            "aligned_surface_token_count": aligned_token_count,
            "strong_marker_count": len(runtime_sequence),
            "surface_token_count": len(tokens),
            "target_count": 1,
            "unaligned_surface_token_count": len(tokens) - aligned_token_count,
        }
        coverage_by_book[book].update(coverage_values)
        coverage_by_chapter[f"{book}.{chapter}"].update(coverage_values)
        for token in tokens:
            if not strong_by_token.get(token.order):
                unaligned_tokens.append(
                    {
                        "alignment_form": alignment_form(token.surface),
                        "contract_version": CONTRACT_VERSION,
                        "end_scalar": token.end_scalar,
                        "order": token.order,
                        "reason": "translation_surface_without_direct_runtime_strong",
                        "schema_version": SCHEMA_VERSION,
                        "start_scalar": token.start_scalar,
                        "surface": token.surface,
                        "target_ref": row["target_ref"],
                        "verse_key": row["verse_key"],
                    }
                )
        uxlc_audit: dict[str, Any] | None = None
        if testament == "OT":
            primary_surfaces = [
                _control_surface_form(token["surface"])
                for token in control["primary_tokens"]
                if _control_surface_form(token["surface"])
            ]
            uxlc_tokens = controls["uxlc"].get(control["primary_ref"] or "", [])
            uxlc_surfaces = [
                _control_surface_form(token["surface"])
                for token in uxlc_tokens
                if _control_surface_form(token["surface"])
            ]
            uxlc_metrics = multiset_metrics(primary_surfaces, uxlc_surfaces)
            uxlc_severity = "info"
            if not uxlc_surfaces or (
                uxlc_metrics["f1"] < 0.5 or uxlc_metrics["jaccard"] < 0.35
            ):
                uxlc_severity = "high"
            elif uxlc_metrics["f1"] < 0.8 or uxlc_metrics["jaccard"] < 0.65:
                uxlc_severity = "medium"
            uxlc_triage[uxlc_severity] += 1
            uxlc_audit = {
                "metrics": uxlc_metrics,
                "ref": control["primary_ref"],
                "resolution": "independent_surface_control_recorded_primary_oshb_retained",
                "severity_before_resolution": uxlc_severity,
            }
            if uxlc_severity != "info":
                source_diff.append(
                    {
                        "detail": "independent UXLC surface difference recorded; OSHB Strong authority retained",
                        "primary_ref": control["primary_ref"] or "",
                        "primary_source": control["primary_source"],
                        "rule_id": row["rule_id"],
                        "secondary_ref": control["primary_ref"] or "",
                        "severity": uxlc_severity,
                        "status": "resolved_by_locked_runtime_authority_contract",
                        "target_ref": row["target_ref"],
                        "type": "uxlc_independent_surface_difference",
                    }
                )
        previous_primary = []
        if (
            verse_index > 0
            and synthesized[verse_index - 1]["target_ref"].split(".", 1)[0]
            == book
        ):
            previous_primary = _strong_sequence(
                selected[verse_index - 1]["primary_tokens"]
            )
        next_primary = []
        if (
            verse_index + 1 < len(selected)
            and synthesized[verse_index + 1]["target_ref"].split(".", 1)[0]
            == book
        ):
            next_primary = _strong_sequence(
                selected[verse_index + 1]["primary_tokens"]
            )
        previous_metrics = multiset_metrics(runtime_sequence, previous_primary)
        next_metrics = multiset_metrics(runtime_sequence, next_primary)
        neighbor_better = any(
            candidate["f1"] >= 0.5
            and candidate["f1"] >= primary_metrics["f1"] + 0.1
            for candidate in (previous_metrics, next_metrics)
        )
        if neighbor_better:
            raise AssertionError("A neighboring control sequence outscored the own verse")
        control_audits.append(
            {
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "neighbor_metrics": {
                    "next": next_metrics,
                    "previous": previous_metrics,
                },
                "own_primary_metrics": primary_metrics,
                "own_secondary_metrics": metrics,
                "primary_ref": control["primary_ref"],
                "primary_source": control["primary_source"],
                "rule_id": row["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "secondary_ref": control["secondary_ref"],
                "secondary_severity_before_resolution": severity,
                "status": "resolved_by_locked_runtime_authority_contract",
                "target_ref": row["target_ref"],
                "verse_key": row["verse_key"],
            }
        )
        testament_markers[testament] += len(primary_sequence)
        testament_targets[testament] += 1
        aligned.append(
            {
                "alignments": alignments,
                "contract_version": CONTRACT_VERSION,
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "marked_text_nfc": marked,
                "marked_text_sha256": sha256_text(marked),
                "operation": row["operation"],
                "order": row["order"],
                "plain_text_nfc": row["plain_text_nfc"],
                "plain_text_sha256": row["plain_text_sha256"],
                "primary_control": control["primary_source"],
                "primary_control_ref": control["primary_ref"],
                "rule_id": row["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "secondary_audit": {
                    "neighbor_metrics": {
                        "next": next_metrics,
                        "previous": previous_metrics,
                    },
                    "primary_metrics": primary_metrics,
                    "ref": control["secondary_ref"],
                    "resolution": "locked_runtime_authority_contract",
                    "secondary_metrics": metrics,
                    "severity_before_resolution": severity,
                    "uxlc_surface": uxlc_audit,
                },
                "strong_marker_count": len(primary_sequence),
                "surface_tokens": [
                    {
                        "alignment_form": alignment_form(token.surface),
                        "confidence": (
                            min(
                                (
                                    item["confidence"]
                                    for item in alignments
                                    if item["target_token_order"] == token.order
                                ),
                                key={"low": 0, "medium": 1, "high": 2}.get,
                            )
                            if strong_by_token.get(token.order)
                            else "not_applicable"
                        ),
                        "end_scalar": token.end_scalar,
                        "kind": "word",
                        "order": token.order,
                        "start_scalar": token.start_scalar,
                        "strong_candidates": strong_by_token.get(token.order, []),
                        "strong_final": strong_by_token.get(token.order, []),
                        "strong_raw": [
                            item["control_strong_raw"]
                            for item in alignments
                            if item["target_token_order"] == token.order
                        ],
                        "strong_relation": (
                            "none"
                            if not strong_by_token.get(token.order)
                            else "single"
                            if len(strong_by_token[token.order]) == 1
                            else "simultaneous"
                        ),
                        "strong_source_ids": sorted(
                            {
                                source_id
                                for item in alignments
                                if item["target_token_order"] == token.order
                                for source_id in item["strong_source_ids"]
                            }
                        ),
                        "surface": token.surface,
                        "token_id": f"{row['verse_key']}:{token.order}",
                    }
                    for token in tokens
                ],
                "target_ref": row["target_ref"],
                "verse_key": row["verse_key"],
            }
        )
    invalid = [
        alignment["strong"]
        for row in aligned
        for alignment in row["alignments"]
        if not validate_strong(alignment["strong"])
    ]
    if invalid:
        raise AssertionError("Invalid or dangling Strong values")
    if no_control:
        raise AssertionError(f"Target positions without primary Strong control: {no_control}")
    stats = {
        "alignment_confidence": dict(sorted(confidence_counts.items())),
        "alignment_method_counts": dict(sorted(alignment_method_counts.items())),
        "book_coverage": [
            {"book": key, **dict(sorted(value.items()))}
            for key, value in coverage_by_book.items()
        ],
        "chapter_coverage": [
            {"chapter_ref": key, **dict(sorted(value.items()))}
            for key, value in coverage_by_chapter.items()
        ],
        "control_target_counts": dict(sorted(source_counts.items())),
        "excluded_alternative_strong_count": excluded_alternative_strong_count,
        "invalid_strong_count": len(invalid),
        "multi_strong_surface_token_count": multi_strong_tokens,
        "manual_review_required_strong_count": confidence_counts["low"],
        "manual_review_required_target_count": len(manual_review_required_targets),
        "manual_review_required_by_testament": {
            key: manual_review_required_by_testament[key] for key in ["OT", "NT"]
        },
        "no_primary_control_target_count": len(no_control),
        "no_primary_control_targets": no_control,
        "reordered_alignment_target_count": reordered_targets,
        "repeated_strong_target_count": repeated_strong_targets,
        "raw_normalization_counts": dict(sorted(raw_normalization_counts.items())),
        "secondary_triage_before_resolution": dict(sorted(secondary_triage.items())),
        "uxlc_surface_triage_before_resolution": dict(sorted(uxlc_triage.items())),
        "strong_marker_count": sum(testament_markers.values()),
        "surface_token_count": sum(
            value["surface_token_count"] for value in coverage_by_book.values()
        ),
        "aligned_surface_token_count": sum(
            value["aligned_surface_token_count"] for value in coverage_by_book.values()
        ),
        "unaligned_surface_token_count": len(unaligned_tokens),
        "testaments": {
            key: {
                "strong_marker_count": testament_markers[key],
                "target_count": testament_targets[key],
            }
            for key in ["OT", "NT"]
        },
        "unresolved_critical_count": 0,
        "unresolved_high_count": 1,
    }
    source_diff.append(
        {
            "detail": (
                f"{stats['manual_review_required_strong_count']} low-margin Strong "
                f"bindings across {stats['manual_review_required_target_count']} "
                "targets require source-backed review; deterministic safety samples "
                "contain semantically incompatible surface bindings"
            ),
            "primary_ref": "",
            "primary_source": "oshb/tagnt",
            "rule_id": "",
            "secondary_ref": "",
            "severity": "high",
            "status": "unresolved_manual_review_required",
            "target_ref": "MULTIPLE",
            "type": "strong_surface_binding_ambiguity",
        }
    )
    return aligned, stats, source_diff, control_audits, unaligned_tokens


def _project_footnotes(
    projections: Sequence[Mapping[str, Any]],
    synthesized: Sequence[Mapping[str, Any]],
    definitions: Mapping[str, Mapping[str, Any]],
    use_records: Mapping[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    by_target = {row["target_ref"]: row for row in synthesized}
    uses: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    for projection in projections:
        if not projection.get("target_candidates"):
            headings.append(
                {
                    **projection,
                    "anchor_status": "non_verse_source_material",
                    "contract_version": CONTRACT_VERSION,
                    "schema_version": SCHEMA_VERSION,
                }
            )
            continue
        target = by_target[projection["target_ref"]]
        parts = [
            SynthesisPart(
                record_id=part["record_id"],
                source_start=part["source_span"]["start_scalar"],
                source_end=part["source_span"]["end_scalar"],
                target_start=part["target_span"]["start_scalar"],
                target_end=part["target_span"]["end_scalar"],
                text="",
            )
            for part in target["source_parts"]
            if part["record_id"] == use_records[projection["use_id"]]
        ]
        anchor = projection["source_anchor"]
        try:
            start, end = rebase_anchor(
                anchor["start_scalar"], anchor["end_scalar"], parts
            )
        except ValueError as error:
            raise ValueError(
                stable_json(
                    {
                        "anchor": anchor,
                        "parts": [asdict(part) for part in parts],
                        "target_ref": projection.get("target_ref"),
                        "use_id": projection["use_id"],
                        "use_record_id": use_records.get(projection["use_id"]),
                    }
                )
            ) from error
        if not (0 <= start <= end <= len(target["plain_text_nfc"])):
            raise AssertionError("Rebased footnote anchor is outside target text")
        definition = definitions[projection["footnote_id"]]
        uses.append(
            {
                "anchor_status": "resolved_by_proven_source_target_interval",
                "contract_version": CONTRACT_VERSION,
                "definition_name": definition["name"],
                "footnote_id": projection["footnote_id"],
                "full_text_nfc": projection["full_text_nfc"],
                "mapping_contract_version": MAPPING_CONTRACT_VERSION,
                "mapping_rule_id": projection["mapping_rule_id"],
                "marker": projection["marker"],
                "operation": projection["operation"],
                "provenance": projection["provenance"],
                "schema_version": SCHEMA_VERSION,
                "source_anchor": projection["source_anchor"],
                "source_order": projection["source_order"],
                "target_anchor": {"end_scalar": end, "start_scalar": start},
                "target_order": projection["target_order"],
                "target_ref": projection["target_ref"],
                "use_id": projection["use_id"],
            }
        )
    uses.sort(key=lambda row: (row["target_order"], row["source_order"], row["use_id"]))
    headings.sort(key=lambda row: (row["source_order"], row["use_id"]))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for use in uses:
        grouped[use["target_ref"]].append(use)
    comments: list[dict[str, Any]] = []
    markerless = 0
    for target in synthesized:
        target_uses = grouped.get(target["target_ref"], [])
        markerless += sum(1 for use in target_uses if not use["marker"])
        comment = serialize_comment_uses(target_uses)
        if re.search(r"(?:^|\s)[GH]\d+(?:\s|$)", comment):
            raise AssertionError("Strong markup leaked into target_comment")
        if len(target["plain_text_nfc"]) >= 12 and target["plain_text_nfc"] in comment:
            raise AssertionError("Canonical verse text leaked into target_comment")
        comments.append(
            {
                "comment_sha256": sha256_text(comment),
                "contract_version": CONTRACT_VERSION,
                "order": target["order"],
                "schema_version": SCHEMA_VERSION,
                "target_comment": comment,
                "target_ref": target["target_ref"],
                "use_ids": [use["use_id"] for use in target_uses],
                "verse_key": target["verse_key"],
            }
        )
    if len(uses) != EXPECTED_VERSE_USES or len(headings) != EXPECTED_HEADING_USES:
        raise AssertionError("Footnote use projection count changed")
    if len({row["use_id"] for row in uses + headings}) != EXPECTED_FOOTNOTE_USES:
        raise AssertionError("Footnote use was lost or duplicated")
    stats = {
        "comment_target_count": len(comments),
        "empty_comment_count": sum(not row["target_comment"] for row in comments),
        "footnote_definition_count": len(definitions),
        "heading_non_verse_use_count": len(headings),
        "markerless_use_count": markerless,
        "named_definition_count": sum(1 for row in definitions.values() if row["name"]),
        "named_use_count": sum(1 for row in uses + headings if definitions[row["footnote_id"]]["name"]),
        "projected_use_count": len(uses),
        "total_use_count": len(uses) + len(headings),
        "unresolved_anchor_count": 0,
    }
    definition_rows = [
        {
            "contract_version": CONTRACT_VERSION,
            "schema_version": SCHEMA_VERSION,
            **row,
        }
        for row in sorted(definitions.values(), key=lambda item: (item["definition_order"], item["footnote_id"]))
    ]
    return uses, headings, comments, {"stats": stats, "definitions": definition_rows}


def _manual_reviews(
    override_rows: Sequence[Mapping[str, Any]],
    headings: Sequence[Mapping[str, Any]],
    aligned: Sequence[Mapping[str, Any]],
    strong_stats: Mapping[str, Any],
) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    with (STAGE4_REPORT / "source_diff.csv").open(encoding="utf-8", newline="") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["type"] == "footnote_text_not_confirmed_by_hidden_ocr"
        ]
    if len(rows) != EXPECTED_OCR_REVIEWS:
        raise AssertionError("Stage-4 OCR-review inventory changed")
    for index, row in enumerate(rows, 1):
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": [
                    {"digest": EXPECTED_SCAN_SHA, "kind": "commons_exact_edition_scan", "locator": f"Ivan Ohienko Bible.djvu/{row['page_or_record']}"},
                    {"digest": row["evidence"].split("footnote_text_sha256=", 1)[1].split(";", 1)[0], "kind": "normalized_footnote_text"},
                ],
                "footnote_id": row["footnote_id"],
                "issue_id": f"uk6-footnote-ocr-{index:03d}",
                "resolution": "visually_matches_commons_scan_retained_without_change",
                "schema_version": SCHEMA_VERSION,
                "severity": "info",
                "status": "resolved",
                "type": "footnote_ocr_review",
            }
        )
    for row in override_rows:
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": row["evidence"],
                "issue_id": row["override_id"],
                "resolution": row["decision"],
                "rule_id": row["rule_id"],
                "schema_version": SCHEMA_VERSION,
                "severity": "high",
                "status": "resolved",
                "type": (
                    "split_boundary_review"
                    if row["decision_type"] == "text_interval_override"
                    else "strong_control_ref_review"
                ),
            }
        )
    for row in headings:
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": [{"kind": "stage_5_non_verse_binding", "mapping_rule_id": row.get("mapping_rule_id")}],
                "footnote_id": row["footnote_id"],
                "issue_id": f"uk6-heading-{row['use_id'].rsplit(':', 1)[-1]}",
                "resolution": "retained_as_non_verse_source_material_no_new_binding_evidence",
                "schema_version": SCHEMA_VERSION,
                "severity": "medium",
                "status": "resolved_expected",
                "type": "heading_footnote_review",
            }
        )
    reviews.append(
        {
            "affected_strong_count": strong_stats[
                "manual_review_required_strong_count"
            ],
            "affected_target_count": strong_stats[
                "manual_review_required_target_count"
            ],
            "contract_version": CONTRACT_VERSION,
            "evidence": [
                {
                    "kind": "deterministic_alignment_confidence_inventory",
                    "method": "global_assignment_margin_below_0.2",
                },
                {
                    "kind": "manual_safety_sample",
                    "target_refs": [row["target_ref"] for row in MANUAL_STRONG_AUDIT],
                },
            ],
            "issue_id": "uk6-strong-binding-aggregate",
            "resolution": (
                "source-backed per-word decisions or an independently validated "
                "alignment model are still required"
            ),
            "schema_version": SCHEMA_VERSION,
            "severity": "high",
            "status": "unresolved_manual_review_required",
            "type": "strong_surface_binding_ambiguity",
        }
    )
    aligned_by_ref = {row["target_ref"]: row for row in aligned}
    for index, audit in enumerate(MANUAL_STRONG_AUDIT, 1):
        row = aligned_by_ref[audit["target_ref"]]
        tokens = {token["order"]: token for token in row["surface_tokens"]}
        observed = [
            {
                "control_surface": alignment["control_surface"],
                "strong": alignment["strong"],
                "surface": tokens[alignment["target_token_order"]]["surface"],
                "target_token_order": alignment["target_token_order"],
            }
            for alignment in row["alignments"]
            if alignment["strong"] in audit["strongs"]
        ]
        reviews.append(
            {
                "contract_version": CONTRACT_VERSION,
                "evidence": [
                    {
                        "digest": row["marked_text_sha256"],
                        "kind": "generated_marked_text",
                        "locator": audit["target_ref"],
                    },
                    {
                        "kind": "original_language_control_tokens",
                        "primary_control": row["primary_control"],
                        "primary_ref": row["primary_control_ref"],
                    },
                ],
                "issue_id": f"uk6-strong-binding-sample-{index:03d}",
                "observed_bindings": observed,
                "resolution": (
                    "manual semantic inspection found at least one incompatible "
                    "surface binding; no correction was guessed"
                ),
                "schema_version": SCHEMA_VERSION,
                "severity": "info",
                "status": "evidence_for_open_aggregate",
                "target_ref": audit["target_ref"],
                "type": "strong_surface_binding_audit_sample",
            }
        )
    return sorted(reviews, key=lambda row: (row["type"], row["issue_id"]))


def _manifest(
    *,
    artifact: str,
    input_hashes: Mapping[str, str],
    output_path: Path,
    processed: int,
    skipped: int = 0,
    status: str = "complete",
    serialization: str = "UTF-8; LF; JSON keys sorted; compact separators",
) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": processed, "skipped": skipped},
        "deterministic_serialization": serialization,
        "generated_on": "2026-08-01",
        "input_sha256": dict(sorted(input_hashes.items())),
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": _sha256_file(output_path),
        "schema_version": SCHEMA_VERSION,
        "status": status,
    }


def generate(*, work_dir: Path, report_dir: Path) -> dict[str, Any]:
    work_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    override_rows, overrides, control_ref_overrides = _load_overrides()
    if report_dir != DEFAULT_REPORT:
        shutil.copyfile(OVERRIDES, report_dir / "alignment_overrides.jsonl")
    input_hashes = {
        "commons_exact_scan": _sha256_file(COMMONS_SCAN),
        "stage4_commons_manifest": _sha256_file(STAGE4_COMMONS_MANIFEST),
        "stage4_ia_manifest": _sha256_file(STAGE4_IA_MANIFEST),
        "stage4_parser_manifest": _sha256_file(STAGE4_PARSER_MANIFEST),
        "stage4_source": _sha256_file(SOURCE),
        "stage5_forward": _sha256_file(FORWARD),
        "stage5_reverse": _sha256_file(REVERSE),
        "stage5_footnotes": _sha256_file(FOOTNOTE_PROJECTION),
    }
    if input_hashes["stage5_forward"] != EXPECTED_FORWARD_SHA:
        raise AssertionError("Stage-5 forward mapping changed")
    if input_hashes["stage5_reverse"] != EXPECTED_REVERSE_SHA:
        raise AssertionError("Stage-5 reverse mapping changed")
    if input_hashes["stage5_footnotes"] != EXPECTED_FOOTNOTE_SHA:
        raise AssertionError("Stage-5 footnote projection changed")
    if input_hashes["commons_exact_scan"] != EXPECTED_SCAN_SHA:
        raise AssertionError("Exact Commons scan changed")
    grid = _target_grid()
    reverse = _read_jsonl(REVERSE)
    if [(row["target_ref"], row["verse_key"]) for row in reverse] != [
        (row["ref"], row["verse_key"]) for row in grid
    ]:
        raise AssertionError("Exact 31,102 target-key equality failed")
    records, definitions, use_records, _ = _load_source()
    synthesized, source_only, synthesis_stats = _synthesize(
        reverse, records, overrides, _source_only_rule()
    )
    synthesized_path = work_dir / "synthesized_text.jsonl"
    source_only_path = work_dir / "source_only_material.jsonl"
    _write_jsonl(synthesized_path, synthesized)
    _write_jsonl(source_only_path, source_only)
    control_input_hashes = {
        path.name: _sha256_file(path)
        for paths in CONTROL_FILES.values()
        for path in paths
    }
    controls = _load_controls()
    aligned, strong_stats, source_diff, control_audits, unaligned_tokens = _align(
        synthesized, controls, control_ref_overrides
    )
    aligned_path = work_dir / "strong_aligned_text.jsonl"
    control_audit_path = work_dir / "strong_control_audit.jsonl"
    unaligned_path = work_dir / "unaligned_surface_tokens.jsonl"
    _write_jsonl(aligned_path, aligned)
    _write_jsonl(control_audit_path, control_audits)
    _write_jsonl(unaligned_path, unaligned_tokens)
    projections = _read_jsonl(FOOTNOTE_PROJECTION)
    uses, headings, comments, footnote_bundle = _project_footnotes(
        projections, synthesized, definitions, use_records
    )
    uses_path = work_dir / "footnote_uses.jsonl"
    headings_path = work_dir / "heading_footnotes.jsonl"
    comments_path = work_dir / "target_comments.jsonl"
    definitions_path = work_dir / "footnote_definitions.jsonl"
    _write_jsonl(uses_path, uses)
    _write_jsonl(headings_path, headings)
    _write_jsonl(comments_path, comments)
    _write_jsonl(definitions_path, footnote_bundle["definitions"])
    manual_reviews = _manual_reviews(override_rows, headings, aligned, strong_stats)
    _write_jsonl(report_dir / "manual_review.jsonl", manual_reviews)
    with (report_dir / "source_diff.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["type", "severity", "status", "target_ref", "rule_id", "primary_source", "primary_ref", "secondary_ref", "detail"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(source_diff, key=lambda row: (row["target_ref"], row["type"])))
    preservation = {
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(aligned), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; JSON keys sorted; compact separators",
        "input_sha256": {"synthesized_text": _sha256_file(synthesized_path)},
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": {"strong_aligned_text": _sha256_file(aligned_path)},
        "plain_text_mismatch_count": 0,
        "round_trip_count": len(aligned),
        "schema_version": SCHEMA_VERSION,
        "source_token_accounting": synthesis_stats,
        "status": "pass",
    }
    _write_json(report_dir / "plain_text_preservation_report.json", preservation)
    strong_report = {
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(aligned), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; JSON keys sorted; compact separators",
        "input_sha256": {
            **control_input_hashes,
            "synthesized_text": _sha256_file(synthesized_path),
        },
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": {"strong_aligned_text": _sha256_file(aligned_path)},
        "schema_version": SCHEMA_VERSION,
        "statistics": strong_stats,
        "status": "incomplete_manual_review_required",
    }
    _write_json(report_dir / "strong_coverage_report.json", strong_report)
    footnote_stats = {
        "contract_version": CONTRACT_VERSION,
        "counts": {"error": 0, "processed": len(projections), "skipped": 0},
        "deterministic_serialization": "UTF-8; LF; JSON keys sorted; compact separators",
        "input_sha256": {"stage5_footnotes": input_hashes["stage5_footnotes"]},
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "output_sha256": {"target_comments": _sha256_file(comments_path), "uses": _sha256_file(uses_path)},
        "schema_version": SCHEMA_VERSION,
        "statistics": footnote_bundle["stats"],
        "status": "pass",
    }
    _write_json(report_dir / "footnote_comment_stats.json", footnote_stats)
    _write_json(
        report_dir / "synthesized_text.manifest.json",
        _manifest(artifact="synthesized_text.jsonl", input_hashes=input_hashes, output_path=synthesized_path, processed=len(synthesized)),
    )
    _write_json(
        report_dir / "strong_alignment.manifest.json",
        _manifest(
            artifact="strong_aligned_text.jsonl",
            input_hashes={**input_hashes, **control_input_hashes},
            output_path=aligned_path,
            processed=len(aligned),
            status="incomplete_manual_review_required",
        ),
    )
    _write_json(
        report_dir / "strong_control_audit.manifest.json",
        _manifest(
            artifact="strong_control_audit.jsonl",
            input_hashes={**input_hashes, **control_input_hashes},
            output_path=control_audit_path,
            processed=len(control_audits),
            serialization=(
                "UTF-8; LF; one sorted compact JSON object per line; "
                "target order"
            ),
        ),
    )
    _write_json(
        report_dir / "unaligned_surface_tokens.manifest.json",
        _manifest(
            artifact="unaligned_surface_tokens.jsonl",
            input_hashes={"strong_aligned_text": _sha256_file(aligned_path)},
            output_path=unaligned_path,
            processed=len(unaligned_tokens),
            serialization=(
                "UTF-8; LF; one sorted compact JSON object per line; "
                "target/token order"
            ),
        ),
    )
    _write_json(
        report_dir / "footnote_comment_projection.manifest.json",
        _manifest(artifact="target_comments.jsonl", input_hashes=input_hashes, output_path=comments_path, processed=len(comments)),
    )
    summary = {
        "contract_version": CONTRACT_VERSION,
        "footnotes": footnote_bundle["stats"],
        "mapping_contract_version": MAPPING_CONTRACT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "source_diff_count": len(source_diff),
        "stage_status": "incomplete_manual_review_required",
        "strong": strong_stats,
        "synthesis": synthesis_stats,
        "unresolved_critical_count": 0,
        "unresolved_high_count": strong_stats["unresolved_high_count"],
    }
    _write_json(work_dir / "generation_summary.json", summary)
    (report_dir / "report.ru.md").write_text(_report_ru(summary), encoding="utf-8", newline="\n")
    (report_dir / "validation_log.md").write_text(_validation_log(summary), encoding="utf-8", newline="\n")
    sidecars = [
        (
            "alignment_overrides.manifest.json",
            report_dir / "alignment_overrides.jsonl",
            len(override_rows),
            {"commons_scan": EXPECTED_SCAN_SHA, **input_hashes, **control_input_hashes},
            "UTF-8; LF; one sorted compact JSON object per line; stable decision order",
        ),
        (
            "manual_review.manifest.json",
            report_dir / "manual_review.jsonl",
            len(manual_reviews),
            {"commons_scan": EXPECTED_SCAN_SHA, **input_hashes},
            "UTF-8; LF; one sorted compact JSON object per line; type/issue_id order",
        ),
        (
            "source_diff.manifest.json",
            report_dir / "source_diff.csv",
            len(source_diff),
            {**input_hashes, **control_input_hashes},
            "UTF-8; LF; RFC 4180 CSV; fixed header; target_ref/type order",
        ),
        (
            "report.manifest.json",
            report_dir / "report.ru.md",
            1,
            {"generation_summary": _sha256_file(work_dir / "generation_summary.json")},
            "UTF-8; LF; deterministic Markdown template",
        ),
        (
            "validation_log.manifest.json",
            report_dir / "validation_log.md",
            1,
            {"generation_summary": _sha256_file(work_dir / "generation_summary.json")},
            "UTF-8; LF; deterministic Markdown template",
        ),
    ]
    for name, output, processed, sidecar_inputs, serialization in sidecars:
        _write_json(
            report_dir / name,
            _manifest(
                artifact=output.name,
                input_hashes=sidecar_inputs,
                output_path=output,
                processed=processed,
                serialization=serialization,
            ),
        )
    return summary


def _report_ru(summary: Mapping[str, Any]) -> str:
    strong = summary["strong"]
    synthesis = summary["synthesis"]
    footnotes = summary["footnotes"]
    return f"""# Этап 7 — добавление индексов Стронга в украинский текст

- `schema_version`: {SCHEMA_VERSION}
- `contract_version`: `{CONTRACT_VERSION}`
- mapping: `{MAPPING_CONTRACT_VERSION}` (не изменён)
- статус: **не завершён — требуется доказательное ручное Strong-выравнивание**

## Текст

Wikisource OH1988 назначен единственным базовым текстом; точный Commons/IA scan и независимые normalized источники этапа 4 использованы только как контроль. Синтезировано {synthesis['target_count']} непустых target-позиций; учтены {synthesis['source_span_count']} source spans и {synthesis['source_word_token_count']} source word tokens без потери и дублирования. Merge использует U+0020 ({synthesis['merge_separator_count']} вставок). Четыре split основаны на versioned scalar overrides и точном Commons DjVu; четыре разделительных U+0020 исключены только на доказанных печатных границах. `2Chr.14.14` сохранён отдельно как source-only range material.

## Strong

Кандидатная разметка построена непосредственно между украинскими surface tokens и OSHB/TAHOT/UXLC для OT, TAGNT/UGNT для NT; KJV, TR, RST и соседние стихи не использовались как источник Strong. Сохранено {strong['strong_marker_count']} Strong occurrences: OT {strong['testaments']['OT']['strong_marker_count']}, NT {strong['testaments']['NT']['strong_marker_count']}. Покрыто {strong['aligned_surface_token_count']} из {strong['surface_token_count']} украинских surface tokens; {strong['unaligned_surface_token_count']} tokens без прямого Strong сохранены отдельным полным списком. Invalid/dangling Strong: 0. Plain-text round-trip: {synthesis['target_count']} / {synthesis['target_count']}.

Автоматическая corpus/position модель детерминирована и сохраняет raw Strong, normalization, control token и score evidence, но не является достаточным доказательством окончательной пословной связи. Её собственный low-margin шлюз выявил {strong['manual_review_required_strong_count']} Strong occurrences в {strong['manual_review_required_target_count']} target-позициях (OT {strong['manual_review_required_by_testament']['OT']}, NT {strong['manual_review_required_by_testament']['NT']}). Ручная safety-выборка зафиксировала несовместимые surface bindings в `Isa.53.5`, `Mic.6.8`, `Luke.2.11` и `Acts.2.38`. Исправления не угадывались; весь агрегат оставлен unresolved high в `manual_review.jsonl` и `source_diff.csv`. Поэтому `strong_aligned_text.jsonl` является только незавершённым кандидатом и не разрешён для этапа 7.

## Сноски и comments

Разрешено {footnotes['projected_use_count']} target anchors через доказанные source→target интервалы. Все {footnotes['total_use_count']} uses сохранены ровно по одному разу; {footnotes['heading_non_verse_use_count']} heading uses остались non-verse. Определений: {footnotes['footnote_definition_count']}; named definitions: {footnotes['named_definition_count']}; uses не дедуплицированы. Пустой comment используется для стиха без сносок, blocks разделяются двумя LF.

Все 149 OCR-review текстов визуально сверены с точным Commons scan и оставлены без изменения. Exit criteria этапа 7 не выполнены из-за Strong-привязок; дорожная карта не закрыта. SQLite и этап 8 не выполнялись.
"""


def _validation_log(summary: Mapping[str, Any]) -> str:
    return f"""# Ukrainian stage 7 Strong-alignment validation log

- Date: 2026-08-01
- Contract: `{CONTRACT_VERSION}`
- Mapping SHA-256 forward: `{EXPECTED_FORWARD_SHA}`
- Mapping SHA-256 reverse: `{EXPECTED_REVERSE_SHA}`
- Target texts: {summary['synthesis']['target_count']} / {EXPECTED_TARGETS}
- Source spans: {summary['synthesis']['source_span_count']} / {EXPECTED_SOURCE_SPANS}
- Footnote uses: {summary['footnotes']['total_use_count']} / {EXPECTED_FOOTNOTE_USES}
- Plain-text round-trip mismatches: 0
- Invalid/dangling Strong: 0
- Strong bindings requiring manual review: {summary['strong']['manual_review_required_strong_count']} across {summary['strong']['manual_review_required_target_count']} targets
- Unresolved critical/high: 0 / {summary['unresolved_high_count']}
- Double deterministic generation: pending final validation run
- Repository-wide validation: pending final validation run
- Smoke: N/A — no runtime, routes, deep links, Flutter, or database changes
- Stage status: incomplete_manual_review_required; roadmap not closed
- Stage 8 / SQLite: not executed
"""


def verify_existing(*, work_dir: Path, report_dir: Path) -> None:
    required = {
        "synthesized_text.manifest.json": work_dir / "synthesized_text.jsonl",
        "strong_alignment.manifest.json": work_dir / "strong_aligned_text.jsonl",
        "strong_control_audit.manifest.json": work_dir / "strong_control_audit.jsonl",
        "unaligned_surface_tokens.manifest.json": work_dir
        / "unaligned_surface_tokens.jsonl",
        "footnote_comment_projection.manifest.json": work_dir / "target_comments.jsonl",
    }
    for manifest_name, output in required.items():
        manifest = _read_json(report_dir / manifest_name)
        if manifest["contract_version"] != CONTRACT_VERSION or manifest["schema_version"] != SCHEMA_VERSION:
            raise AssertionError(f"Contract mismatch in {manifest_name}")
        if manifest["output_sha256"] != _sha256_file(output):
            raise AssertionError(f"Output digest mismatch in {manifest_name}")
    for manifest_name in [
        "alignment_overrides.manifest.json",
        "manual_review.manifest.json",
        "source_diff.manifest.json",
        "report.manifest.json",
        "validation_log.manifest.json",
    ]:
        manifest = _read_json(report_dir / manifest_name)
        output = report_dir / manifest["artifact"]
        if manifest["output_sha256"] != _sha256_file(output):
            raise AssertionError(f"Report digest mismatch in {manifest_name}")
    if _sha256_file(FORWARD) != EXPECTED_FORWARD_SHA or _sha256_file(REVERSE) != EXPECTED_REVERSE_SHA:
        raise AssertionError("Stage-5 mapping hashes changed")
    summary = _read_json(work_dir / "generation_summary.json")
    if summary["unresolved_critical_count"]:
        raise AssertionError("Unresolved critical issue")
    if summary["stage_status"] != "incomplete_manual_review_required":
        raise AssertionError(
            "Rejected experiment status does not expose the Strong review gate"
        )
    if summary["unresolved_high_count"] < 1:
        raise AssertionError("Known Strong binding ambiguity was hidden")
    print(
        stable_json(
            {
                "stage": 7,
                "status": "structurally_verified_incomplete_manual_review_required",
                "unresolved_high_count": summary["unresolved_high_count"],
            }
        )
    )


def verify_determinism() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix="ukrainian-stage-7-experiment-a-"
    ) as first, tempfile.TemporaryDirectory(
        prefix="ukrainian-stage-7-experiment-b-"
    ) as second:
        first_root, second_root = Path(first), Path(second)
        generate(work_dir=first_root / "work", report_dir=first_root / "report")
        generate(work_dir=second_root / "work", report_dir=second_root / "report")
        first_files = sorted(path.relative_to(first_root) for path in first_root.rglob("*") if path.is_file())
        second_files = sorted(path.relative_to(second_root) for path in second_root.rglob("*") if path.is_file())
        if first_files != second_files:
            raise AssertionError("Deterministic generation file inventory mismatch")
        mismatches = [str(path) for path in first_files if _sha256_file(first_root / path) != _sha256_file(second_root / path)]
        if mismatches:
            raise AssertionError(f"Deterministic generation digest mismatch: {mismatches}")
        return {"artifact_count": len(first_files), "status": "deterministic"}


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--determinism", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.check:
        verify_existing(work_dir=args.work_dir, report_dir=args.report_dir)
    elif args.determinism:
        print(stable_json(verify_determinism()))
    else:
        print(stable_json(generate(work_dir=args.work_dir, report_dir=args.report_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
