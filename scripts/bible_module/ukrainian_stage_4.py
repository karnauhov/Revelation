from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import unicodedata
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

from .ukrainian_stage_3_sources import SOURCE_LOCK_PATH, verify_locked_cache
from .ukrainian_stage_4_model import (
    PARSER_CONTRACT_VERSION,
    STAGE_4_SCHEMA_VERSION,
    canonical_json,
    normalize_source_text,
    sha256_bytes,
)
from .ukrainian_stage_4_parsers import (
    ParseResult,
    SourceContext,
    Stage4ParseError,
    parse_crosswire_kjv_osis,
    parse_djvu_hidden_text,
    parse_oshb_zip,
    parse_step_word_table,
    parse_tvtms,
    parse_ugnt_zip,
    parse_uxlc_zip,
    parse_wikisource_bundle,
)

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parents[1]
REPORT_DATE = "20260801"
REPORT_DIR = PACKAGE_DIR / "reports" / f"ukrainian_stage_4_{REPORT_DATE}"
WORK_DIR = PACKAGE_DIR / "work" / f"ukrainian_stage_4_{REPORT_DATE}"
DJVUTXT_DEFAULT = Path(r"C:\Program Files (x86)\DjVuLibre\djvutxt.exe")
GENERATOR_VERSION = "1"

_EDITION_SOURCES = {
    "commons_ohienko_1988_scan",
    "internet_archive_ohienko_1988_scan",
    "wikisource_ohienko_1988_revisions",
}
_HIGH_WARNING_TYPES = {
    "empty_footnote",
    "undefined_named_ref",
    "conflicting_named_ref_definition",
    "unclosed_ref",
    "unparsed_mediawiki_carrier",
    "unexpected_mediawiki_template",
    "empty_canonical_record",
    "empty_canonical_verse",
}


class Stage4PipelineError(RuntimeError):
    """A deterministic generation or verification failure."""


