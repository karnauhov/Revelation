from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from markdown import markdown as md_to_html
except ImportError:
    md_to_html = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

if TYPE_CHECKING:
    from tkinterweb import HtmlFrame as HtmlFrameType
else:
    HtmlFrameType = Any

try:
    from tkinterweb import HtmlFrame as HtmlFrameWidget
except ImportError:
    HtmlFrameWidget = None
