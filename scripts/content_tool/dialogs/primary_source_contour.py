from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any, Callable

from ..compat import Image, ImageTk
from ..helpers import clamp01, format_indexes_for_ui, parse_indexes, parse_verse_snippet
from ..models import Point
from ..widgets import _ToolTip

if TYPE_CHECKING:
    from ..app import TopicContentTool


class PrimarySourceContourEditorDialog(tk.Toplevel):
    def __init__(
        self,
        *,
        parent: TopicContentTool,
        image_path: Path,
        source_id: str,
        page_name: str,
        initial_payload: dict[str, object],
        previous_verse_index: int | None,
        on_save: Callable[[dict[str, object], int | None], bool],
    ) -> None:
        super().__init__(parent)
        self.parent_tool = parent
        self.source_id = source_id
        self.page_name = page_name
        self.start_dir = image_path.parent
        self.on_save = on_save
        self.previous_verse_index = previous_verse_index

        self.title(f"Редактор контуров - {source_id} / {page_name}")
        self.geometry("1380x900")
        self.minsize(1040, 720)
        self.transient(parent)
        self.grab_set()

        self.mode = tk.StringVar(value="add")
        self.snap_axis = tk.BooleanVar(value=True)
        self.verse_index_var = tk.IntVar(value=int(initial_payload.get("verse_index") or 0))
        self.chapter = tk.IntVar(value=int(initial_payload.get("chapter_number") or 1))
        self.verse = tk.IntVar(value=int(initial_payload.get("verse_number") or 1))
        self.word_indexes = tk.StringVar(
            value=format_indexes_for_ui([int(v) for v in initial_payload.get("word_indexes", [])])
        )
        self.label_text = tk.StringVar(value="Метка: -")
        self.status = tk.StringVar(value="Откройте изображение и размечайте.")
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

        initial_contours = initial_payload.get("contours", [])
        self.contours: list[list[Point]] = []
        for contour in initial_contours if isinstance(initial_contours, list) else []:
            points: list[Point] = []
            if isinstance(contour, list):
                for point in contour:
                    if not isinstance(point, (list, tuple)) or len(point) != 2:
                        continue
                    points.append((clamp01(float(point[0])), clamp01(float(point[1]))))
            if points:
                self.contours.append(points)
        if not self.contours:
            self.contours = [[]]
        self.active_contour = 0
        self.drag_point: tuple[int, int] | None = None
        self.wait_label_pick = False
        self.label_position: Point | None = None
        if "label_x" in initial_payload and "label_y" in initial_payload:
            self.label_position = (
                clamp01(float(initial_payload["label_x"])),
                clamp01(float(initial_payload["label_y"])),
            )
        elif self.contours and self.contours[0]:
            self.label_position = self.contours[0][0]
        self.panning = False
        self.pan_start = (0.0, 0.0)
        self.pan_base = (0.0, 0.0)

        self._build_ui()
        self._bind_events()
        self._refresh_label_text()
        self._refresh_contour_info()
        self.load_image(image_path)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=8)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(
            top,
            text=f"{self.source_id} / {self.page_name}",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))
        btn_open = ttk.Button(top, text="Открыть", command=self.open_image)
        btn_open.grid(row=0, column=1, padx=2)
        btn_save = ttk.Button(top, text="В БД", command=self.save_to_db)
        btn_save.grid(row=0, column=2, padx=(6, 2))
        btn_close = ttk.Button(top, text="Закрыть", command=self.destroy)
        btn_close.grid(row=0, column=3, padx=(2, 6))
        btn_new = ttk.Button(top, text="Новый", command=self.new_contour)
        btn_new.grid(row=0, column=4, padx=2)
        btn_clear = ttk.Button(top, text="Очистить", command=self.clear_contour)
        btn_clear.grid(row=0, column=5, padx=2)
        btn_delete = ttk.Button(top, text="Удалить", command=self.delete_contour)
        btn_delete.grid(row=0, column=6, padx=2)
        btn_label = ttk.Button(top, text="Метка", command=self.pick_label)
        btn_label.grid(row=0, column=7, padx=4)
        btn_copy_contours = ttk.Button(top, text="Коп. конт.", command=self.copy_contours)
        btn_copy_contours.grid(row=0, column=8, padx=2)
        btn_copy_verse = ttk.Button(top, text="Коп. стих", command=self.copy_verse)
        btn_copy_verse.grid(row=0, column=9, padx=2)
        btn_import_verse = ttk.Button(top, text="Имп. стих", command=self.import_verse_dialog)
        btn_import_verse.grid(row=0, column=10, padx=2)
        check_snap_axis = ttk.Checkbutton(top, text="Ось", variable=self.snap_axis)
        check_snap_axis.grid(row=0, column=11, padx=6)

        mode_frame = ttk.Frame(top)
        mode_frame.grid(row=0, column=12, padx=6)
        ttk.Label(mode_frame, text="Режим:").grid(row=0, column=0, padx=(0, 4))
        mode_buttons: dict[str, ttk.Radiobutton] = {}
        for col, (title, value) in enumerate([("Доб.", "add"), ("Сдв.", "move"), ("Удал.", "delete")], start=1):
            button = ttk.Radiobutton(mode_frame, text=title, value=value, variable=self.mode)
            button.grid(
                row=0,
                column=col,
                padx=2,
            )
            mode_buttons[value] = button

        meta = ttk.Frame(top)
        meta.grid(row=1, column=0, columnspan=13, sticky="ew", pady=(8, 0))
        ttk.Label(meta, text="Индекс").grid(row=0, column=0, padx=(0, 4))
        ttk.Spinbox(meta, from_=0, to=9999, textvariable=self.verse_index_var, width=6).grid(row=0, column=1)
        ttk.Label(meta, text="Гл.").grid(row=0, column=2, padx=(10, 4))
        ttk.Spinbox(meta, from_=1, to=999, textvariable=self.chapter, width=5).grid(row=0, column=3)
        ttk.Label(meta, text="Стих").grid(row=0, column=4, padx=(8, 4))
        ttk.Spinbox(meta, from_=1, to=999, textvariable=self.verse, width=5).grid(row=0, column=5)
        ttk.Label(meta, text="Слова").grid(row=0, column=6, padx=(8, 4))
        ttk.Entry(meta, textvariable=self.word_indexes, width=56).grid(row=0, column=7, sticky="ew")
        ttk.Label(meta, textvariable=self.label_text).grid(row=0, column=8, padx=(10, 0), sticky="w")

        self.canvas = tk.Canvas(self, bg="#1f1f1f", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        ttk.Label(self, textvariable=self.status, anchor="w", padding=(8, 4)).grid(row=2, column=0, sticky="ew")

        self._install_tooltips(
            [
                (btn_open, "Открыть другое изображение."),
                (btn_save, "Сохранить стих и контуры в БД."),
                (btn_close, "Закрыть редактор."),
                (btn_new, "Создать новый контур."),
                (btn_clear, "Очистить точки активного контура."),
                (btn_delete, "Удалить активный контур."),
                (btn_label, "Поставить метку стиха на изображении."),
                (btn_copy_contours, "Скопировать только контуры."),
                (btn_copy_verse, "Скопировать готовый стих."),
                (btn_import_verse, "Импортировать Verse(...) из старых данных."),
                (check_snap_axis, "Выравнивать новую точку по оси X или Y."),
                (mode_buttons["add"], "Добавлять точки в активный контур."),
                (mode_buttons["move"], "Перетаскивать существующие точки."),
                (mode_buttons["delete"], "Удалять точки щелчком."),
            ]
        )

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", lambda _e: self.redraw())
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda _e: setattr(self, "drag_point", None))
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-3>", lambda _e: setattr(self, "panning", False))
        self.canvas.bind("<MouseWheel>", self.on_wheel_win)
        self.canvas.bind("<Button-4>", self.on_wheel_linux)
        self.canvas.bind("<Button-5>", self.on_wheel_linux)
        self.canvas.bind("<Motion>", self.on_motion)
        self.bind("<Control-o>", lambda _e: self.open_image())
        self.bind("<Control-s>", lambda _e: self.save_to_db())
        self.bind("<Control-c>", lambda _e: self.copy_contours())
        self.bind("<Control-i>", lambda _e: self.import_verse_dialog())

    def open_image(self) -> None:
        init = self.start_dir if self.start_dir.exists() else Path.cwd()
        file_path = filedialog.askopenfilename(
            parent=self,
            initialdir=str(init),
            title="Открыть изображение",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff"), ("Все файлы", "*.*")],
        )
        if file_path:
            self.load_image(Path(file_path))

    def load_image(self, path: Path) -> None:
        self.image = Image.open(path).convert("RGB")
        self.image_path = path
        self.image_size = self.image.size
        self.image_cache_key = None
        self.start_dir = path.parent
        self.status.set(f"Загружено: {path.name}")
        self.after(40, self.fit_view)

    def fit_view(self) -> None:
        if self.image is None:
            self.redraw()
            return
        cw, ch = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        iw, ih = self.image_size
        if cw <= 1 or ch <= 1:
            self.after(30, self.fit_view)
            return
        self.zoom = max(self.min_zoom, min(self.max_zoom, min((cw - 30) / iw, (ch - 30) / ih)))
        self.pan_x = (cw - iw * self.zoom) / 2
        self.pan_y = (ch - ih * self.zoom) / 2
        self.redraw()

    def rel_to_canvas(self, point: Point) -> Point:
        iw, ih = self.image_size
        return (self.pan_x + point[0] * iw * self.zoom, self.pan_y + point[1] * ih * self.zoom)

    def canvas_to_rel(self, x: float, y: float) -> Point | None:
        if self.image is None:
            return None
        iw, ih = self.image_size
        ix = (x - self.pan_x) / self.zoom
        iy = (y - self.pan_y) / self.zoom
        if ix < 0 or iy < 0 or ix > iw or iy > ih:
            return None
        return (clamp01(ix / iw), clamp01(iy / ih))

    def nearest_point(self, x: float, y: float) -> tuple[int, int] | None:
        best: tuple[int, int] | None = None
        best_d2 = 12 * 12
        for ci, contour in enumerate(self.contours):
            for pi, point in enumerate(contour):
                px, py = self.rel_to_canvas(point)
                d2 = (px - x) ** 2 + (py - y) ** 2
                if d2 <= best_d2:
                    best, best_d2 = (ci, pi), d2
        return best

    def on_left_down(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return
        if self.wait_label_pick:
            self.wait_label_pick = False
            self.label_position = rel
            self._refresh_label_text()
            self.redraw()
            return
        mode = self.mode.get()
        if mode == "add":
            contour = self.contours[self.active_contour]
            if contour and self.snap_axis.get():
                px, py = contour[-1]
                dx, dy = abs(rel[0] - px), abs(rel[1] - py)
                rel = (px, rel[1]) if dx < dy else (rel[0], py)
            contour.append(rel)
            self._refresh_contour_info()
            self.redraw()
            return
        near = self.nearest_point(event.x, event.y)
        if near is None:
            return
        ci, pi = near
        if mode == "move":
            self.active_contour = ci
            self.drag_point = (ci, pi)
            self._refresh_contour_info()
        elif mode == "delete":
            self.contours[ci].pop(pi)
            self._refresh_contour_info()
            self.redraw()

    def on_left_drag(self, event: tk.Event[tk.Misc]) -> None:
        if self.drag_point is None:
            return
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return
        ci, pi = self.drag_point
        self.contours[ci][pi] = rel
        self.redraw()

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
            self.status.set(f"Режим={self._mode_label()}  Масштаб={self.zoom:.2f}x  вне изображения")
            return
        self.status.set(
            f"Режим={self._mode_label()}  Масштаб={self.zoom:.2f}x  Точка=({rel[0]:.4f}, {rel[1]:.4f})"
        )

    def new_contour(self) -> None:
        self.contours.append([])
        self.active_contour = len(self.contours) - 1
        self._refresh_contour_info()
        self.redraw()

    def clear_contour(self) -> None:
        self.contours[self.active_contour].clear()
        self._refresh_contour_info()
        self.redraw()

    def delete_contour(self) -> None:
        if len(self.contours) <= 1:
            self.contours[0].clear()
        else:
            self.contours.pop(self.active_contour)
            self.active_contour = max(0, self.active_contour - 1)
        self._refresh_contour_info()
        self.redraw()

    def pick_label(self) -> None:
        self.wait_label_pick = True
        self.status.set("Щёлкните по изображению, чтобы поставить метку.")

    def import_verse_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Импорт стиха")
        dialog.geometry("900x560")
        dialog.minsize(700, 420)
        dialog.transient(self)
        dialog.grab_set()

        container = ttk.Frame(dialog, padding=8)
        container.pack(fill="both", expand=True)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        ttk.Label(
            container,
            text=(
                "Вставьте блок Verse(...) из старого снимка первоисточников.\n"
                "Нужны поля: chapterNumber, verseNumber, labelPosition, wordIndexes, contours."
            ),
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        text = tk.Text(container, wrap="none")
        text.grid(row=1, column=0, sticky="nsew", pady=(8, 8))

        y_scroll = ttk.Scrollbar(container, orient="vertical", command=text.yview)
        y_scroll.grid(row=1, column=1, sticky="ns", pady=(8, 8))
        text.configure(yscrollcommand=y_scroll.set)

        try:
            clip = self.clipboard_get()
            if isinstance(clip, str) and "Verse(" in clip:
                text.insert("1.0", clip)
        except tk.TclError:
            pass

        buttons = ttk.Frame(container)
        buttons.grid(row=2, column=0, sticky="e")

        def do_import() -> None:
            raw = text.get("1.0", "end").strip()
            if not raw:
                messagebox.showwarning("Импорт", "Сначала вставьте Verse(...).", parent=dialog)
                return
            try:
                payload = parse_verse_snippet(raw)
                self.apply_imported_verse(payload)
            except Exception as exc:
                messagebox.showerror("Импорт", f"Не удалось разобрать фрагмент:\n{exc}", parent=dialog)
                return
            dialog.destroy()

        ttk.Button(buttons, text="Импорт", command=do_import).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Отмена", command=dialog.destroy).grid(row=0, column=1)

        text.focus_set()
        self.wait_window(dialog)

    def apply_imported_verse(self, payload: dict[str, object]) -> None:
        chapter = int(payload["chapter"])
        verse = int(payload["verse"])
        indexes = [int(v) for v in payload.get("word_indexes", [])]
        raw_contours = payload.get("contours", [])

        contours: list[list[Point]] = []
        for contour in raw_contours if isinstance(raw_contours, list) else []:
            points: list[Point] = []
            if isinstance(contour, list):
                for x, y in contour:
                    points.append((clamp01(float(x)), clamp01(float(y))))
            if points:
                contours.append(points)
        if not contours:
            raise ValueError("У импортированного стиха нет контуров.")

        self.chapter.set(chapter)
        self.verse.set(verse)
        self.word_indexes.set(format_indexes_for_ui(indexes))
        self.contours = contours
        self.active_contour = 0
        self.drag_point = None

        label = payload.get("label")
        if label is None:
            label = contours[0][0]
        self.label_position = (clamp01(float(label[0])), clamp01(float(label[1])))
        self._refresh_label_text()
        self._refresh_contour_info()
        self.redraw()
        self.status.set(f"Импортирован стих {chapter}:{verse}, контуров: {len(contours)}.")

    def _refresh_label_text(self) -> None:
        if self.label_position is None:
            self.label_text.set("Метка: -")
            return
        self.label_text.set(f"Метка: ({self.label_position[0]:.4f}, {self.label_position[1]:.4f})")

    def _refresh_contour_info(self) -> None:
        if not self.contours:
            self.contours = [[]]
            self.active_contour = 0
        summary = ", ".join(f"{index + 1}:{len(contour)}" for index, contour in enumerate(self.contours))
        self.status.set(f"Контуры [{summary}] | активный={self.active_contour + 1}")

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.image is None:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="Откройте изображение",
                fill="#ccc",
            )
            return
        iw, ih = self.image_size
        dw, dh = max(1, int(iw * self.zoom)), max(1, int(ih * self.zoom))
        cache_key = (str(self.image_path), dw, dh)
        if cache_key != self.image_cache_key:
            resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            self.tk_image = ImageTk.PhotoImage(self.image.resize((dw, dh), resampling))
            self.image_cache_key = cache_key
        self.canvas.create_image(self.pan_x, self.pan_y, image=self.tk_image, anchor="nw")
        for contour_index, contour in enumerate(self.contours):
            if len(contour) < 1:
                continue
            color = "#00a06f" if contour_index == self.active_contour else "#0b8561"
            pts = [self.rel_to_canvas(point) for point in contour]
            if len(pts) >= 2:
                flat = [xy for point in pts for xy in point]
                self.canvas.create_line(*flat, fill=color, width=3 if contour_index == self.active_contour else 2)
                if len(pts) >= 3 and contour[0] != contour[-1]:
                    self.canvas.create_line(*pts[-1], *pts[0], fill=color, width=2, dash=(4, 4))
            for point_index, (x, y) in enumerate(pts):
                radius = 4 if contour_index == self.active_contour else 3
                self.canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill="#0b5f47",
                    outline="",
                )
                if contour_index == self.active_contour:
                    self.canvas.create_text(
                        x + 8,
                        y - 8,
                        text=str(point_index),
                        fill="#0b5f47",
                        anchor="sw",
                        font=("Segoe UI", 8),
                    )
        if self.label_position:
            lx, ly = self.rel_to_canvas(self.label_position)
            self.canvas.create_rectangle(lx - 5, ly - 5, lx + 5, ly + 5, outline="#ffe066", width=2)
            self.canvas.create_text(
                lx + 9,
                ly,
                text=f"{self.chapter.get()}:{self.verse.get()}",
                fill="#ffe066",
                anchor="w",
                font=("Segoe UI", 11, "bold"),
            )

    def filtered_contours(self) -> list[list[Point]]:
        result: list[list[Point]] = []
        for contour in self.contours:
            points = contour[:-1] if len(contour) >= 2 and contour[0] == contour[-1] else contour
            if len(points) >= 3:
                result.append(points)
        return result

    def copy_contours(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Копирование", "Нужен хотя бы один контур с 3+ точками.", parent=self)
            return
        lines = ["contours: const ["]
        for contour in contours:
            lines.append("  [")
            for x, y in contour:
                lines.append(f"    Offset({x:.4f}, {y:.4f}),")
            lines.append("  ],")
        lines.append("],")
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status.set("Контуры скопированы.")

    def copy_verse(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Копирование", "Нужен хотя бы один контур с 3+ точками.", parent=self)
            return
        try:
            indexes = parse_indexes(self.word_indexes.get())
        except Exception as exc:
            messagebox.showerror("Индексы", str(exc), parent=self)
            return
        label = self.label_position or contours[0][0]
        lines = [
            "Verse(",
            f"  chapterNumber: {self.chapter.get()},",
            f"  verseNumber: {self.verse.get()},",
            f"  labelPosition: Offset({label[0]:.4f}, {label[1]:.4f}),",
            "  wordIndexes: [",
        ]
        for index in indexes:
            lines.append(f"    {index},")
        lines.extend(["  ],", "  contours: const ["])
        for contour in contours:
            lines.append("    [")
            for x, y in contour:
                lines.append(f"      Offset({x:.4f}, {y:.4f}),")
            lines.append("    ],")
        lines.extend(["  ],", "),"])
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status.set("Стих скопирован.")

    def save_to_db(self) -> None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Сохранение", "Нужен хотя бы один контур с 3+ точками.", parent=self)
            return
        try:
            word_indexes = parse_indexes(self.word_indexes.get())
        except Exception as exc:
            messagebox.showerror("Индексы", str(exc), parent=self)
            return
        label = self.label_position or contours[0][0]
        payload = {
            "verse_index": str(int(self.verse_index_var.get())),
            "chapter_number": str(int(self.chapter.get())),
            "verse_number": str(int(self.verse.get())),
            "label_x": f"{label[0]:.4f}",
            "label_y": f"{label[1]:.4f}",
            "word_indexes_json": json.dumps(word_indexes, ensure_ascii=False),
            "contours_json": json.dumps(contours, ensure_ascii=False),
        }
        if self.on_save(payload, self.previous_verse_index):
            self.previous_verse_index = int(self.verse_index_var.get())
            self.status.set(f"Сохранено в БД: индекс={self.previous_verse_index} для {self.source_id}/{self.page_name}")

    def _mode_label(self) -> str:
        return {
            "add": "доб.",
            "move": "сдв.",
            "delete": "удал.",
        }.get(self.mode.get(), self.mode.get())

    def _install_tooltips(self, items: list[tuple[tk.Widget, str]]) -> None:
        self._tooltips = [_ToolTip(widget, text) for widget, text in items]


