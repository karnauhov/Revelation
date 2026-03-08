from __future__ import annotations

from pathlib import Path
import sqlite3
import tkinter as tk
import unicodedata
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

from ..compat import Image, ImageTk
from ..helpers import clamp01
from ..ocr import OcrSetupError, recognize_greek_word_from_fragments
from ..widgets import _ToolTip

if TYPE_CHECKING:
    from ..app import TopicContentTool


RectRel = tuple[float, float, float, float]


class PrimarySourceWordEditorDialog(tk.Toplevel):
    STRONG_SEARCH_CHAR_TRANSLATION = str.maketrans(
        {
            "ς": "σ",
            "ϲ": "σ",
            "ϐ": "β",
            "ϑ": "θ",
            "ϕ": "φ",
            "ϰ": "κ",
            "ϱ": "ρ",
            "ϖ": "π",
        }
    )

    MODE_LABEL_TO_KEY: dict[str, str] = {
        "Рисование": "draw",
        "Перемещение": "move",
        "Удаление": "delete",
    }

    GREEK_UPPERCASE_KEYS: tuple[str, ...] = (
        "Α",
        "Β",
        "Γ",
        "Δ",
        "Ε",
        "Ζ",
        "Η",
        "Θ",
        "Ι",
        "Κ",
        "Λ",
        "Μ",
        "Ν",
        "Ξ",
        "Ο",
        "Π",
        "Ρ",
        "Σ",
        "Τ",
        "Υ",
        "Φ",
        "Χ",
        "Ψ",
        "Ω",
    )

    def __init__(
        self,
        *,
        parent: TopicContentTool,
        image_path: Path,
        source_id: str,
        page_name: str,
        initial_payload: dict[str, object],
        previous_word_index: int | None,
        strong_entries: list[tuple[int, str]],
        on_save: Callable[[dict[str, object], int | None], bool | None],
    ) -> None:
        super().__init__(parent)
        self.parent_tool = parent
        self.source_id = source_id
        self.page_name = page_name
        self.on_save = on_save
        self.previous_word_index = previous_word_index
        self.greek_keyboard_window: tk.Toplevel | None = None
        self._normalized_strong_rows_cache: list[tuple[int, str, str, tuple[str, ...]]] | None = None

        self.title(f"Редактор слова - {source_id} / {page_name}")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = max(980, min(1360, screen_w - 120))
        window_h = max(680, min(860, screen_h - 140))
        pos_x = max(0, (screen_w - window_w) // 2)
        pos_y = max(0, (screen_h - window_h) // 2)
        self.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
        self.minsize(960, 640)
        self.transient(parent)
        self.grab_set()

        self.mode_label_var = tk.StringVar(value="Рисование")
        self.word_index_var = tk.IntVar(value=int(initial_payload.get("word_index") or 0))
        self.word_text_var = tk.StringVar(value=str(initial_payload.get("text") or ""))
        self.strong_pronounce_var = tk.BooleanVar(value=bool(initial_payload.get("strong_pronounce")))
        self.strong_x_shift_var = tk.StringVar(value=str(initial_payload.get("strong_x_shift") or "0"))
        self.missing_indexes = self._normalize_missing_indexes(initial_payload)
        self.missing_indexes_button_var = tk.StringVar(value=self._missing_indexes_caption())
        self.status_left_var = tk.StringVar(value="")
        self.status_right_var = tk.StringVar(value="")
        self.status_note = "Укажите слово и разметьте его прямоугольники."
        self.last_pointer_rel: tuple[float, float] | None = None
        self.pointer_outside = False
        self._tooltips: list[_ToolTip] = []

        self.image_path: Path | None = None
        self.image: Image.Image | None = None
        self.image_size = (0, 0)
        self.tk_image: ImageTk.PhotoImage | None = None
        self.image_cache_key: tuple[str, int, int] | None = None

        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 9.0
        self.pan_x = 16.0
        self.pan_y = 16.0
        self.panning = False
        self.pan_start = (0.0, 0.0)
        self.pan_base = (0.0, 0.0)

        self.rectangles: list[RectRel] = self._normalize_rectangles(initial_payload.get("rectangles_json"))
        self.active_rect_index: int | None = 0 if self.rectangles else None
        self.draw_start: tuple[float, float] | None = None
        self.draw_current: tuple[float, float] | None = None
        self.drag_rect_index: int | None = None
        self.drag_start: tuple[float, float] | None = None
        self.drag_origin_rect: RectRel | None = None

        self.strong_display_by_id: dict[int, str] = {}
        self.strong_id_by_display: dict[str, int] = {}
        strong_values = [""]
        for strong_id, word in sorted(strong_entries, key=lambda item: item[0]):
            display = f"{strong_id} | {word}"
            self.strong_display_by_id[strong_id] = display
            self.strong_id_by_display[display] = strong_id
            strong_values.append(display)
        self.strong_combo_values = strong_values
        self.strong_value_var = tk.StringVar(value="")
        initial_strong = self._parse_optional_int(initial_payload.get("strong_number"))
        if initial_strong is not None:
            if initial_strong not in self.strong_display_by_id:
                fallback_display = f"{initial_strong} | ?"
                self.strong_display_by_id[initial_strong] = fallback_display
                self.strong_id_by_display[fallback_display] = initial_strong
                self.strong_combo_values.append(fallback_display)
            self.strong_value_var.set(self.strong_display_by_id[initial_strong])

        self._build_ui()
        self._bind_events()
        self.word_text_var.trace_add("write", self._on_word_text_changed)
        self.strong_x_shift_var.trace_add("write", self._on_strong_shift_changed)

        self.load_image(image_path)
        self.protocol("WM_DELETE_WINDOW", self._close_dialog)

    def _close_dialog(self) -> None:
        self._close_greek_keyboard()
        self.destroy()

    def _normalize_missing_indexes(self, initial_payload: dict[str, object]) -> list[int]:
        raw = initial_payload.get("missing_char_indexes_json")
        if not isinstance(raw, list):
            return []
        indexes: list[int] = []
        for value in raw:
            try:
                index = int(value)
            except (TypeError, ValueError):
                continue
            if index >= 0:
                indexes.append(index)
        return sorted(set(indexes))

    def _normalize_rectangles(self, raw: object) -> list[RectRel]:
        rects: list[RectRel] = []
        payload = raw if isinstance(raw, list) else []
        for item in payload:
            if not isinstance(item, (list, tuple)) or len(item) != 4:
                continue
            try:
                x1, y1, x2, y2 = [float(value) for value in item]
            except (TypeError, ValueError):
                continue
            left, right = sorted((clamp01(x1), clamp01(x2)))
            top, bottom = sorted((clamp01(y1), clamp01(y2)))
            if right - left < 1e-6 or bottom - top < 1e-6:
                continue
            rects.append((left, top, right, bottom))
        return rects

    def _parse_optional_int(self, raw: object) -> int | None:
        if raw is None:
            return None
        text = str(raw).strip()
        if not text:
            return None
        return int(text)

    def _mode_key(self) -> str:
        return self.MODE_LABEL_TO_KEY.get(self.mode_label_var.get(), "draw")

    def _missing_indexes_caption(self) -> str:
        if not self.missing_indexes:
            return "Видно все буквы"
        return f"Нет букв {self.missing_indexes}"

    def _rectangles_status_text(self) -> str:
        active = "-" if self.active_rect_index is None else str(self.active_rect_index)
        return f"Прямоугольники: {len(self.rectangles)} | активный: {active}"

    def _render_status(self) -> None:
        left_parts = [f"Масштаб={self.zoom:.2f}x"]
        if self.last_pointer_rel is not None:
            left_parts.append(f"Точка=({self.last_pointer_rel[0]:.4f}, {self.last_pointer_rel[1]:.4f})")
        elif self.pointer_outside:
            left_parts.append("вне изображения")
        self.status_left_var.set("  ".join(left_parts))

        right_parts = [self._rectangles_status_text()]
        if self.status_note:
            right_parts.insert(0, self.status_note)
        self.status_right_var.set("  ".join(right_parts))

    def _set_status_note(self, note: str) -> None:
        self.status_note = note
        self._render_status()

    def _on_mode_changed(self, _event: object | None = None) -> None:
        if self._mode_key() != "draw":
            self.draw_start = None
            self.draw_current = None
        self.redraw()

    def _sync_missing_indexes_to_word(self) -> None:
        max_index = len(self.word_text_var.get()) - 1
        if max_index < 0:
            self.missing_indexes = []
        else:
            self.missing_indexes = [idx for idx in self.missing_indexes if 0 <= idx <= max_index]
        self.missing_indexes_button_var.set(self._missing_indexes_caption())

    def _on_word_text_changed(self, *_args: object) -> None:
        self._sync_missing_indexes_to_word()

    def _on_strong_shift_changed(self, *_args: object) -> None:
        self.redraw()

    def _toggle_greek_keyboard(self) -> None:
        if self.greek_keyboard_window is not None and self.greek_keyboard_window.winfo_exists():
            self._close_greek_keyboard()
            return

        keyboard = tk.Toplevel(self)
        self.greek_keyboard_window = keyboard
        keyboard.title("Греческие буквы")
        keyboard.transient(self)
        keyboard.resizable(False, False)

        frame = ttk.Frame(keyboard, padding=8)
        frame.grid(row=0, column=0, sticky="nsew")

        cols = 8
        for idx, letter in enumerate(self.GREEK_UPPERCASE_KEYS):
            row, col = divmod(idx, cols)
            btn = tk.Button(
                frame,
                text=letter,
                font=("Segoe UI", 16, "bold"),
                width=3,
                command=lambda ch=letter: self._insert_greek_letter(ch),
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        button_x = self.btn_greek_keyboard.winfo_rootx()
        button_y = self.btn_greek_keyboard.winfo_rooty() + self.btn_greek_keyboard.winfo_height() + 2
        keyboard.geometry(f"+{button_x}+{button_y}")
        keyboard.protocol("WM_DELETE_WINDOW", self._close_greek_keyboard)

    def _close_greek_keyboard(self) -> None:
        if self.greek_keyboard_window is None:
            return
        if self.greek_keyboard_window.winfo_exists():
            self.greek_keyboard_window.destroy()
        self.greek_keyboard_window = None

    def _insert_greek_letter(self, letter: str) -> None:
        try:
            insert_index = self.word_entry.index(tk.INSERT)
        except tk.TclError:
            insert_index = tk.END
        self.word_entry.insert(insert_index, letter)
        self.word_entry.focus_set()
        self.word_entry.icursor(tk.INSERT)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        top = ttk.Frame(self, padding=(8, 8, 8, 4))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)

        controls = ttk.Frame(top)
        controls.grid(row=0, column=0, sticky="w")

        btn_save_close = ttk.Button(controls, text="Сохранить и закрыть", command=self.save_to_db_close)
        btn_save_close.grid(row=0, column=0, padx=(2, 2))

        btn_save_new = ttk.Button(controls, text="Сохранить + новое слово", command=self.save_to_db_and_prepare_new)
        btn_save_new.grid(row=0, column=1, padx=(2, 2))

        btn_ocr = ttk.Button(controls, text="OCR", command=self._run_ocr)
        btn_ocr.grid(row=0, column=2, padx=(2, 2))

        self.btn_greek_keyboard = ttk.Button(controls, text="ΑΒΓ", command=self._toggle_greek_keyboard)
        self.btn_greek_keyboard.grid(row=0, column=3, padx=(2, 2))

        btn_find_strong = ttk.Button(controls, text="Найти # Стронга", command=self._find_strong_for_word)
        btn_find_strong.grid(row=0, column=4, padx=(2, 8))

        ttk.Label(controls, text="Режим:").grid(row=0, column=5, padx=(0, 4))
        self.mode_combo = ttk.Combobox(
            controls,
            textvariable=self.mode_label_var,
            values=list(self.MODE_LABEL_TO_KEY.keys()),
            state="readonly",
            width=14,
        )
        self.mode_combo.grid(row=0, column=6, padx=(0, 2))
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        meta = ttk.Frame(self, padding=(8, 0, 8, 6))
        meta.grid(row=1, column=0, sticky="ew")

        ttk.Label(meta, text="Индекс").grid(row=0, column=0, padx=(0, 4), pady=(0, 2))
        ttk.Spinbox(meta, from_=0, to=99999, textvariable=self.word_index_var, width=7).grid(
            row=0,
            column=1,
            pady=(0, 2),
        )

        ttk.Label(meta, text="X-сдвиг").grid(row=0, column=2, padx=(8, 4), pady=(0, 2))
        self.strong_shift_spin = ttk.Spinbox(
            meta,
            from_=-999.0,
            to=999.0,
            increment=0.001,
            textvariable=self.strong_x_shift_var,
            width=10,
        )
        self.strong_shift_spin.grid(row=0, column=3, pady=(0, 2), sticky="w")

        ttk.Label(meta, text="Слово").grid(row=0, column=4, padx=(8, 4), pady=(0, 2))
        self.word_entry = ttk.Entry(meta, textvariable=self.word_text_var, width=20)
        self.word_entry.grid(row=0, column=5, pady=(0, 2), sticky="w")

        ttk.Label(meta, text="Стронг").grid(row=0, column=6, padx=(8, 4), pady=(0, 2))
        self.strong_combo = ttk.Combobox(
            meta,
            textvariable=self.strong_value_var,
            values=self.strong_combo_values,
            state="readonly",
            width=18,
        )
        self.strong_combo.grid(row=0, column=7, pady=(0, 2), sticky="w")
        self.strong_combo.bind("<<ComboboxSelected>>", lambda _event: self.redraw())

        ttk.Checkbutton(
            meta,
            text="Произн. из Стронга",
            variable=self.strong_pronounce_var,
        ).grid(row=0, column=8, padx=(8, 8), pady=(0, 2), sticky="w")

        self.missing_button = ttk.Button(
            meta,
            textvariable=self.missing_indexes_button_var,
            command=self.edit_missing_letters,
        )
        self.missing_button.grid(row=0, column=9, pady=(0, 2), sticky="w")

        self.canvas = tk.Canvas(self, bg="#1f1f1f", highlightthickness=0)
        self.canvas.grid(row=2, column=0, sticky="nsew")

        status_frame = ttk.Frame(self, padding=(8, 4))
        status_frame.grid(row=3, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        ttk.Label(status_frame, textvariable=self.status_left_var, anchor="w").grid(row=0, column=0, sticky="w")
        ttk.Label(status_frame, textvariable=self.status_right_var, anchor="e").grid(row=0, column=1, sticky="e")

        self._install_tooltips(
            [
                (btn_save_close, "Сохранить слово в БД и закрыть окно."),
                (btn_save_new, "Сохранить текущее слово и сразу подготовить форму для нового."),
                (btn_ocr, "Распознать слово по выделенным прямоугольникам."),
                (btn_find_strong, "Найти номер Стронга по слову из поля 'Слово'."),
                (self.btn_greek_keyboard, "Показать/скрыть экранную клавиатуру с греческими буквами."),
                (self.mode_combo, "Режим работы с прямоугольниками: рисование, перемещение или удаление."),
                (self.missing_button, "Выбор букв, которых нет в исходнике (индексы будут сохранены в БД)."),
            ]
        )

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", lambda _event: self.redraw())
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-3>", lambda _event: setattr(self, "panning", False))
        self.canvas.bind("<MouseWheel>", self.on_wheel_win)
        self.canvas.bind("<Button-4>", self.on_wheel_linux)
        self.canvas.bind("<Button-5>", self.on_wheel_linux)
        self.canvas.bind("<Motion>", self.on_motion)
        self.bind("<Control-s>", lambda _event: self.save_to_db_close())

    def _install_tooltips(self, items: list[tuple[tk.Widget, str]]) -> None:
        for widget, text in items:
            self._tooltips.append(_ToolTip(widget, text))

    def _run_ocr(self) -> None:
        if self.image is None:
            messagebox.showwarning("OCR", "Изображение не загружено.", parent=self)
            return
        if not self.rectangles:
            messagebox.showinfo("OCR", "Сначала разметьте прямоугольники слова.", parent=self)
            return

        try:
            recognized = recognize_greek_word_from_fragments(
                self.image,
                self.rectangles,
                source_id=self.source_id,
            )
        except OcrSetupError as exc:
            messagebox.showwarning("OCR", str(exc), parent=self)
            self._set_status_note("OCR не настроен.")
            return
        except Exception as exc:
            messagebox.showerror("OCR", f"Ошибка OCR: {exc}", parent=self)
            self._set_status_note("OCR завершился с ошибкой.")
            return

        if not recognized:
            messagebox.showinfo(
                "OCR",
                "По заданным прямоугольникам не удалось распознать слово.",
                parent=self,
            )
            self._set_status_note("OCR ничего не нашел.")
            return

        self.word_text_var.set(recognized)
        self.word_entry.focus_set()
        self.word_entry.icursor(tk.END)
        self._set_status_note(f"OCR: {recognized}")

    def _find_strong_for_word(self) -> None:
        word = self.word_text_var.get().strip()
        if not word:
            messagebox.showinfo("Найти # Стронга", "Сначала введите слово.", parent=self)
            return
        normalized_word = self._normalize_strong_lookup_text(word)
        if not normalized_word:
            messagebox.showinfo(
                "Найти # Стронга",
                "В слове не осталось букв после нормализации. Уточните запрос.",
                parent=self,
            )
            return

        common_connection = getattr(self.parent_tool, "common_connection", None)
        if common_connection is None:
            messagebox.showwarning(
                "Найти # Стронга",
                "Общая БД не подключена. Поиск по словарю Стронга недоступен.",
                parent=self,
            )
            return

        strong_id = self._lookup_strong_id_by_usage(common_connection, normalized_word)
        if strong_id is None:
            messagebox.showinfo("Найти # Стронга", f"Слово '{word}' не найдено в словаре Стронга.", parent=self)
            return

        display = self.strong_display_by_id.get(strong_id)
        if display is None:
            display = f"{strong_id} | ?"
            self.strong_display_by_id[strong_id] = display
            self.strong_id_by_display[display] = strong_id
            if display not in self.strong_combo_values:
                self.strong_combo_values.append(display)
                self.strong_combo.configure(values=self.strong_combo_values)

        self.strong_value_var.set(display)
        self._set_status_note(f"Найден Strong #{strong_id} для слова '{word}'.")
        self.redraw()

    def _normalize_strong_lookup_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFD", text or "")
        without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        folded = without_marks.casefold().translate(self.STRONG_SEARCH_CHAR_TRANSLATION)
        cleaned = "".join(char if char.isalnum() else " " for char in folded)
        return " ".join(cleaned.split())

    def _lookup_strong_id_by_usage(self, connection: sqlite3.Connection, normalized_word: str) -> int | None:
        if not normalized_word:
            return None
        normalized_rows = self._normalized_strong_rows(connection)
        if not normalized_rows:
            return None

        # 1) Highest priority: exact match in greek_words.word
        for strong_id, normalized_db_word, _normalized_usage, _usage_tokens in normalized_rows:
            if normalized_db_word and normalized_db_word == normalized_word:
                return strong_id

        # 2) Next priority: exact standalone word in greek_words.usage
        for strong_id, _normalized_db_word, _normalized_usage, usage_tokens in normalized_rows:
            if normalized_word in usage_tokens:
                return strong_id

        # 3) Last priority: query is only a part of found words
        best_partial: tuple[int, int, int] | None = None
        for strong_id, normalized_db_word, normalized_usage, usage_tokens in normalized_rows:
            if normalized_db_word and normalized_word in normalized_db_word and normalized_db_word != normalized_word:
                candidate = (0, len(normalized_db_word), strong_id)
                if best_partial is None or candidate < best_partial:
                    best_partial = candidate

            usage_token_matches = [
                token
                for token in usage_tokens
                if normalized_word in token and token != normalized_word
            ]
            if usage_token_matches:
                candidate = (1, min(len(token) for token in usage_token_matches), strong_id)
                if best_partial is None or candidate < best_partial:
                    best_partial = candidate
                continue

            if normalized_usage and normalized_word in normalized_usage and normalized_usage != normalized_word:
                candidate = (2, len(normalized_usage), strong_id)
                if best_partial is None or candidate < best_partial:
                    best_partial = candidate

        if best_partial is None:
            return None
        return best_partial[2]

    def _normalized_strong_rows(self, connection: sqlite3.Connection) -> list[tuple[int, str, str, tuple[str, ...]]]:
        if self._normalized_strong_rows_cache is not None:
            return self._normalized_strong_rows_cache

        try:
            rows = connection.execute(
                """
                SELECT id, word, usage
                FROM greek_words
                ORDER BY id ASC
                """
            ).fetchall()
        except sqlite3.DatabaseError:
            return []

        payload: list[tuple[int, str, str, tuple[str, ...]]] = []
        for row in rows:
            strong_id = int(row[0])
            normalized_db_word = self._normalize_strong_lookup_text(str(row[1] or ""))
            normalized_usage = self._normalize_strong_lookup_text(str(row[2] or ""))
            usage_tokens = tuple(normalized_usage.split()) if normalized_usage else tuple()
            payload.append((strong_id, normalized_db_word, normalized_usage, usage_tokens))

        self._normalized_strong_rows_cache = payload
        return payload

    def edit_missing_letters(self) -> None:
        word = self.word_text_var.get()
        if not word:
            messagebox.showinfo("Нет слова", "Сначала введите слово.", parent=self)
            return

        chars = list(word)
        selected = set(self.missing_indexes)

        dialog = tk.Toplevel(self)
        dialog.title("Отсутствующие буквы")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, True)

        root = ttk.Frame(dialog, padding=10)
        root.grid(row=0, column=0, sticky="nsew")
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        list_host = ttk.Frame(root)
        list_host.grid(row=0, column=0, sticky="nsew")
        list_host.columnconfigure(0, weight=1)
        list_host.rowconfigure(0, weight=1)

        canvas_height = min(420, max(140, len(chars) * 28))
        canvas = tk.Canvas(list_host, height=canvas_height, width=220, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_host, orient="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)

        rows = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=rows, anchor="nw")
        rows.columnconfigure(0, weight=1)

        flags: list[tk.BooleanVar] = []
        for idx, char in enumerate(chars):
            display = char if char.strip() else "␠"
            ttk.Label(rows, text=f"{idx}: {display}").grid(row=idx, column=0, sticky="w", padx=(0, 8), pady=2)
            flag = tk.BooleanVar(value=idx in selected)
            flags.append(flag)
            ttk.Checkbutton(rows, variable=flag).grid(row=idx, column=1, sticky="w", pady=2)

        def _refresh_scroll_region(_event: object | None = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        rows.bind("<Configure>", _refresh_scroll_region)
        _refresh_scroll_region()

        actions = ttk.Frame(root)
        actions.grid(row=1, column=0, sticky="e", pady=(8, 0))

        def _apply() -> None:
            self.missing_indexes = [idx for idx, flag in enumerate(flags) if flag.get()]
            self.missing_indexes_button_var.set(self._missing_indexes_caption())
            self._set_status_note("Обновлены отсутствующие буквы.")
            dialog.destroy()

        ttk.Button(actions, text="OK", command=_apply).pack(side="left")
        ttk.Button(actions, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.wait_window()

    def load_image(self, path: Path) -> None:
        self.image = Image.open(path).convert("RGB")
        self.image_path = path
        self.image_size = self.image.size
        self.image_cache_key = None
        self._set_status_note(f"Загружено: {path.name}")
        self.after(40, self.fit_view)

    def fit_view(self) -> None:
        if self.image is None:
            self.redraw()
            return
        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())
        image_width, image_height = self.image_size
        if canvas_width <= 1 or canvas_height <= 1:
            self.after(30, self.fit_view)
            return
        self.zoom = max(
            self.min_zoom,
            min(self.max_zoom, min((canvas_width - 30) / image_width, (canvas_height - 30) / image_height)),
        )
        self.pan_x = (canvas_width - image_width * self.zoom) / 2
        self.pan_y = (canvas_height - image_height * self.zoom) / 2
        self.redraw()

    def rel_to_canvas(self, point: tuple[float, float]) -> tuple[float, float]:
        image_width, image_height = self.image_size
        return (self.pan_x + point[0] * image_width * self.zoom, self.pan_y + point[1] * image_height * self.zoom)

    def canvas_to_rel(self, x: float, y: float) -> tuple[float, float] | None:
        if self.image is None:
            return None
        image_width, image_height = self.image_size
        image_x = (x - self.pan_x) / self.zoom
        image_y = (y - self.pan_y) / self.zoom
        if image_x < 0 or image_y < 0 or image_x > image_width or image_y > image_height:
            return None
        return (clamp01(image_x / image_width), clamp01(image_y / image_height))

    def rect_to_canvas(self, rect: RectRel) -> tuple[float, float, float, float]:
        x1, y1 = self.rel_to_canvas((rect[0], rect[1]))
        x2, y2 = self.rel_to_canvas((rect[2], rect[3]))
        return (x1, y1, x2, y2)

    def _find_rect_at(self, rel: tuple[float, float]) -> int | None:
        for idx in range(len(self.rectangles) - 1, -1, -1):
            x1, y1, x2, y2 = self.rectangles[idx]
            if x1 <= rel[0] <= x2 and y1 <= rel[1] <= y2:
                return idx
        return None

    def _finalize_draw_rect(self, start: tuple[float, float], end: tuple[float, float]) -> None:
        left, right = sorted((clamp01(start[0]), clamp01(end[0])))
        top, bottom = sorted((clamp01(start[1]), clamp01(end[1])))
        if right - left < 1e-6 or bottom - top < 1e-6:
            self._set_status_note("Слишком маленький прямоугольник, пропущен.")
            return
        self.rectangles.append((left, top, right, bottom))
        self.active_rect_index = len(self.rectangles) - 1
        self.redraw()

    def on_left_down(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return

        mode = self._mode_key()
        if mode == "draw":
            if self.draw_start is None:
                self.draw_start = rel
                self.draw_current = rel
                self._set_status_note("Выберите правый нижний угол прямоугольника.")
            else:
                self._finalize_draw_rect(self.draw_start, rel)
                self.draw_start = None
                self.draw_current = None
            return

        rect_index = self._find_rect_at(rel)
        if rect_index is None:
            return

        self.active_rect_index = rect_index
        if mode == "delete":
            self.rectangles.pop(rect_index)
            self.active_rect_index = min(rect_index, len(self.rectangles) - 1) if self.rectangles else None
            self._set_status_note("Прямоугольник удален.")
            self.redraw()
            return

        if mode == "move":
            self.drag_rect_index = rect_index
            self.drag_start = rel
            self.drag_origin_rect = self.rectangles[rect_index]
            self.redraw()

    def on_left_drag(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return

        if self._mode_key() == "draw" and self.draw_start is not None:
            self.draw_current = rel
            self.redraw()
            return

        if self._mode_key() != "move":
            return
        if self.drag_rect_index is None or self.drag_start is None or self.drag_origin_rect is None:
            return

        dx = rel[0] - self.drag_start[0]
        dy = rel[1] - self.drag_start[1]
        x1, y1, x2, y2 = self.drag_origin_rect
        width = x2 - x1
        height = y2 - y1
        new_x1 = min(max(x1 + dx, 0.0), 1.0 - width)
        new_y1 = min(max(y1 + dy, 0.0), 1.0 - height)
        self.rectangles[self.drag_rect_index] = (
            clamp01(new_x1),
            clamp01(new_y1),
            clamp01(new_x1 + width),
            clamp01(new_y1 + height),
        )
        self.redraw()

    def on_left_up(self, _event: tk.Event[tk.Misc]) -> None:
        self.drag_rect_index = None
        self.drag_start = None
        self.drag_origin_rect = None

    def on_pan_start(self, event: tk.Event[tk.Misc]) -> None:
        self.panning = True
        self.pan_start = (event.x, event.y)
        self.pan_base = (self.pan_x, self.pan_y)

    def on_pan_drag(self, event: tk.Event[tk.Misc]) -> None:
        if not self.panning:
            return
        self.pan_x = self.pan_base[0] + (event.x - self.pan_start[0])
        self.pan_y = self.pan_base[1] + (event.y - self.pan_start[1])
        self.redraw()

    def on_wheel_win(self, event: tk.Event[tk.Misc]) -> None:
        self.zoom_at(event.x, event.y, 1.1 if event.delta > 0 else 1 / 1.1)

    def on_wheel_linux(self, event: tk.Event[tk.Misc]) -> None:
        self.zoom_at(event.x, event.y, 1.1 if event.num == 4 else 1 / 1.1)

    def zoom_at(self, x: float, y: float, factor: float) -> None:
        if self.image is None:
            return
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        if abs(self.zoom - old_zoom) < 1e-8:
            return
        self.pan_x = x - (x - self.pan_x) * (self.zoom / old_zoom)
        self.pan_y = y - (y - self.pan_y) * (self.zoom / old_zoom)
        self.redraw()

    def on_motion(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            self.last_pointer_rel = None
            self.pointer_outside = True
        else:
            self.last_pointer_rel = rel
            self.pointer_outside = False
        self._render_status()

    def _selected_strong_number(self) -> int | None:
        raw = self.strong_value_var.get().strip()
        if not raw:
            return None
        return self.strong_id_by_display.get(raw)

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.image is None:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="Изображение страницы не загружено",
                fill="#ccc",
            )
            self._render_status()
            return

        image_width, image_height = self.image_size
        draw_width = max(1, int(image_width * self.zoom))
        draw_height = max(1, int(image_height * self.zoom))
        cache_key = (str(self.image_path), draw_width, draw_height)
        if cache_key != self.image_cache_key:
            resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            self.tk_image = ImageTk.PhotoImage(self.image.resize((draw_width, draw_height), resampling))
            self.image_cache_key = cache_key
        self.canvas.create_image(self.pan_x, self.pan_y, image=self.tk_image, anchor="nw")

        for idx, rect in enumerate(self.rectangles):
            x1, y1, x2, y2 = self.rect_to_canvas(rect)
            is_active = idx == self.active_rect_index
            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline="#0fa06f" if is_active else "#0b8561",
                width=3 if is_active else 2,
                fill="",
            )
            self.canvas.create_text(
                x1 + 4,
                y1 + 4,
                text=str(idx),
                fill="#0b5f47",
                anchor="nw",
                font=("Segoe UI", 8, "bold"),
            )

        if self.draw_start is not None and self.draw_current is not None:
            px1, py1 = self.rel_to_canvas(self.draw_start)
            px2, py2 = self.rel_to_canvas(self.draw_current)
            self.canvas.create_rectangle(px1, py1, px2, py2, outline="#3fc5ff", width=2, dash=(6, 3))

        strong_number = self._selected_strong_number()
        if strong_number is not None and self.rectangles:
            try:
                shift = float(self.strong_x_shift_var.get().strip().replace(",", "."))
            except ValueError:
                shift = 0.0
            first_rect = self.rectangles[0]
            font_size = max(9, int(draw_height * 0.004))
            x = self.pan_x + (first_rect[0] + shift) * image_width * self.zoom + (font_size * 0.2)
            y = self.pan_y + first_rect[1] * image_height * self.zoom - (font_size * 1.2)
            self.canvas.create_text(
                x,
                y,
                text=str(strong_number),
                fill="#4a4cff",
                anchor="nw",
                font=("Segoe UI", font_size, "bold"),
            )

        self._render_status()

    def _build_payload(self) -> dict[str, object] | None:
        text = self.word_text_var.get().strip()
        if not text:
            messagebox.showwarning("Ошибка данных", "Слово обязательно.", parent=self)
            return None
        try:
            strong_shift = float(self.strong_x_shift_var.get().strip().replace(",", ".") or "0")
        except ValueError:
            messagebox.showwarning("Ошибка данных", "Некорректный X-сдвиг.", parent=self)
            return None

        return {
            "word_index": str(self.word_index_var.get()),
            "text": text,
            "strong_number": "" if self._selected_strong_number() is None else str(self._selected_strong_number()),
            "strong_pronounce": bool(self.strong_pronounce_var.get()),
            "strong_x_shift": str(strong_shift),
            "missing_char_indexes_json": list(self.missing_indexes),
            "rectangles_json": [list(rect) for rect in self.rectangles],
        }

    def _save_payload(self, payload: dict[str, object]) -> bool:
        try:
            result = self.on_save(payload, self.previous_word_index)
        except Exception as exc:
            messagebox.showerror("Ошибка сохранения", str(exc), parent=self)
            return False
        if result is False:
            return False
        return True

    def _occupied_word_indexes(self) -> set[int]:
        rows = getattr(self.parent_tool, "primary_source_word_rows", [])
        occupied: set[int] = set()
        for row in rows:
            try:
                occupied.add(int(row["word_index"] or 0))
            except (TypeError, ValueError, KeyError):
                continue
        return occupied

    def _next_free_word_index(self, start: int) -> int:
        occupied = self._occupied_word_indexes()
        candidate = max(0, int(start))
        while candidate in occupied:
            candidate += 1
        return candidate

    def _reset_editor_for_new_word(self, next_index: int) -> None:
        self.previous_word_index = None
        self.word_index_var.set(next_index)
        self.word_text_var.set("")
        self.strong_value_var.set("")
        self.strong_pronounce_var.set(False)
        self.strong_x_shift_var.set("0")
        self.missing_indexes = []
        self.missing_indexes_button_var.set(self._missing_indexes_caption())
        self.mode_label_var.set("Рисование")
        self.draw_start = None
        self.draw_current = None
        self.drag_rect_index = None
        self.drag_start = None
        self.drag_origin_rect = None
        self.rectangles.clear()
        self.active_rect_index = None
        self._set_status_note(f"Слово сохранено. Подготовлено новое, индекс {next_index}.")
        self.redraw()

    def save_to_db_close(self) -> None:
        payload = self._build_payload()
        if payload is None:
            return
        if self._save_payload(payload):
            self._close_dialog()

    def save_to_db_and_prepare_new(self) -> None:
        payload = self._build_payload()
        if payload is None:
            return
        if not self._save_payload(payload):
            return
        current_index = int(payload["word_index"])
        next_index = self._next_free_word_index(current_index + 1)
        self._reset_editor_for_new_word(next_index)
