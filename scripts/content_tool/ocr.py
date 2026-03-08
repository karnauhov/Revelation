from __future__ import annotations

import os
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Callable, Sequence

from .helpers import clamp01, get_documents_dir

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - content_tool already depends on Pillow.
    Image = None
    ImageOps = None


RectRel = tuple[float, float, float, float]

_LATIN_TO_GREEK = str.maketrans(
    {
        "A": "Α",
        "B": "Β",
        "E": "Ε",
        "H": "Η",
        "I": "Ι",
        "K": "Κ",
        "M": "Μ",
        "N": "Ν",
        "O": "Ο",
        "P": "Ρ",
        "T": "Τ",
        "X": "Χ",
        "Y": "Υ",
        "Z": "Ζ",
    }
)

_SPECIAL_GREEK_NORMALIZATION = str.maketrans(
    {
        "ς": "Σ",
        "σ": "Σ",
        "ϲ": "Σ",
        "Ϲ": "Σ",
        "ϐ": "Β",
        "ϑ": "Θ",
        "ϕ": "Φ",
        "ϖ": "Π",
        "ϰ": "Κ",
    }
)

_DEFAULT_MODEL_NAMES: tuple[str, ...] = (
    "u001_sinaiticus_word.mlmodel",
    "u001_sinaiticus_word_best.mlmodel",
    "greek_majuscule_best.mlmodel",
    "greek_majuscule.mlmodel",
    "greek_word.mlmodel",
)


class OcrSetupError(RuntimeError):
    pass


def _normalize_source_id(source_id: str | None) -> str | None:
    if source_id is None:
        return None
    token = "".join(ch for ch in source_id.strip().upper() if ch.isalnum() or ch in {"_", "-"})
    return token or None


def _source_model_names(source_id: str) -> tuple[str, ...]:
    sid_upper = source_id.upper()
    sid_lower = source_id.lower()
    return (
        f"{sid_lower}_word.mlmodel",
        f"{sid_lower}_word_best.mlmodel",
        f"{sid_upper}_word.mlmodel",
        f"{sid_upper}_word_best.mlmodel",
        f"{sid_lower}.mlmodel",
        f"{sid_upper}.mlmodel",
    )


def _append_source_candidates(append: Callable[[Path], None], root_dir: Path, source_id: str) -> None:
    names = _source_model_names(source_id)
    for source_dir in (root_dir / "sources" / source_id, root_dir / source_id):
        for name in names:
            append(source_dir / name)
        if source_dir.exists() and source_dir.is_dir():
            for path in sorted(source_dir.glob("*.mlmodel")):
                append(path)


def recognize_greek_word_from_fragments(
    image: "Image.Image",
    rectangles: Sequence[RectRel],
    *,
    source_id: str | None = None,
) -> str:
    if Image is None or ImageOps is None:
        raise OcrSetupError("Pillow недоступен в текущем Python-окружении.")

    if not rectangles:
        return ""

    stitched = build_word_crop_from_fragments(image, rectangles)
    if stitched is None:
        return ""

    raw_text = _run_kraken_ocr(stitched, source_id=source_id)
    return normalize_greek_ocr_text(raw_text)


