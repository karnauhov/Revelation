from __future__ import annotations

import tkinter as tk
from pathlib import Path

from .icons import CONTENT_TOOL_ICONS
from .mixins import ArticlesMixin, CoreDbMixin, CoreUiMixin, PrimarySourcesMixin, ResourcesMixin, StrongsMixin


class TopicContentTool(
    PrimarySourcesMixin,
    ResourcesMixin,
    ArticlesMixin,
    StrongsMixin,
    CoreDbMixin,
    CoreUiMixin,
    tk.Tk,
):
    BASE_TITLE = "Content of Revelation"
    NO_ARTICLE_OPTION = "(без статьи)"
    NO_ICON_OPTION = "(без иконки)"
    UNBOUND_TAG = "unbound_row"
    ALERT_COLOR = "#c1121f"
    OK_COLOR = "#1f7a3f"
    ICON_PNG_BASE64 = CONTENT_TOOL_ICONS
