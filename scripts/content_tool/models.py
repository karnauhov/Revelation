from __future__ import annotations

from dataclasses import dataclass

@dataclass
class ArticleRow:
    route: str
    name: str
    description: str
    id_icon: str
    sort_order: int
    is_visible: bool
    markdown: str


@dataclass
class ResourceRow:
    key: str
    file_name: str
    mime_type: str
    size_bytes: int


@dataclass
class StrongRow:
    id: int
    word: str
    category: str
    synonyms: str
    origin: str
    usage: str
    localized_flags: dict[str, bool]
    localized_search: str


@dataclass
class PrimarySourceSummary:
    id: str
    family: str
    number: int
    group_kind: str
    sort_order: int
    pages_count: int
    words_count: int
    verse_rows_count: int
    can_show_images: bool
    preview_resource_key: str
    title_preview: str
    locale_flags: dict[str, bool]
    ocr_metric: int = 0


@dataclass
class PrimarySourcePageSummary:
    source_id: str
    page_name: str
    sort_order: int
    content_ref: str
    image_path: str
    words_count: int
    verse_rows_count: int
    local_exists: bool


@dataclass(frozen=True)
class FormFieldSpec:
    key: str
    label: str
    kind: str = "entry"
    width: int = 40
    height: int = 4
    options: tuple[str, ...] = ()
    readonly: bool = False


@dataclass(frozen=True)
class MarkdownTemplateSpec:
    key: str
    label: str
    icon_name: str
    template: str
    title: str
    example: str
    note: str = ""



Point = tuple[float, float]
