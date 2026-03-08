from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.content_tool.compat import Image
from scripts.content_tool.helpers import default_primary_sources_dir
from scripts.content_tool.ocr import build_word_crop_from_fragments, normalize_greek_ocr_text


@dataclass(slots=True)
class Sample:
    source_id: str
    page_name: str
    word_index: int
    text: str
    source_image_rel: str
    image_path: Path
    gt_path: Path


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare OCR training samples from primary_source_words and run ketos train. "
            "Default workflow: full retrain on all currently available words for selected source/pages."
        )
    )
    parser.add_argument("--db", type=Path, required=True, help="Path to SQLite DB (e.g. revelation.sqlite).")
    parser.add_argument("--source-id", required=True, help="Primary source ID (e.g. U001).")
    parser.add_argument(
        "--page-name",
        action="append",
        default=[],
        help="Page name to include (repeatable). If omitted, all pages with words for source are used.",
    )
    parser.add_argument(
        "--primary-sources-root",
        type=Path,
        default=None,
        help="Local root directory containing page images. If omitted it is auto-resolved from DB path.",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("scripts/content_tool/models/ocr/datasets"),
        help="Root directory for generated training datasets.",
    )
    parser.add_argument(
        "--run-name",
        default="",
        help="Optional dataset run name. Defaults to source + pages.",
    )
    parser.add_argument(
        "--normalize-target",
        choices=("none", "ocr"),
        default="ocr",
        help="Text normalization policy for training targets.",
    )
    parser.add_argument("--min-chars", type=int, default=1, help="Skip samples shorter than this length.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for train/eval split.")
    parser.add_argument(
        "--train-split",
        type=float,
        default=0.85,
        help="Train split ratio for generated image list files.",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Do not delete an existing dataset run directory before export.",
    )
    parser.add_argument("--prepare-only", action="store_true", help="Only export dataset, do not launch ketos train.")

    parser.add_argument(
        "--base-model",
        type=Path,
        default=None,
        help="Optional base model (.mlmodel) for fine-tuning. If omitted, training starts from scratch.",
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        default=Path("scripts/content_tool/models/ocr"),
        help="Root dir for OCR models.",
    )
    parser.add_argument(
        "--output-stem",
        type=Path,
        default=None,
        help=(
            "Ketos output stem (final best model is <stem>_best.mlmodel). "
            "Default: <model-root>/sources/<SOURCE_ID>/<source_id_lower>_word"
        ),
    )
    parser.add_argument(
        "--copy-to-model",
        type=Path,
        default=None,
        help=(
            "Optional stable path where trained model is copied. "
            "Default: <model-root>/sources/<SOURCE_ID>/<source_id_lower>_word.mlmodel"
        ),
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional path for machine-readable training report JSON.",
    )

    parser.add_argument("--epochs", type=int, default=80, help="Fixed number of epochs for ketos train.")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size for ketos train.")
    parser.add_argument(
        "--device",
        default="cpu",
        help="Ketos device (cpu, cuda:0, ...).",
    )
    parser.add_argument(
        "--augment",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable/disable augmentation in ketos train.",
    )
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def sanitize_token(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]+", "_", value.strip())