def build_word_crop_from_fragments(image: "Image.Image", rectangles: Sequence[RectRel]) -> "Image.Image | None":
    source = image.convert("RGB")
    fragments: list[Image.Image] = []
    for rect in rectangles:
        crop = _crop_fragment(source, rect)
        if crop is not None:
            fragments.append(crop)

    if not fragments:
        return None

    fragment_height = max(fragment.height for fragment in fragments)
    gap = max(1, int(round(fragment_height * 0.04)))
    outer_padding = max(8, int(round(fragment_height * 0.16)))
    canvas_width = (outer_padding * 2) + sum(fragment.width for fragment in fragments) + gap * (len(fragments) - 1)
    canvas_height = (outer_padding * 2) + fragment_height
    canvas = Image.new("L", (canvas_width, canvas_height), color=255)

    cursor_x = outer_padding
    for fragment in fragments:
        grayscale = fragment.convert("L")
        paste_y = outer_padding + max(0, (fragment_height - grayscale.height) // 2)
        canvas.paste(grayscale, (cursor_x, paste_y))
        cursor_x += grayscale.width + gap

    prepared = ImageOps.autocontrast(canvas)
    prepared = _trim_excess_background(prepared)
    prepared = ImageOps.expand(prepared, border=max(12, prepared.height // 8), fill=255)

    min_height = 96
    if prepared.height < min_height:
        scale = min_height / max(1, prepared.height)
        resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        prepared = prepared.resize(
            (max(1, int(round(prepared.width * scale))), min_height),
            resampling,
        )

    return prepared.convert("RGB")


def _crop_fragment(image: "Image.Image", rect: RectRel) -> "Image.Image | None":
    width, height = image.size
    left = int(round(clamp01(min(rect[0], rect[2])) * width))
    top = int(round(clamp01(min(rect[1], rect[3])) * height))
    right = int(round(clamp01(max(rect[0], rect[2])) * width))
    bottom = int(round(clamp01(max(rect[1], rect[3])) * height))

    if right - left < 2 or bottom - top < 2:
        return None

    pad_x = max(2, int(round((right - left) * 0.05)))
    pad_y = max(2, int(round((bottom - top) * 0.1)))
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(width, right + pad_x)
    bottom = min(height, bottom + pad_y)

    if right - left < 2 or bottom - top < 2:
        return None

    return image.crop((left, top, right, bottom))


def _trim_excess_background(image: "Image.Image") -> "Image.Image":
    threshold = 235
    mask = image.point(lambda px: 255 if px < threshold else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def _run_kraken_ocr(image: "Image.Image", *, source_id: str | None = None) -> str:
    try:
        from kraken import rpred
    except Exception as exc:  # pragma: no cover - depends on external package/runtime.
        raise OcrSetupError(
            "OCR требует установленный пакет `kraken` в Python-окружении content_tool."
        ) from exc

    model_path = _resolve_kraken_model_path(source_id=source_id)
    try:
        model_mtime_ns = model_path.stat().st_mtime_ns
    except OSError:
        model_mtime_ns = 0
    model = _load_kraken_model(str(model_path), model_mtime_ns)
    segmentation = _build_segmentation(image)

    try:
        predictions = rpred.rpred(model, image, segmentation)
    except Exception as exc:  # pragma: no cover - depends on external package/runtime.
        raise OcrSetupError(f"Kraken не смог запустить распознавание: {exc}") from exc

    parts: list[str] = []
    for record in predictions:
        prediction = getattr(record, "prediction", "")
        if prediction:
            parts.append(prediction)
    return "".join(parts).strip()


def _build_segmentation(image: "Image.Image"):
    try:
        from kraken.containers import BBoxLine, Segmentation
    except Exception as exc:  # pragma: no cover - depends on external package/runtime.
        raise OcrSetupError(
            "OCR требует установленный пакет `kraken` в Python-окружении content_tool."
        ) from exc

    width, height = image.size
    return Segmentation(
        type="bbox",
        imagename="primary_source_word_crop",
        text_direction="horizontal-lr",
        script_detection=False,
        lines=[
            BBoxLine(
                id="line0",
                bbox=[0, 0, width, height],
                text=None,
                base_dir=None,
                type="bbox",
                imagename=None,
                tags=None,
                split=None,
                regions=None,
                text_direction="horizontal-lr",
            )
        ],
        regions={},
        line_orders=[],
    )


@lru_cache(maxsize=32)
def _load_kraken_model(model_path: str, model_mtime_ns: int):
    # model_mtime_ns participates in cache key, so updated files are reloaded automatically.
    _ = model_mtime_ns
    try:
        from kraken.lib import models
    except Exception as exc:  # pragma: no cover - depends on external package/runtime.
        raise OcrSetupError(
            "OCR требует установленный пакет `kraken` в Python-окружении content_tool."
        ) from exc

    try:
        return models.load_any(model_path)
    except Exception as exc:  # pragma: no cover - depends on external package/runtime.
        raise OcrSetupError(f"Не удалось загрузить Kraken-модель: {model_path}") from exc


def _resolve_kraken_model_path(*, source_id: str | None = None) -> Path:
    source_token = _normalize_source_id(source_id)
    candidates = _candidate_model_paths(source_id=source_token)
    for path in candidates:
        if path.exists() and path.is_file():
            return path

    preview = "\n".join(f"- {path}" for path in candidates[:8])
    if source_token is not None:
        raise OcrSetupError(
            f"Kraken model for source '{source_token}' was not found.\n"
            "Train this source model first or place it into one of these paths:\n"
            f"{preview}"
        )
    raise OcrSetupError(
        "Не найдена Kraken-модель `.mlmodel`.\n"
        "Укажите путь через переменную окружения `REVELATION_KRAKEN_MODEL` "
        "или положите модель в один из путей:\n"
        f"{preview}"
    )


def _candidate_model_paths(*, source_id: str | None = None) -> list[Path]:
    seen: set[Path] = set()
    candidates: list[Path] = []

    def append(path: Path) -> None:
        resolved = path.expanduser()
        if resolved not in seen:
            seen.add(resolved)
            candidates.append(resolved)

    env_values = [
        os.environ.get("REVELATION_KRAKEN_MODEL", "").strip(),
        os.environ.get("REVELATION_KRAKEN_MODELS_ROOT", "").strip(),
        os.environ.get("KRAKEN_MODEL_PATH", "").strip(),
    ]
    for raw in env_values:
        if not raw:
            continue
        env_path = Path(raw)
        if env_path.suffix.lower() == ".mlmodel":
            append(env_path)
            continue
        if source_id:
            _append_source_candidates(append, env_path, source_id)
        for name in _DEFAULT_MODEL_NAMES:
            append(env_path / name)
        if env_path.exists() and env_path.is_dir():
            for path in sorted(env_path.glob("*.mlmodel")):
                append(path)

    project_root = Path(__file__).resolve().parents[2]
    default_dirs = (
        project_root / "scripts" / "content_tool" / "models" / "ocr",
        project_root / "scripts" / "content_tool" / "models",
        project_root / "scripts" / "ocr",
        project_root / "models" / "ocr",
        get_documents_dir() / "revelation" / "ocr",
    )
    for directory in default_dirs:
        if source_id:
            _append_source_candidates(append, directory, source_id)
        for name in _DEFAULT_MODEL_NAMES:
            append(directory / name)
        if directory.exists() and directory.is_dir():
            for path in sorted(directory.glob("*.mlmodel")):
                append(path)

    return candidates


def normalize_greek_ocr_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text or "")
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    normalized = unicodedata.normalize("NFC", normalized).upper()
    normalized = normalized.translate(_LATIN_TO_GREEK)
    normalized = normalized.translate(_SPECIAL_GREEK_NORMALIZATION)

    output: list[str] = []
    for ch in normalized:
        category = unicodedata.category(ch)
        if ch.isdigit():
            output.append(ch)
            continue
        if category.startswith("L") and "GREEK" in unicodedata.name(ch, ""):
            output.append(ch)

    return "".join(output)