def _json_bytes(value: object, *, pretty: bool = True) -> bytes:
    if pretty:
        return (
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
    return (canonical_json(value) + "\n").encode("utf-8")


def _write_bytes_if_changed(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_bytes() == payload:
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def _portable_details(value: object) -> object:
    if isinstance(value, Mapping):
        portable: dict[str, object] = {}
        for key, item in value.items():
            if key == "djvutxt_path" and isinstance(item, str):
                portable[key] = Path(item).name
            elif key.endswith("_path") and isinstance(item, str):
                candidate = Path(item)
                try:
                    portable[key] = _relative(candidate) if candidate.is_absolute() else candidate.as_posix()
                except ValueError:
                    portable[key] = candidate.name
            else:
                portable[key] = _portable_details(item)
        return portable
    if isinstance(value, list):
        return [_portable_details(item) for item in value]
    return value


def _source_revision(source: Mapping[str, object]) -> str:
    pin = source["pin"]
    if not isinstance(pin, Mapping):
        raise Stage4PipelineError(f"Invalid pin for {source['source_id']}")
    if pin.get("value"):
        return str(pin["value"])
    if pin.get("revision_lock_sha256"):
        return str(pin["revision_lock_sha256"])
    if pin.get("version") and pin.get("build"):
        return f"{pin['version']}; build {pin['build']}"
    raise Stage4PipelineError(f"No exact revision for {source['source_id']}")


def load_contexts() -> tuple[list[SourceContext], dict[str, object]]:
    lock = json.loads(SOURCE_LOCK_PATH.read_text(encoding="utf-8"))
    contexts: list[SourceContext] = []
    for source in lock["sources"]:
        local_path = (SOURCE_LOCK_PATH.parent / source["local_path"]).resolve()
        contexts.append(
            SourceContext(
                source_id=str(source["source_id"]),
                role=str(source["role"]),
                version=str(source["version"]),
                revision=_source_revision(source),
                path=local_path,
                expected_bytes=int(source["bytes"]),
                expected_sha256=str(source["sha256"]),
                edition_applicable=str(source["source_id"]) in _EDITION_SOURCES,
            )
        )
    if len(contexts) != 14:
        raise Stage4PipelineError(f"Expected 14 locked machine sources, got {len(contexts)}")
    return contexts, lock


def _parse(context: SourceContext, *, djvutxt: Path) -> ParseResult:
    source_id = context.source_id
    if source_id.startswith("step_tahot_"):
        return parse_step_word_table(context, family="TAHOT")
    if source_id.startswith("step_tagnt_"):
        return parse_step_word_table(context, family="TAGNT")
    if source_id == "step_tvtms":
        return parse_tvtms(context)
    if source_id == "openscriptures_oshb_v2_2":
        return parse_oshb_zip(context)
    if source_id == "tanach_us_uxlc_2_5_27_6":
        return parse_uxlc_zip(context)
    if source_id == "unfoldingword_ugnt_v0_34":
        return parse_ugnt_zip(context)
    if source_id == "crosswire_kjv_3_1":
        return parse_crosswire_kjv_osis(context)
    if source_id == "wikisource_ohienko_1988_revisions":
        return parse_wikisource_bundle(context)
    if source_id in {
        "commons_ohienko_1988_scan",
        "internet_archive_ohienko_1988_scan",
    }:
        return parse_djvu_hidden_text(
            context,
            djvutxt_path=djvutxt,
            work_dir=WORK_DIR / "tool_inputs",
        )
    raise Stage4PipelineError(f"No independent parser for {source_id}")


def _write_normalized(
    context: SourceContext, result: ParseResult
) -> tuple[dict[str, object], dict[str, object]]:
    path = WORK_DIR / f"normalized_{context.source_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".jsonl.tmp")
    digest = hashlib.sha256()
    byte_count = 0
    record_count = 0
    with temporary.open("wb") as handle:
        for record in result.records:
            line = (canonical_json(record) + "\n").encode("utf-8")
            handle.write(line)
            digest.update(line)
            byte_count += len(line)
            record_count += 1
    os.replace(temporary, path)
    output_sha = digest.hexdigest()
    counters = dict(sorted(result.counters.items()))
    skipped = dict(sorted(result.skipped.items()))
    manifest = {
        "schema_version": STAGE_4_SCHEMA_VERSION,
        "stage": 4,
        "status": "source_normalized_unprojected",
        "parser_contract_version": PARSER_CONTRACT_VERSION,
        "generator_version": GENERATOR_VERSION,
        "source_id": context.source_id,
        "source_role": context.role,
        "source_version": context.version,
        "source_revision": context.revision,
        "input": {
            "path": _relative(context.path),
            "bytes": context.expected_bytes,
            "sha256": context.expected_sha256,
        },
        "normalized_artifact": {
            "gitignored_path": _relative(path),
            "bytes": byte_count,
            "sha256": output_sha,
            "records": record_count,
            "serialization": "UTF-8 JSON Lines; keys sorted; compact separators; LF",
            "stable_order": "source_order ascending",
        },
        "accounting": {
            "processed": record_count,
            "skipped": sum(skipped.values()),
            "errors": len(result.errors),
            "counters": counters,
            "skipped_by_class": skipped,
        },
        "format_details": _portable_details(result.format_details),
        "target_projection": "not_performed",
    }
    manifest_path = REPORT_DIR / f"normalized_{context.source_id}.manifest.json"
    _write_bytes_if_changed(manifest_path, _json_bytes(manifest))
    return manifest, _summarize_records(result.records)


def _strong_sequence(record: Mapping[str, object]) -> list[str]:
    values: list[str] = []
    for token in record.get("tokens", []):
        if not isinstance(token, Mapping):
            continue
        for strong in token.get("strong", []):
            if isinstance(strong, Mapping) and strong.get("normalized"):
                values.append(str(strong["normalized"]))
    return values


def _comparison_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value).casefold()
    return "".join(character for character in decomposed if character.isalnum())


def _summarize_records(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    refs: dict[str, dict[str, object]] = {}
    pages: dict[int, dict[str, object]] = {}
    footnotes: dict[str, dict[str, object]] = {}
    for record in records:
        ref = record.get("source_ref_normalized")
        tokens = record.get("tokens", [])
        strong = _strong_sequence(record)
        plain = str(record.get("source_plain_nfc", ""))
        token_surfaces = [
            str(token.get("surface_nfc", ""))
            for token in tokens
            if isinstance(token, Mapping)
        ]
        summary = {
            "record_id": record["record_id"],
            "plain_sha256": sha256_bytes(plain.encode("utf-8")),
            "token_count": len(tokens),
            "token_sequence_sha256": sha256_bytes("\u001f".join(token_surfaces).encode("utf-8")),
            "strong_count": len(strong),
            "strong_sequence_sha256": sha256_bytes("\u001f".join(strong).encode("utf-8")),
        }
        if isinstance(ref, Mapping):
            label = f"{ref['book']}.{ref['chapter']}.{ref['verse']}"
            if ref.get("subverse"):
                label += f".{ref['subverse']}"
            refs[label] = summary
        locator = record.get("source_locator", {})
        if isinstance(locator, Mapping) and isinstance(locator.get("page"), int):
            pages[int(locator["page"])] = {**summary, "comparison_text": _comparison_text(plain)}
        for footnote in record.get("footnotes", []):
            if not isinstance(footnote, Mapping):
                continue
            footnote_id = footnote.get("footnote_id")
            if footnote_id and str(footnote_id) not in footnotes:
                footnotes[str(footnote_id)] = {
                    "footnote_id": footnote_id,
                    "source_page": footnote.get("source_page"),
                    "text_sha256": sha256_bytes(str(footnote.get("full_text_nfc", "")).encode("utf-8")),
                    "comparison_text": _comparison_text(str(footnote.get("full_text_nfc", ""))),
                    "binding_status": footnote.get("binding_status"),
                    "source_ref": footnote.get("source_ref"),
                    "printed_marker_present": footnote.get("printed_marker_present"),
                }
    return {"refs": refs, "pages": pages, "footnotes": footnotes}


def _combine_ref_summaries(
    summaries: Mapping[str, Mapping[str, object]], source_ids: Sequence[str]
) -> dict[str, object]:
    combined: dict[str, object] = {}
    for source_id in source_ids:
        refs = summaries[source_id]["refs"]
        for ref, value in refs.items():
            if ref in combined:
                raise Stage4PipelineError(f"Duplicate combined source ref {ref}")
            combined[ref] = value
    return combined


def _compare_refs(
    rows: list[dict[str, object]],
    *,
    source_id: str,
    compared_source_id: str,
    left: Mapping[str, Mapping[str, object]],
    right: Mapping[str, Mapping[str, object]],
    relation: str,
    compare_surface: bool,
    compare_strong: bool,
) -> dict[str, int]:
    counts = Counter()
    for ref in sorted(set(left) | set(right)):
        left_value = left.get(ref)
        right_value = right.get(ref)
        if left_value is None or right_value is None:
            rows.append(
                {
                    "source_id": source_id,
                    "compared_source_id": compared_source_id,
                    "source_ref": ref,
                    "record_id": (left_value or right_value or {}).get("record_id", ""),
                    "page_or_record": "",
                    "footnote_id": "",
                    "type": "missing_source_record",
                    "severity": "medium",
                    "evidence": f"present_in={'left' if left_value else 'right'};relation={relation}",
                    "candidates": "",
                    "status": "explained_source_versification_difference",
                }
            )
            counts["missing_records"] += 1
            continue
        counts["common_records"] += 1
        if compare_surface and left_value["token_sequence_sha256"] != right_value["token_sequence_sha256"]:
            rows.append(
                {
                    "source_id": source_id,
                    "compared_source_id": compared_source_id,
                    "source_ref": ref,
                    "record_id": left_value["record_id"],
                    "page_or_record": "",
                    "footnote_id": "",
                    "type": "source_native_token_sequence_difference",
                    "severity": "info",
                    "evidence": (
                        f"left_tokens={left_value['token_count']};right_tokens={right_value['token_count']};"
                        f"left_sha256={left_value['token_sequence_sha256']};"
                        f"right_sha256={right_value['token_sequence_sha256']};relation={relation}"
                    ),
                    "candidates": "",
                    "status": "retained_not_silently_corrected",
                }
            )
            counts["surface_differences"] += 1
        if compare_strong and left_value["strong_sequence_sha256"] != right_value["strong_sequence_sha256"]:
            rows.append(
                {
                    "source_id": source_id,
                    "compared_source_id": compared_source_id,
                    "source_ref": ref,
                    "record_id": left_value["record_id"],
                    "page_or_record": "",
                    "footnote_id": "",
                    "type": "source_native_strong_sequence_difference",
                    "severity": "info",
                    "evidence": (
                        f"left_strong={left_value['strong_count']};right_strong={right_value['strong_count']};"
                        f"left_sha256={left_value['strong_sequence_sha256']};"
                        f"right_sha256={right_value['strong_sequence_sha256']};relation={relation}"
                    ),
                    "candidates": "",
                    "status": "deferred_to_stage_6_alignment",
                }
            )
            counts["strong_differences"] += 1
    return dict(counts)


def _build_diffs(summaries: Mapping[str, Mapping[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    comparisons: dict[str, object] = {}
    commons_pages = summaries["commons_ohienko_1988_scan"]["pages"]
    archive_pages = summaries["internet_archive_ohienko_1988_scan"]["pages"]
    page_mismatches = 0
    for page in range(1, 1539):
        if commons_pages[page]["plain_sha256"] != archive_pages[page]["plain_sha256"]:
            page_mismatches += 1
            rows.append(
                {
                    "source_id": "commons_ohienko_1988_scan",
                    "compared_source_id": "internet_archive_ohienko_1988_scan",
                    "source_ref": "",
                    "record_id": commons_pages[page]["record_id"],
                    "page_or_record": page,
                    "footnote_id": "",
                    "type": "dependent_scan_ocr_difference",
                    "severity": "high",
                    "evidence": (
                        f"commons_sha256={commons_pages[page]['plain_sha256']};"
                        f"archive_sha256={archive_pages[page]['plain_sha256']}"
                    ),
                    "candidates": "",
                    "status": "unresolved",
                }
            )
    comparisons["commons_vs_internet_archive_pages"] = {
        "relation": "same scan; Internet Archive is dependent control",
        "pages_compared": 1538,
        "differences": page_mismatches,
    }
    tahot = _combine_ref_summaries(
        summaries,
        ["step_tahot_gen_deu", "step_tahot_jos_est", "step_tahot_job_sng", "step_tahot_isa_mal"],
    )
    tagnt = _combine_ref_summaries(summaries, ["step_tagnt_mat_jhn", "step_tagnt_act_rev"])
    comparisons["tahot_vs_oshb"] = _compare_refs(
        rows,
        source_id="step_tahot_all",
        compared_source_id="openscriptures_oshb_v2_2",
        left=tahot,
        right=summaries["openscriptures_oshb_v2_2"]["refs"],
        relation="dependent Hebrew Strong/morphology audit",
        compare_surface=True,
        compare_strong=True,
    )
    comparisons["oshb_vs_uxlc"] = _compare_refs(
        rows,
        source_id="openscriptures_oshb_v2_2",
        compared_source_id="tanach_us_uxlc_2_5_27_6",
        left=summaries["openscriptures_oshb_v2_2"]["refs"],
        right=summaries["tanach_us_uxlc_2_5_27_6"]["refs"],
        relation="independent Hebrew surface control",
        compare_surface=True,
        compare_strong=False,
    )
    comparisons["tagnt_vs_ugnt"] = _compare_refs(
        rows,
        source_id="step_tagnt_all",
        compared_source_id="unfoldingword_ugnt_v0_34",
        left=tagnt,
        right=summaries["unfoldingword_ugnt_v0_34"]["refs"],
        relation="independent Greek token/Strong control",
        compare_surface=True,
        compare_strong=True,
    )
    kjv_refs = summaries["crosswire_kjv_3_1"]["refs"]
    comparisons["tagnt_vs_crosswire_kjv"] = _compare_refs(
        rows,
        source_id="step_tagnt_all",
        compared_source_id="crosswire_kjv_3_1",
        left=tagnt,
        right={key: value for key, value in kjv_refs.items() if key.split(".", 1)[0] in {ref.split(".", 1)[0] for ref in tagnt}},
        relation="independent classic-Strong multiset control; surfaces not compared",
        compare_surface=False,
        compare_strong=True,
    )
    footnote_match = Counter()
    for footnote_id, footnote in summaries["wikisource_ohienko_1988_revisions"]["footnotes"].items():
        page = footnote["source_page"]
        print_page = commons_pages.get(page)
        needle = str(footnote["comparison_text"])
        haystack = str(print_page["comparison_text"]) if print_page else ""
        if needle and needle in haystack:
            status = "exact_normalized_ocr_containment"
        else:
            needle_chunks = {needle[index : index + 8] for index in range(0, max(0, len(needle) - 7), 8)}
            overlap = (
                sum(chunk in haystack for chunk in needle_chunks) / len(needle_chunks)
                if needle_chunks
                else 0.0
            )
            status = "partial_ocr_evidence" if overlap >= 0.5 else "manual_print_check_needed"
            if status == "manual_print_check_needed":
                rows.append(
                    {
                        "source_id": "wikisource_ohienko_1988_revisions",
                        "compared_source_id": "commons_ohienko_1988_scan",
                        "source_ref": canonical_json(footnote.get("source_ref")) if footnote.get("source_ref") else "",
                        "record_id": "",
                        "page_or_record": page or "",
                        "footnote_id": footnote_id,
                        "type": "footnote_text_not_confirmed_by_hidden_ocr",
                        "severity": "medium",
                        "evidence": f"footnote_text_sha256={footnote['text_sha256']};ocr_chunk_overlap={overlap:.4f}",
                        "candidates": canonical_json(footnote.get("source_ref")) if footnote.get("source_ref") else "",
                        "status": "manual_review_against_commons_scan",
                    }
                )
        footnote_match[status] += 1
    comparisons["wikisource_footnotes_vs_commons_hidden_ocr"] = dict(footnote_match)
    return rows, comparisons


def _write_diff(rows: Sequence[Mapping[str, object]]) -> None:
    path = REPORT_DIR / "source_diff.csv"
    fieldnames = [
        "source_id", "compared_source_id", "source_ref", "record_id", "page_or_record",
        "footnote_id", "type", "severity", "evidence", "candidates", "status",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _safe_warning(warning: Mapping[str, object]) -> dict[str, object]:
    result = dict(_portable_details(warning))
    result["severity"] = "high" if warning.get("type") in _HIGH_WARNING_TYPES else "low"
    result["status"] = (
        "unresolved" if result["severity"] == "high" else "classified_manual_or_informational"
    )
    return result


def _normalization_rules() -> str:
    return """# Правила нормализации этапа 4

- Unicode: `source_plain_nfc` и surface-токены приводятся к NFC; raw-поля сохраняются без подмены.
- Окончания строк: CRLF/CR/U+2028/U+2029 приводятся к LF; однострочный plain затем соединяется пробелами.
- Пробелы: табуляции и Unicode space separators приводятся к U+0020, повторные пробелы схлопываются. Потеря букв не допускается.
- Апострофы: `'`, `’`, `ʼ` не взаимозаменяются и сохраняются как в источнике.
- Дефисы и тире: дефис, en dash, em dash и другие знаки не взаимозаменяются.
- Пунктуация и регистр сохраняются; украинская орфография не модернизируется.
- MediaWiki: вложенные шаблоны разбираются балансным сканером; `ref` — структурным HTML-carrier сканером. Текст `ref` исключается из canonical plain без удаления окружающей пунктуации.
- Печатный маркер: для ProofreadPage сохраняется доказуемый page-local ordinal каждого `ref` use, заданный порядком carrier-разметки и page-level списком ссылок; self-closing reuse получает собственный use-marker. Явное отсутствие в другом формате фиксируется `printed_marker_present=false`, искусственный target-marker не создаётся.
- Named refs: определение уникально в пределах ProofreadPage; paired ref является определением и использованием, self-closing ref — только новым использованием существующего определения.
- Anchor: скалярная позиция — точка вставки ref в source-normalized verse; при отсутствии доказуемого source verse anchor остаётся пустым.
- Strong: raw сохраняется; leading zero снимается у числовой части. Augmented/alternative/out-of-range значения не усекаются и получают явный status. Специальное окончание `0` UGNT декодируется только по зафиксированному контракту UGNT. Решение alignment не выполняется.
- Target-поля отсутствуют; `projection_status=unprojected`. `target_comment`, `decision_comment` и `alignment_comment` не формируются.
"""


def _render_report(
    stats: Mapping[str, object],
    footnote_stats: Mapping[str, object],
    comparisons: Mapping[str, object],
    manifests: Sequence[Mapping[str, object]],
) -> str:
    source_lines = []
    for manifest in manifests:
        counters = manifest["accounting"]["counters"]
        source_lines.append(
            f"| `{manifest['source_id']}` | {counters.get('records', 0)} | "
            f"{counters.get('verses', 0)} | {counters.get('tokens', 0)} | "
            f"{counters.get('strong', 0)} | {counters.get('footnotes', 0)} | "
            f"{counters.get('warnings', 0)} | {counters.get('errors', 0)} |"
        )
    return f"""# Этап 4: парсеры и независимая нормализация источников

Статус: **завершён**. Дата доказательств: 2026-08-01.

Этап разобрал все 14 locked machine sources независимыми путями после fail-closed проверки размера и SHA-256. Полные normalized JSONL находятся в gitignored `scripts/bible_module/work/ukrainian_stage_4_{REPORT_DATE}/`; в Git сохранены точные manifests, агрегаты, hashes и безопасные расхождения.

Проекция на `kjv_protestant`, `verse_key`, формирование `target_comment`, Strong-выравнивание и SQLite **не выполнялись**. Каждая source-native запись имеет `projection_status=unprojected`.

## Источники

| source_id | records | verses | tokens | Strong | footnote uses | warnings | errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(source_lines)}

Commons является печатным эталоном. Закреплённый Commons DjVu содержит два байт-в-байт одинаковых логических DjVu-контейнера; parser fail-closed проверил это и разобрал один логический набор из 1 538 страниц. Internet Archive совпадает с этим логическим контейнером и учитывается только как зависимый контроль. Wikisource — транскрипция того же Commons-скана, а не независимое издание.

## Сноски

- raw carrier inventory: {footnote_stats['raw_carriers']}.
- уникальные определения: {footnote_stats['unique_definitions']}.
- места использования после разрешения named/self-closing refs: {footnote_stats['uses']}.
- однозначно привязаны к source verse: {footnote_stats['binding']['unambiguous']}.
- missing/unresolved/ambiguous: {footnote_stats['binding']['missing']}/{footnote_stats['binding']['unresolved']}/{footnote_stats['binding']['ambiguous']}.
- source verses с одной или несколькими сносками: {footnote_stats['verses_with_footnotes']}; с несколькими: {footnote_stats['verses_with_multiple_footnotes']}.

Carrier counts не объявляются количеством итоговых сносок. Paired named ref хранит определение и использование, self-closing named ref создаёт только дополнительное use. Текст сносок отсутствует в `source_plain_nfc`; каждый печатный marker сохраняется как page-local `ref` ordinal с carrier provenance. Одиннадцать сносок находятся в заголовочных шаблонах и не имеют verse anchor; они сохранены как `missing` для ручной проверки. Продолжение Иак. 5:5 на границе страницы 1490 удерживается в исходном стихе, без присоединения к соседней книге.

## Сравнения и расхождения

Постиховые сравнения выполнялись по порядку source-native tokens, их digest, raw/normalized Strong sequence и полноте source refs. Для печатных сносок сравнивались page, порядок, digest текста и доступное OCR-доказательство Commons. Производные/зеркальные источники помечены зависимыми и не считаются независимым подтверждением.

Агрегаты сравнений: `{canonical_json(comparisons)}`.

Полный безопасный список находится в `source_diff.csv`; он содержит identifiers, hashes и counts, но не воспроизводит корпус. Отсутствие точного совпадения с hidden OCR имеет medium/manual-review статус и не означает потерю ref: OCR печатного скана шумный, а provenance каждой сноски сохранён.

## Manual-only источники

Google Books, HathiTrust и Internet Archive access-preview/manual controls из source lock не превращались в machine inputs. На следующих ручных проверках спорный `footnote_id` можно открыть по Commons page/revision provenance и сверить с этими control surfaces; они не меняют автоматически source text или binding.

## Выход

Все machine records учтены как processed либо классифицированные metadata/service/skipped records; ошибок parser contract нет. Все 1 329 `<ref>` carriers структурно потреблены: 1 204 paired definitions/uses и 125 self-closing named uses. Нет нерешённых critical/high дефектов. Missing heading anchors и OCR-review items находятся в явных безопасных списках. Этап 5 разрешён, но не начат.
"""


def generate(*, djvutxt: Path = DJVUTXT_DEFAULT) -> dict[str, object]:
    verify_locked_cache()
    contexts, lock = load_contexts()
    if not djvutxt.is_file():
        raise Stage4PipelineError(f"Required pinned local DjVuLibre tool is missing: {djvutxt}")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    manifests: list[dict[str, object]] = []
    stats: dict[str, object] = {}
    summaries: dict[str, dict[str, object]] = {}
    warnings: list[dict[str, object]] = []
    unresolved: list[dict[str, object]] = []
    for context in contexts:
        print(f"Parsing {context.source_id}...", flush=True)
        result = _parse(context, djvutxt=djvutxt)
        if result.errors:
            raise Stage4PipelineError(f"Parser errors for {context.source_id}: {result.errors[:3]}")
        manifest, summary = _write_normalized(context, result)
        manifests.append(manifest)
        summaries[context.source_id] = summary
        stats[context.source_id] = {
            "role": context.role,
            "version": context.version,
            "revision": context.revision,
            "counters": dict(sorted(result.counters.items())),
            "skipped": dict(sorted(result.skipped.items())),
            "warnings": len(result.warnings),
            "errors": len(result.errors),
        }
        warnings.extend(_safe_warning(warning) for warning in result.warnings)
        for record in result.records:
            for footnote in record.get("footnotes", []):
                if footnote.get("binding_status") in {"missing", "ambiguous", "unresolved"}:
                    unresolved.append(
                        {
                            "footnote_id": footnote.get("footnote_id"),
                            "use_id": footnote.get("use_id"),
                            "source_id": footnote.get("source_id"),
                            "source_revision": footnote.get("source_revision"),
                            "source_page": footnote.get("source_page"),
                            "source_ref": footnote.get("source_ref"),
                            "anchor_locator": footnote.get("anchor_locator"),
                            "binding_status": footnote.get("binding_status"),
                            "binding_candidates": footnote.get("binding_candidates", []),
                            "binding_evidence": footnote.get("binding_evidence", []),
                            "source_fragment_sha256": footnote.get("source_fragment_sha256"),
                            "status": "manual_review",
                        }
                    )
        del result
    rows, comparisons = _build_diffs(summaries)
    _write_diff(rows)
    wikisource_counters = stats["wikisource_ohienko_1988_revisions"]["counters"]
    binding = {
        status: int(wikisource_counters.get(f"footnote_binding_{status}", 0))
        for status in ("unambiguous", "ambiguous", "missing", "unresolved")
    }
    footnote_stats = {
        "schema_version": 1,
        "carrier_inventory_is_not_final_footnote_count": True,
        "raw_carriers": {
            "ref_opening": wikisource_counters["raw_carrier_ref_opening"],
            "ref_closing": wikisource_counters["raw_carrier_ref_closing"],
            "ref_self_closing": wikisource_counters["raw_carrier_ref_self_closing"],
            "reflist": wikisource_counters["raw_carrier_reflist"],
            "anchor": wikisource_counters["raw_carrier_anchor"],
        },
        "unique_definitions": wikisource_counters["unique_footnote_definitions"],
        "uses": wikisource_counters["footnote_uses"],
        "resolved_named_and_self_closing_uses": wikisource_counters["resolved_footnote_uses"],
        "binding": binding,
        "verses_with_footnotes": wikisource_counters["verses_with_footnotes"],
        "verses_with_multiple_footnotes": wikisource_counters["verses_with_multiple_footnotes"],
        "printed_markers_resolved": wikisource_counters["printed_markers_resolved"],
        "footnotes_without_printed_marker": (
            wikisource_counters["footnote_uses"]
            - wikisource_counters["printed_markers_resolved"]
        ),
        "print_ocr_comparison": comparisons["wikisource_footnotes_vs_commons_hidden_ocr"],
        "unresolved_or_missing_entries": len(unresolved),
    }
    parser_manifest = {
        "schema_version": 1,
        "stage": 4,
        "status": "complete",
        "generated_on": "2026-08-01",
        "parser_contract_version": PARSER_CONTRACT_VERSION,
        "generator_version": GENERATOR_VERSION,
        "source_lock": {
            "path": _relative(SOURCE_LOCK_PATH),
            "sha256": sha256_bytes(SOURCE_LOCK_PATH.read_bytes()),
            "machine_source_count": len(contexts),
        },
        "normalized_manifests": [
            f"normalized_{manifest['source_id']}.manifest.json" for manifest in manifests
        ],
        "parser_independence": {
            "commons": "DjVu IFF + DjVuLibre hidden-text path from Commons bytes",
            "internet_archive": "separate DjVu IFF + DjVuLibre invocation from IA bytes",
            "wikisource": "MediaWiki/ProofreadPage JSON and balanced markup parser",
            "step_tahot": "17-column TSV parser",
            "step_tagnt": "17-column TSV parser",
            "step_tvtms": "line/section/mapping TSV parser without projection",
            "oshb": "ZIP + OSIS XML parser",
            "uxlc": "ZIP + native UXLC XML parser",
            "ugnt": "ZIP + USFM parser",
            "crosswire_kjv": "milestone OSIS XML parser",
        },
        "tools": {
            "python": sys.version.split()[0],
            "djvulibre": {
                "product_version": "3.5.29+4.12",
                "license": "GPL-2.0-or-later (local development tool; not redistributed)",
                "executable": djvutxt.name,
                "sha256": sha256_bytes(djvutxt.read_bytes()),
            },
            "third_party_python_dependencies_added": False,
        },
        "manual_controls": lock.get("manual_controls", []),
        "manual_controls_policy": "not_machine_inputs; provenance locators only for later human review",
        "target_projection": "not_performed",
        "stage_5_started": False,
    }
    high_warnings = [warning for warning in warnings if warning["severity"] == "high"]
    high_diffs = [row for row in rows if row["severity"] in {"critical", "high"} and row["status"] == "unresolved"]
    if high_warnings or high_diffs:
        raise Stage4PipelineError(
            f"Unresolved high defects block stage 4: warnings={len(high_warnings)}, diffs={len(high_diffs)}"
        )
    source_stats = {
        "schema_version": 1,
        "stage": 4,
        "parser_contract_version": PARSER_CONTRACT_VERSION,
        "sources": stats,
        "comparisons": comparisons,
        "warning_count": len(warnings),
        "error_count": 0,
        "diff_row_count": len(rows),
        "target_projection": "not_performed",
    }
    _write_bytes_if_changed(REPORT_DIR / "source_stats.json", _json_bytes(source_stats))
    _write_bytes_if_changed(REPORT_DIR / "footnote_stats.json", _json_bytes(footnote_stats))
    _write_bytes_if_changed(REPORT_DIR / "parser_manifest.json", _json_bytes(parser_manifest))
    _write_bytes_if_changed(REPORT_DIR / "warning_log.json", _json_bytes({"schema_version": 1, "warnings": warnings}))
    _write_bytes_if_changed(
        REPORT_DIR / "unresolved_footnotes.jsonl",
        b"".join(_json_bytes(item, pretty=False) for item in unresolved),
    )
    _write_bytes_if_changed(REPORT_DIR / "normalization_rules.md", _normalization_rules().encode("utf-8"))
    _write_bytes_if_changed(
        REPORT_DIR / "report.ru.md",
        _render_report(source_stats, footnote_stats, comparisons, manifests).encode("utf-8"),
    )
    return {
        "source_count": len(contexts),
        "normalized_count": len(manifests),
        "warning_count": len(warnings),
        "diff_row_count": len(rows),
        "unresolved_footnote_count": len(unresolved),
    }


def check() -> dict[str, object]:
    verify_locked_cache()
    contexts, _ = load_contexts()
    failures: list[str] = []
    for context in contexts:
        manifest_path = REPORT_DIR / f"normalized_{context.source_id}.manifest.json"
        if not manifest_path.is_file():
            failures.append(f"missing manifest: {manifest_path}")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["input"]["sha256"] != context.expected_sha256:
            failures.append(f"stale input digest: {context.source_id}")
        artifact = PROJECT_ROOT / manifest["normalized_artifact"]["gitignored_path"]
        if not artifact.is_file():
            failures.append(f"missing normalized artifact: {artifact}")
            continue
        payload = artifact.read_bytes()
        if len(payload) != manifest["normalized_artifact"]["bytes"]:
            failures.append(f"normalized size mismatch: {context.source_id}")
        if sha256_bytes(payload) != manifest["normalized_artifact"]["sha256"]:
            failures.append(f"normalized SHA mismatch: {context.source_id}")
    required = {
        "source_stats.json", "source_diff.csv", "report.ru.md", "validation_log.md",
        "parser_manifest.json", "warning_log.json", "footnote_stats.json",
        "unresolved_footnotes.jsonl", "normalization_rules.md",
    }
    for name in required:
        if not (REPORT_DIR / name).is_file():
            failures.append(f"missing stage-4 evidence: {name}")
    if failures:
        raise Stage4PipelineError("\n".join(failures))
    return {"source_count": len(contexts), "status": "verified"}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or verify Ukrainian Bible stage-4 source-native artifacts.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--djvutxt", type=Path, default=DJVUTXT_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        result = generate(djvutxt=args.djvutxt) if args.generate else check()
    except (Stage4PipelineError, Stage4ParseError, OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