def resolve_primary_sources_root(db_path: Path, explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        return resolve_path(explicit_root)
    if db_path.parent.name.lower() == "db":
        return (db_path.parent.parent / "primary_sources").resolve()
    return default_primary_sources_dir().resolve()


def resolve_primary_source_local_path(root: Path, image_path: str) -> Path:
    normalized = (image_path or "").replace("\\", "/").lstrip("/")
    if normalized.startswith("primary_sources/"):
        normalized = normalized[len("primary_sources/") :]
    return root / Path(normalized)


def parse_rectangles(raw: str) -> list[tuple[float, float, float, float]]:
    try:
        payload = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    rectangles: list[tuple[float, float, float, float]] = []
    for item in payload:
        if not isinstance(item, (list, tuple)) or len(item) != 4:
            continue
        try:
            x1, y1, x2, y2 = (float(item[0]), float(item[1]), float(item[2]), float(item[3]))
        except (TypeError, ValueError):
            continue
        rectangles.append((x1, y1, x2, y2))
    return rectangles


def fetch_rows(connection: sqlite3.Connection, source_id: str, page_names: list[str]) -> list[sqlite3.Row]:
    sql = """
        SELECT
          w.source_id,
          w.page_name,
          w.word_index,
          w.text,
          w.rectangles_json,
          p.image_path
        FROM primary_source_words w
        JOIN primary_source_pages p
          ON p.source_id = w.source_id
         AND p.page_name = w.page_name
        WHERE w.source_id = ?
    """
    params: list[object] = [source_id]
    if page_names:
        placeholders = ", ".join("?" for _ in page_names)
        sql += f" AND w.page_name IN ({placeholders})"
        params.extend(page_names)
    sql += " ORDER BY w.page_name ASC, w.word_index ASC"
    return connection.execute(sql, params).fetchall()


def choose_run_name(source_id: str, page_names: list[str], explicit_run_name: str) -> str:
    if explicit_run_name.strip():
        return sanitize_token(explicit_run_name)
    if not page_names:
        return f"{sanitize_token(source_id)}_all_pages"
    page_part = "_".join(sanitize_token(name) for name in sorted(page_names))
    return f"{sanitize_token(source_id)}_{page_part}"


def split_samples(samples: list[Sample], train_split: float, seed: int) -> tuple[list[Sample], list[Sample]]:
    if not samples:
        return [], []
    shuffled = list(samples)
    random.Random(seed).shuffle(shuffled)

    ratio = 0.0 if train_split < 0.0 else 1.0 if train_split > 1.0 else train_split
    eval_count = int(round(len(shuffled) * (1.0 - ratio)))
    if len(shuffled) >= 8 and eval_count < 1:
        eval_count = 1
    if eval_count >= len(shuffled):
        eval_count = len(shuffled) - 1
    if eval_count < 0:
        eval_count = 0

    eval_samples = shuffled[:eval_count]
    train_samples = shuffled[eval_count:]
    return train_samples, eval_samples


def _coverage_bucket(train_count: int) -> str:
    if train_count <= 0:
        return "missing_in_train"
    if train_count < 5:
        return "rare"
    if train_count < 15:
        return "limited"
    if train_count < 40:
        return "good"
    return "strong"


def empty_char_coverage() -> dict[str, Any]:
    bucket_names = ("strong", "good", "limited", "rare", "missing_in_train")
    return {
        "version": 1,
        "bucket_thresholds": {
            "strong": ">= 40 (train)",
            "good": "15-39 (train)",
            "limited": "5-14 (train)",
            "rare": "1-4 (train)",
            "missing_in_train": "0 (train)",
        },
        "bucket_labels_ru": {
            "strong": "сильное покрытие",
            "good": "хорошее покрытие",
            "limited": "ограниченное покрытие",
            "rare": "редкое покрытие",
            "missing_in_train": "нет в train",
        },
        "total_unique_chars": 0,
        "chars": [],
        "bucket_counts": {name: 0 for name in bucket_names},
        "bucket_chars": {name: [] for name in bucket_names},
        "train_chars_with_at_least_5": 0,
        "train_chars_with_at_least_15": 0,
        "train_chars_with_at_least_40": 0,
    }


def build_char_coverage(
    exported: list[Sample],
    train_samples: list[Sample],
    eval_samples: list[Sample],
) -> dict[str, Any]:
    coverage = empty_char_coverage()
    total_counts: Counter[str] = Counter()
    train_counts: Counter[str] = Counter()
    eval_counts: Counter[str] = Counter()

    for sample in exported:
        total_counts.update(sample.text)
    for sample in train_samples:
        train_counts.update(sample.text)
    for sample in eval_samples:
        eval_counts.update(sample.text)

    if not total_counts:
        return coverage

    chars = sorted(
        total_counts.keys(),
        key=lambda ch: (-int(train_counts.get(ch, 0)), -int(total_counts.get(ch, 0)), ch),
    )

    char_rows: list[dict[str, Any]] = []
    bucket_counts = coverage["bucket_counts"]
    bucket_chars = coverage["bucket_chars"]
    assert isinstance(bucket_counts, dict)
    assert isinstance(bucket_chars, dict)

    for char in chars:
        total_count = int(total_counts.get(char, 0))
        train_count = int(train_counts.get(char, 0))
        eval_count = int(eval_counts.get(char, 0))
        bucket = _coverage_bucket(train_count)
        bucket_counts[bucket] = int(bucket_counts.get(bucket, 0)) + 1
        bucket_list = bucket_chars.get(bucket)
        if isinstance(bucket_list, list):
            bucket_list.append(char)
        char_rows.append(
            {
                "char": char,
                "codepoint": f"U+{ord(char):04X}",
                "total_count": total_count,
                "train_count": train_count,
                "eval_count": eval_count,
                "bucket": bucket,
            }
        )

    coverage["total_unique_chars"] = len(char_rows)
    coverage["chars"] = char_rows
    coverage["train_chars_with_at_least_5"] = sum(1 for row in char_rows if int(row["train_count"]) >= 5)
    coverage["train_chars_with_at_least_15"] = sum(1 for row in char_rows if int(row["train_count"]) >= 15)
    coverage["train_chars_with_at_least_40"] = sum(1 for row in char_rows if int(row["train_count"]) >= 40)
    return coverage


def write_path_list(path: Path, samples: list[Sample]) -> None:
    lines = [str(sample.image_path.resolve()) for sample in samples]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def locate_ketos() -> str:
    py_dir = Path(sys.executable).resolve().parent
    for name in ("ketos.exe", "ketos"):
        candidate = py_dir / name
        if candidate.exists():
            return str(candidate)
    return "ketos"


def run_command(
    command: list[str],
    *,
    log_path: Path | None,
    logger: Callable[[str], None],
) -> str:
    logger("RUN: " + " ".join(command))
    env = dict(**os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["FORCE_COLOR"] = "0"

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    output_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        text = line.rstrip("\n")
        logger(text)
        output_lines.append(text)

    return_code = process.wait()
    output_text = "\n".join(output_lines)
    if output_lines:
        output_text += "\n"

    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(output_text, encoding="utf-8")

    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command, output=output_text)

    return output_text


def choose_model_paths(args: argparse.Namespace) -> tuple[Path, Path | None]:
    source_token_upper = sanitize_token(args.source_id).upper()
    source_token_lower = sanitize_token(args.source_id).lower()

    model_root = resolve_path(args.model_root)
    default_dir = model_root / "sources" / source_token_upper
    default_stem = default_dir / f"{source_token_lower}_word"
    default_copy = default_dir / f"{source_token_lower}_word.mlmodel"

    output_stem = resolve_path(args.output_stem) if args.output_stem is not None else default_stem
    copy_to_model = resolve_path(args.copy_to_model) if args.copy_to_model is not None else default_copy
    return output_stem, copy_to_model


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def status_label_ru(status: str) -> str:
    labels = {
        "ok": "успешно",
        "prepared_only": "подготовлено (без запуска обучения)",
        "export_failed": "ошибка экспорта датасета",
        "split_failed": "ошибка разделения train/eval",
        "train_failed": "ошибка обучения",
        "model_missing_after_train": "обучение завершено, но модель не найдена",
        "test_failed": "ошибка проверки модели",
    }
    return labels.get(status, status)


def build_report_ru(payload: dict[str, Any]) -> dict[str, Any]:
    char_coverage = payload.get("char_coverage")
    if not isinstance(char_coverage, dict):
        char_coverage = empty_char_coverage()
    skipped = payload.get("skipped")
    if not isinstance(skipped, dict):
        skipped = {}
    bucket_counts = char_coverage.get("bucket_counts")
    if not isinstance(bucket_counts, dict):
        bucket_counts = {}
    return {
        "статус": status_label_ru(str(payload.get("status", ""))),
        "кратко": {
            "первоисточник": payload.get("source_id"),
            "страницы": payload.get("pages"),
            "слов_из_БД": payload.get("rows_fetched"),
            "экспортировано_примеров": payload.get("exported_samples"),
            "train_примеров": payload.get("train_samples"),
            "eval_примеров": payload.get("eval_samples"),
            "уникальных_словоформ": payload.get("unique_word_forms"),
            "пропуски": {
                "пустой_текст": skipped.get("empty"),
                "нет_прямоугольников": skipped.get("rectangles"),
                "нет_изображения": skipped.get("missing_image"),
                "ошибка_crop": skipped.get("crop"),
            },
        },
        "покрытие_букв": {
            "уникальных_букв": char_coverage.get("total_unique_chars"),
            "сильное_покрытие": bucket_counts.get("strong"),
            "хорошее_покрытие": bucket_counts.get("good"),
            "ограниченное_покрытие": bucket_counts.get("limited"),
            "редкое_покрытие": bucket_counts.get("rare"),
            "нет_в_train": bucket_counts.get("missing_in_train"),
            "букв_в_train_>=5": char_coverage.get("train_chars_with_at_least_5"),
            "букв_в_train_>=15": char_coverage.get("train_chars_with_at_least_15"),
            "букв_в_train_>=40": char_coverage.get("train_chars_with_at_least_40"),
        },
    }


def update_model_state(
    *,
    state_path: Path,
    source_id: str,
    copy_to_model: Path | None,
    report_payload: dict[str, Any],
) -> None:
    previous = load_json_object(state_path)
    history = previous.get("history", [])
    if not isinstance(history, list):
        history = []

    run_item = {
        "finished_at": report_payload.get("run_finished_at"),
        "status": report_payload.get("status"),
        "status_ru": report_payload.get("status_ru"),
        "exported_samples": report_payload.get("exported_samples"),
        "train_samples": report_payload.get("train_samples"),
        "eval_samples": report_payload.get("eval_samples"),
        "unique_word_forms": report_payload.get("unique_word_forms"),
        "report_path": report_payload.get("report_path"),
        "best_model": report_payload.get("best_model"),
        "copied_model": report_payload.get("copied_model"),
    }
    history.append(run_item)
    history = history[-30:]

    model_path = None if copy_to_model is None else str(copy_to_model)
    state_payload = {
        "version": 1,
        "source_id": source_id,
        "model_path": model_path,
        "model_exists": bool(copy_to_model is not None and copy_to_model.exists()),
        "last_status": report_payload.get("status"),
        "last_status_ru": report_payload.get("status_ru"),
        "last_updated_at": report_payload.get("run_finished_at"),
        "last_report_path": report_payload.get("report_path"),
        "last_run": run_item,
        "history": history,
    }
    save_json(state_path, state_payload)


def main() -> int:
    args = parse_args()

    def log(message: str) -> None:
        print(message, flush=True)

    run_started_at = now_utc_iso()

    if Image is None:
        log("Pillow недоступен в текущем Python-окружении.")
        return 1

    db_path = resolve_path(args.db)
    if not db_path.exists():
        log(f"Файл БД не найден: {db_path}")
        return 1

    if args.base_model is not None:
        base_model = resolve_path(args.base_model)
        if not base_model.exists():
            log(f"Базовая модель не найдена: {base_model}")
            return 1
    else:
        base_model = None

    output_stem, copy_to_model = choose_model_paths(args)
    primary_sources_root = resolve_primary_sources_root(db_path, args.primary_sources_root)
    dataset_root = resolve_path(args.dataset_root)
    model_dir = output_stem.parent if copy_to_model is None else copy_to_model.parent
    model_state_path = model_dir / "model_state.json"
    model_last_report_path = model_dir / "last_training_report.json"

    log("STAGE: Загрузка данных источника")
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = fetch_rows(connection, args.source_id, args.page_name)

    if not rows:
        log(f"Для source_id={args.source_id!r} и выбранных страниц слова не найдены.")
        return 1

    actual_pages = sorted({str(row["page_name"] or "") for row in rows})
    run_name = choose_run_name(args.source_id, actual_pages, args.run_name)
    run_dir = dataset_root / run_name
    samples_dir = run_dir / "samples"
    train_list = run_dir / "train_files.txt"
    eval_list = run_dir / "eval_files.txt"
    manifest = run_dir / "manifest.tsv"
    report_path = run_dir / "training_report.json"

    if run_dir.exists() and not args.keep_existing:
        shutil.rmtree(run_dir)
    samples_dir.mkdir(parents=True, exist_ok=True)

    log(f"БД: {db_path}")
    log(f"Источник: {args.source_id} | страницы: {', '.join(actual_pages)}")
    log(f"Строк получено из БД: {len(rows)}")
    log(f"Корень primary_sources: {primary_sources_root}")
    log(f"Папка датасета: {run_dir}")
    log(f"Нормализация target: {args.normalize_target}")
    log(f"Выходной stem модели: {output_stem}")
    if copy_to_model is not None:
        log(f"Стабильный путь модели: {copy_to_model}")

    if args.augment:
        try:
            import albumentations  # type: ignore  # noqa: F401
        except Exception:
            log("Запрошены аугментации, но `albumentations` не установлен. Продолжаю с --no-augment.")
            args.augment = False

    base_report: dict[str, Any] = {
        "source_id": args.source_id,
        "pages": actual_pages,
        "rows_fetched": len(rows),
        "exported_samples": 0,
        "train_samples": 0,
        "eval_samples": 0,
        "unique_word_forms": 0,
        "skipped": {
            "empty": 0,
            "rectangles": 0,
            "missing_image": 0,
            "crop": 0,
        },
        "train_split": args.train_split,
        "seed": args.seed,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "augment": bool(args.augment),
        "base_model": None if base_model is None else str(base_model),
        "output_stem": str(output_stem),
        "copy_to_model": None if copy_to_model is None else str(copy_to_model),
        "char_coverage": empty_char_coverage(),
        "status_ru": "",
        "report_ru": {},
        "run_dir": str(run_dir),
        "run_started_at": run_started_at,
    }

    def finalize(status: str, **extra: Any) -> dict[str, Any]:
        payload = {
            **base_report,
            **extra,
            "status": status,
            "status_ru": status_label_ru(status),
            "report_path": str(report_path),
            "run_finished_at": now_utc_iso(),
        }
        payload["report_ru"] = build_report_ru(payload)
        save_json(report_path, payload)
        save_json(model_last_report_path, payload)
        update_model_state(
            state_path=model_state_path,
            source_id=args.source_id,
            copy_to_model=copy_to_model,
            report_payload=payload,
        )
        if args.report_json is not None:
            save_json(resolve_path(args.report_json), payload)
        log(f"Training report: {report_path}")
        log(f"Model report: {model_last_report_path}")
        log(f"Model state: {model_state_path}")
        return payload

    log("STAGE: Экспорт обучающего датасета")
    image_cache: dict[Path, Image.Image] = {}
    exported: list[Sample] = []
    skipped_empty = 0
    skipped_rectangles = 0
    skipped_missing_image = 0
    skipped_crop = 0
    page_sample_counts: dict[str, int] = {}

    try:
        for row in rows:
            raw_text = str(row["text"] or "").strip()
            if not raw_text:
                skipped_empty += 1
                continue
            text = normalize_greek_ocr_text(raw_text) if args.normalize_target == "ocr" else raw_text
            if len(text) < args.min_chars:
                skipped_empty += 1
                continue

            rectangles = parse_rectangles(str(row["rectangles_json"] or "[]"))
            if not rectangles:
                skipped_rectangles += 1
                continue

            rel_image = str(row["image_path"] or "")
            image_path = resolve_primary_source_local_path(primary_sources_root, rel_image)
            if not image_path.exists():
                skipped_missing_image += 1
                continue

            image = image_cache.get(image_path)
            if image is None:
                image = Image.open(image_path).convert("RGB")
                image_cache[image_path] = image

            crop = build_word_crop_from_fragments(image, rectangles)
            if crop is None:
                skipped_crop += 1
                continue

            page_name = str(row["page_name"] or "")
            word_index = int(row["word_index"])
            sample_name = f"{sanitize_token(args.source_id)}_{sanitize_token(page_name)}_{word_index:05d}"
            image_out = samples_dir / f"{sample_name}.png"
            gt_out = samples_dir / f"{sample_name}.gt.txt"
            crop.save(image_out)
            gt_out.write_text(text, encoding="utf-8")
            exported.append(
                Sample(
                    source_id=str(row["source_id"]),
                    page_name=page_name,
                    word_index=word_index,
                    text=text,
                    source_image_rel=rel_image,
                    image_path=image_out,
                    gt_path=gt_out,
                )
            )
            page_sample_counts[page_name] = page_sample_counts.get(page_name, 0) + 1
    finally:
        for image in image_cache.values():
            image.close()

    if not exported:
        log("Не удалось выгрузить ни одного примера. Проверьте слова, прямоугольники и пути изображений.")
        finalize(
            "export_failed",
            skipped={
                "empty": skipped_empty,
                "rectangles": skipped_rectangles,
                "missing_image": skipped_missing_image,
                "crop": skipped_crop,
            },
        )
        return 1

    train_samples, eval_samples = split_samples(exported, args.train_split, args.seed)
    if not train_samples:
        log("Train-выборка получилась пустой. Увеличьте train_split или добавьте данные.")
        finalize("split_failed")
        return 1

    manifest_lines = [
        "source_id\tpage_name\tword_index\ttext\tsource_image\timage_path\tgt_path",
    ]
    for sample in exported:
        manifest_lines.append(
            "\t".join(
                [
                    sample.source_id,
                    sample.page_name,
                    str(sample.word_index),
                    sample.text,
                    sample.source_image_rel,
                    str(sample.image_path.resolve()),
                    str(sample.gt_path.resolve()),
                ]
            )
        )
    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    write_path_list(train_list, train_samples)
    write_path_list(eval_list, eval_samples)

    unique_word_forms = len({sample.text for sample in exported})
    top_pages = sorted(page_sample_counts.items(), key=lambda item: (-item[1], item[0]))[:10]
    char_coverage = build_char_coverage(exported, train_samples, eval_samples)

    base_report["exported_samples"] = len(exported)
    base_report["train_samples"] = len(train_samples)
    base_report["eval_samples"] = len(eval_samples)
    base_report["unique_word_forms"] = unique_word_forms
    base_report["char_coverage"] = char_coverage
    base_report["skipped"] = {
        "empty": skipped_empty,
        "rectangles": skipped_rectangles,
        "missing_image": skipped_missing_image,
        "crop": skipped_crop,
    }

    log(
        f"Экспортировано примеров: {len(exported)} (train={len(train_samples)}, eval={len(eval_samples)}). "
        f"Уникальных словоформ: {unique_word_forms}."
    )
    log(
        "Покрытие букв (train): "
        f"unique={char_coverage['total_unique_chars']}, "
        f">=40={char_coverage['train_chars_with_at_least_40']}, "
        f">=15={char_coverage['train_chars_with_at_least_15']}, "
        f">=5={char_coverage['train_chars_with_at_least_5']}."
    )
    log(
        "Пропущено: "
        f"empty={skipped_empty}, rectangles={skipped_rectangles}, "
        f"missing_image={skipped_missing_image}, crop={skipped_crop}."
    )
    if top_pages:
        log("Топ страниц по числу экспортированных примеров:")
        for page_name, count in top_pages:
            log(f"  - {page_name}: {count}")
    log(f"Файл train-списка: {train_list}")
    log(f"Файл eval-списка: {eval_list}")
    log(f"Манифест: {manifest}")

    if args.prepare_only:
        log("Подготовка датасета завершена (--prepare-only).")
        finalize("prepared_only")
        return 0

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    ketos = locate_ketos()

    train_cmd = [ketos, "--device", args.device, "train", "-f", "path"]
    if base_model is not None:
        train_cmd.extend(["-i", str(base_model.resolve()), "--resize", "union"])
    if args.augment:
        train_cmd.append("--augment")
    train_cmd.extend(
        [
            "-o",
            str(output_stem),
            "-B",
            str(args.batch_size),
            "-N",
            str(args.epochs),
            "-q",
            "fixed",
            "-t",
            str(train_list),
        ]
    )
    if eval_samples:
        train_cmd.extend(["-e", str(eval_list)])

    train_log = run_dir / "ketos_train.log"
    best_model: Path | None = None
    log("STAGE: Обучение модели")
    try:
        run_command(train_cmd, log_path=train_log, logger=log)
    except subprocess.CalledProcessError as exc:
        log(f"ketos train завершился с кодом {exc.returncode}.")
        log(f"Полный лог обучения: {train_log}")
        checkpoint_candidates = sorted(
            output_stem.parent.glob(f"{output_stem.name}_*.mlmodel"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if checkpoint_candidates:
            best_model = checkpoint_candidates[0]
            log(f"Используется последний checkpoint как модель: {best_model}")
        else:
            log("Подсказка: если ошибка связана с augmentation, установите `albumentations` или запустите с --no-augment.")
            finalize("train_failed", train_log=str(train_log))
            return 1

    if best_model is None:
        expected_best = Path(f"{output_stem}_best.mlmodel")
        if expected_best.exists():
            best_model = expected_best
        else:
            checkpoint_candidates = sorted(
                output_stem.parent.glob(f"{output_stem.name}_*.mlmodel"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if checkpoint_candidates:
                best_model = checkpoint_candidates[0]
                log(f"Файл best недоступен, используется последний checkpoint: {best_model}")
            else:
                log(f"Обучение завершено, но выходная модель для stem не найдена: {output_stem}")
                finalize("model_missing_after_train", train_log=str(train_log))
                return 1

    log(f"Лучшая модель: {best_model}")
    if copy_to_model is not None:
        copy_to_model.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_model, copy_to_model)
        log(f"Лучшая модель скопирована в: {copy_to_model}")

    test_log: Path | None = None
    if eval_samples:
        test_cmd = [
            ketos,
            "--device",
            args.device,
            "test",
            "-f",
            "path",
            "-m",
            str(best_model),
            "-e",
            str(eval_list),
        ]
        test_log = run_dir / "ketos_test.log"
        log("STAGE: Оценка модели")
        try:
            run_command(test_cmd, log_path=test_log, logger=log)
        except subprocess.CalledProcessError as exc:
            log(f"ketos test завершился с ошибкой, код {exc.returncode}.")
            log(f"Полный лог проверки: {test_log}")
            finalize(
                "test_failed",
                best_model=str(best_model),
                train_log=str(train_log),
                test_log=str(test_log),
                copied_model=None if copy_to_model is None else str(copy_to_model),
            )
            return 1

    log("STAGE: Финализация")
    finalize(
        "ok",
        best_model=str(best_model),
        copied_model=None if copy_to_model is None else str(copy_to_model),
        train_log=str(train_log),
        test_log=None if test_log is None else str(test_log),
    )

    log("Готово.")
    log(
        "Итог обучения: "
        f"обучено на {len(train_samples)} примерах "
        f"(+ eval {len(eval_samples)}), всего экспортировано {len(exported)}, "
        f"уникальных транскрипций {unique_word_forms}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
