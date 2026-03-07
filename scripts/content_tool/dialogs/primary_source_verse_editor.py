from __future__ import annotations

from collections import defaultdict, deque
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable

from ..compat import Image, ImageTk
from ..helpers import clamp01
from ..models import Point
from ..widgets import _ToolTip

if TYPE_CHECKING:
    from ..app import TopicContentTool


class PrimarySourceVerseEditorDialog(tk.Toplevel):
    MODE_LABEL_TO_KEY: dict[str, str] = {
        "Рисование": "add",
        "Перемещение": "move",
        "Удаление": "delete",
    }

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
        self.on_save = on_save
        self.previous_verse_index = previous_verse_index

        self.title(f"Редактор стиха - {source_id} / {page_name}")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = max(980, min(1360, screen_w - 120))
        window_h = max(700, min(900, screen_h - 140))
        pos_x = max(0, (screen_w - window_w) // 2)
        pos_y = max(0, (screen_h - window_h) // 2)
        self.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
        self.minsize(960, 660)
        self.transient(parent)
        self.grab_set()

        self.mode_label_var = tk.StringVar(value="Рисование")
        self.snap_axis = tk.BooleanVar(value=True)
        self.verse_index_var = tk.IntVar(value=int(initial_payload.get("verse_index") or 0))
        self.chapter_var = tk.IntVar(value=int(initial_payload.get("chapter_number") or 1))
        self.verse_var = tk.IntVar(value=int(initial_payload.get("verse_number") or 1))
        self.selected_word_indexes = self._normalize_word_indexes(initial_payload.get("word_indexes"))
        self.word_indexes_caption_var = tk.StringVar(value=self._word_indexes_caption())

        self.status_left_var = tk.StringVar(value="")
        self.status_right_var = tk.StringVar(value="")
        self.status_note = "Размечайте контуры стиха."
        self.last_pointer_rel: Point | None = None
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

        self.contours = self._normalize_contours(initial_payload.get("contours"))
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

        self._build_ui()
        self._bind_events()
        self.load_image(image_path)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _normalize_word_indexes(self, raw: object) -> list[int]:
        if not isinstance(raw, list):
            return []
        values: list[int] = []
        for item in raw:
            try:
                value = int(item)
            except (TypeError, ValueError):
                continue
            if value >= 0:
                values.append(value)
        return sorted(set(values))

    def _normalize_contours(self, raw: object) -> list[list[Point]]:
        source = raw if isinstance(raw, list) else []
        contours: list[list[Point]] = []
        for contour in source:
            if not isinstance(contour, list):
                continue
            points: list[Point] = []
            for point in contour:
                if not isinstance(point, (list, tuple)) or len(point) != 2:
                    continue
                points.append((clamp01(float(point[0])), clamp01(float(point[1]))))
            if points:
                contours.append(points)
        return contours

    def _mode_key(self) -> str:
        return self.MODE_LABEL_TO_KEY.get(self.mode_label_var.get(), "add")

    def _format_indexes_ranges(self, indexes: list[int]) -> str:
        if not indexes:
            return ""
        sorted_indexes = sorted(set(indexes))
        ranges: list[str] = []
        start = sorted_indexes[0]
        end = start
        for value in sorted_indexes[1:]:
            if value == end + 1:
                end = value
                continue
            if end - start >= 2:
                ranges.append(f"{start}-{end}")
            elif end == start + 1:
                ranges.append(str(start))
                ranges.append(str(end))
            else:
                ranges.append(str(start))
            start = value
            end = value
        if end - start >= 2:
            ranges.append(f"{start}-{end}")
        elif end == start + 1:
            ranges.append(str(start))
            ranges.append(str(end))
        else:
            ranges.append(str(start))
        return ",".join(ranges)

    def _word_indexes_caption(self) -> str:
        packed = self._format_indexes_ranges(self.selected_word_indexes)
        return f"Слова: [{packed}]"

    def _label_status_text(self) -> str:
        if self.label_position is None:
            return "Метка: -"
        return f"Метка: ({self.label_position[0]:.4f}, {self.label_position[1]:.4f})"

    def _contours_status_text(self) -> str:
        if not self.contours:
            return "Контуры: [-]"
        summary = ", ".join(f"{index + 1}:{len(contour)}" for index, contour in enumerate(self.contours))
        return f"Контуры: [{summary}] | активный: {self.active_contour + 1}"

    def _render_status(self) -> None:
        left_parts = [f"Масштаб={self.zoom:.2f}x"]
        if self.last_pointer_rel is not None:
            left_parts.append(f"Точка=({self.last_pointer_rel[0]:.4f}, {self.last_pointer_rel[1]:.4f})")
        elif self.pointer_outside:
            left_parts.append("вне изображения")
        self.status_left_var.set("  ".join(left_parts))

        right_parts = [self._contours_status_text(), self._label_status_text()]
        if self.status_note:
            right_parts.insert(0, self.status_note)
        self.status_right_var.set("  ".join(right_parts))

    def _set_status_note(self, note: str) -> None:
        self.status_note = note
        self._render_status()

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

        btn_save_new = ttk.Button(controls, text="Сохранить + новый стих", command=self.save_to_db_and_prepare_new)
        btn_save_new.grid(row=0, column=1, padx=(2, 2))

        btn_new = ttk.Button(controls, text="Новый контур", command=self.new_contour)
        btn_new.grid(row=0, column=2, padx=(8, 2))

        btn_delete = ttk.Button(controls, text="Удалить контур", command=self.delete_contour)
        btn_delete.grid(row=0, column=3, padx=2)

        btn_label = ttk.Button(controls, text="Метка", command=self.pick_label)
        btn_label.grid(row=0, column=4, padx=(8, 2))

        check_snap_axis = ttk.Checkbutton(controls, text="Ось", variable=self.snap_axis)
        check_snap_axis.grid(row=0, column=5, padx=(8, 6))

        ttk.Label(controls, text="Режим:").grid(row=0, column=6, padx=(0, 4))
        self.mode_combo = ttk.Combobox(
            controls,
            textvariable=self.mode_label_var,
            values=list(self.MODE_LABEL_TO_KEY.keys()),
            state="readonly",
            width=14,
        )
        self.mode_combo.grid(row=0, column=7, padx=(0, 2))
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        meta = ttk.Frame(self, padding=(8, 0, 8, 6))
        meta.grid(row=1, column=0, sticky="ew")
        meta.columnconfigure(8, weight=1)

        ttk.Label(meta, text="Индекс").grid(row=0, column=0, padx=(0, 4))
        ttk.Spinbox(meta, from_=0, to=99999, textvariable=self.verse_index_var, width=7).grid(row=0, column=1)

        ttk.Label(meta, text="Гл.").grid(row=0, column=2, padx=(8, 4))
        ttk.Spinbox(meta, from_=1, to=999, textvariable=self.chapter_var, width=5).grid(row=0, column=3)

        ttk.Label(meta, text="Стих").grid(row=0, column=4, padx=(8, 4))
        ttk.Spinbox(meta, from_=1, to=9999, textvariable=self.verse_var, width=6).grid(row=0, column=5)

        self.word_indexes_button = ttk.Button(
            meta,
            textvariable=self.word_indexes_caption_var,
            command=self.edit_word_indexes,
            width=36,
        )
        self.word_indexes_button.grid(row=0, column=6, padx=(8, 0), sticky="w")

        self.btn_draft_contour = ttk.Button(
            meta,
            text="Черновой контур",
            command=self.generate_draft_contour,
        )
        self.btn_draft_contour.grid(row=0, column=7, padx=(8, 0), sticky="w")

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
                (btn_save_close, "Сохранить стих в БД и закрыть окно."),
                (btn_save_new, "Сохранить текущий стих и подготовить форму для следующего."),
                (btn_new, "Создать новый контур стиха."),
                (btn_delete, "Удалить активный контур."),
                (btn_label, "Указать позицию метки стиха на изображении."),
                (check_snap_axis, "Выравнивать новую точку по оси X или Y."),
                (self.mode_combo, "Режим работы: рисование, перемещение или удаление точек."),
                (self.word_indexes_button, "Выбрать слова, которые относятся к этому стиху."),
                (self.btn_draft_contour, "Построить общий черновой контур по прямоугольникам выбранных слов."),
            ]
        )

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", lambda _event: self.redraw())
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda _event: setattr(self, "drag_point", None))
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_drag)
        self.canvas.bind("<ButtonRelease-3>", lambda _event: setattr(self, "panning", False))
        self.canvas.bind("<MouseWheel>", self.on_wheel_win)
        self.canvas.bind("<Button-4>", self.on_wheel_linux)
        self.canvas.bind("<Button-5>", self.on_wheel_linux)
        self.canvas.bind("<Motion>", self.on_motion)
        self.bind("<Control-s>", lambda _event: self.save_to_db_close())

    def _on_mode_changed(self, _event: object | None = None) -> None:
        self.redraw()

    def edit_word_indexes(self) -> None:
        rows = []
        for row in getattr(self.parent_tool, "primary_source_word_rows", []):
            try:
                idx = int(row["word_index"] or 0)
            except (TypeError, ValueError, KeyError):
                continue
            rows.append((idx, str(row["text"] or "").strip()))
        rows.sort(key=lambda item: item[0])

        if not rows:
            messagebox.showinfo("Нет слов", "Для страницы пока нет слов.", parent=self)
            return

        selected = set(self.selected_word_indexes)

        dialog = tk.Toplevel(self)
        dialog.title("Слова стиха")
        dialog.transient(self)
        dialog.grab_set()
        dialog.minsize(380, 320)

        root = ttk.Frame(dialog, padding=10)
        root.grid(row=0, column=0, sticky="nsew")
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        list_host = ttk.Frame(root)
        list_host.grid(row=0, column=0, sticky="nsew")
        list_host.columnconfigure(0, weight=1)
        list_host.rowconfigure(0, weight=1)

        canvas = tk.Canvas(list_host, highlightthickness=0, height=420)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_host, orient="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)

        rows_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        rows_frame.columnconfigure(0, weight=1)

        flags: list[tuple[int, tk.BooleanVar]] = []
        for row_idx, (word_index, text) in enumerate(rows):
            caption = text if text else "-"
            var = tk.BooleanVar(value=word_index in selected)
            flags.append((word_index, var))
            ttk.Checkbutton(
                rows_frame,
                text=f"{word_index}: {caption}",
                variable=var,
            ).grid(row=row_idx, column=0, sticky="w", pady=2)

        def _refresh_scroll_region(_event: object | None = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        rows_frame.bind("<Configure>", _refresh_scroll_region)
        _refresh_scroll_region()

        actions = ttk.Frame(root)
        actions.grid(row=1, column=0, sticky="e", pady=(8, 0))

        def _apply() -> None:
            self.selected_word_indexes = sorted(index for index, flag in flags if flag.get())
            self.word_indexes_caption_var.set(self._word_indexes_caption())
            self._set_status_note("Список слов обновлен.")
            dialog.destroy()

        ttk.Button(actions, text="OK", command=_apply).pack(side="left")
        ttk.Button(actions, text="Отмена", command=dialog.destroy).pack(side="left", padx=(8, 0))
        dialog.bind("<Escape>", lambda _event: dialog.destroy())
        dialog.wait_window()

    def _parse_rectangles_payload(self, raw: object) -> list[tuple[float, float, float, float]]:
        if isinstance(raw, list):
            payload = raw
        else:
            try:
                payload = json.loads(str(raw or "[]"))
            except json.JSONDecodeError:
                payload = []
        if not isinstance(payload, list):
            return []

        rectangles: list[tuple[float, float, float, float]] = []
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
            rectangles.append((left, top, right, bottom))
        return rectangles

    def _rectangles_for_selected_words(self) -> list[tuple[float, float, float, float]]:
        selected = set(self.selected_word_indexes)
        if not selected:
            return []
        rectangles: list[tuple[float, float, float, float]] = []
        for row in getattr(self.parent_tool, "primary_source_word_rows", []):
            try:
                word_index = int(row["word_index"] or 0)
            except (TypeError, ValueError, KeyError):
                continue
            if word_index not in selected:
                continue
            try:
                raw_rectangles = row["rectangles_json"]
            except (KeyError, TypeError):
                raw_rectangles = "[]"
            rectangles.extend(self._parse_rectangles_payload(raw_rectangles))
        return rectangles

    def _rectangles_for_page_words(self) -> list[tuple[float, float, float, float]]:
        rectangles: list[tuple[float, float, float, float]] = []
        for row in getattr(self.parent_tool, "primary_source_word_rows", []):
            try:
                raw_rectangles = row["rectangles_json"]
            except (KeyError, TypeError):
                raw_rectangles = "[]"
            rectangles.extend(self._parse_rectangles_payload(raw_rectangles))
        return rectangles

    def _snap_value_to_guides(self, value: float, guides: list[float], tolerance: float) -> float:
        if not guides:
            return value
        nearest = min(guides, key=lambda guide: abs(guide - value))
        return nearest if abs(nearest - value) <= tolerance else value

    def _snap_rectangles_to_guides(
        self,
        rectangles: list[tuple[float, float, float, float]],
        guide_rectangles: list[tuple[float, float, float, float]],
    ) -> list[tuple[float, float, float, float]]:
        if not rectangles:
            return []
        x_guides = sorted({edge for rect in guide_rectangles for edge in (rect[0], rect[2])})
        y_guides = sorted({edge for rect in guide_rectangles for edge in (rect[1], rect[3])})
        widths = [rect[2] - rect[0] for rect in rectangles]
        heights = [rect[3] - rect[1] for rect in rectangles]
        base_size = min(widths + heights) if widths and heights else 0.01
        tolerance = max(0.002, min(0.012, base_size * 0.25))

        snapped: list[tuple[float, float, float, float]] = []
        for rect in rectangles:
            x1, y1, x2, y2 = rect
            sx1 = self._snap_value_to_guides(x1, x_guides, tolerance)
            sx2 = self._snap_value_to_guides(x2, x_guides, tolerance)
            sy1 = self._snap_value_to_guides(y1, y_guides, tolerance)
            sy2 = self._snap_value_to_guides(y2, y_guides, tolerance)
            left, right = sorted((sx1, sx2))
            top, bottom = sorted((sy1, sy2))
            if right - left < 1e-6 or bottom - top < 1e-6:
                left, top, right, bottom = rect
            snapped.append((left, top, right, bottom))
        return snapped

    def _build_grid_union(
        self,
        rectangles: list[tuple[float, float, float, float]],
    ) -> tuple[list[float], list[float], set[tuple[int, int]]]:
        x_coords = sorted({edge for rect in rectangles for edge in (rect[0], rect[2])})
        y_coords = sorted({edge for rect in rectangles for edge in (rect[1], rect[3])})
        if len(x_coords) < 2 or len(y_coords) < 2:
            return x_coords, y_coords, set()

        x_index = {value: idx for idx, value in enumerate(x_coords)}
        y_index = {value: idx for idx, value in enumerate(y_coords)}
        filled: set[tuple[int, int]] = set()

        for x1, y1, x2, y2 in rectangles:
            i1, i2 = x_index[x1], x_index[x2]
            j1, j2 = y_index[y1], y_index[y2]
            for cell_x in range(i1, i2):
                for cell_y in range(j1, j2):
                    filled.add((cell_x, cell_y))
        return x_coords, y_coords, filled

    def _connected_components(self, cells: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
        components: list[set[tuple[int, int]]] = []
        pending = set(cells)
        while pending:
            seed = pending.pop()
            component = {seed}
            queue: deque[tuple[int, int]] = deque([seed])
            while queue:
                x_cell, y_cell = queue.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    neighbor = (x_cell + dx, y_cell + dy)
                    if neighbor not in pending:
                        continue
                    pending.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
            components.append(component)
        return components

    def _connect_components_with_corridors(self, cells: set[tuple[int, int]]) -> set[tuple[int, int]]:
        filled = set(cells)
        safety = 0
        while True:
            components = self._connected_components(filled)
            if len(components) <= 1:
                return filled
            if safety > 64:
                return filled
            safety += 1

            best_pair: tuple[tuple[int, int], tuple[int, int]] | None = None
            best_distance: int | None = None
            for left_idx in range(len(components)):
                for right_idx in range(left_idx + 1, len(components)):
                    for source in components[left_idx]:
                        for target in components[right_idx]:
                            distance = abs(source[0] - target[0]) + abs(source[1] - target[1])
                            if best_distance is None or distance < best_distance:
                                best_distance = distance
                                best_pair = (source, target)

            if best_pair is None:
                return filled

            (sx, sy), (tx, ty) = best_pair
            cx, cy = sx, sy
            filled.add((cx, cy))
            while cx != tx:
                cx += 1 if tx > cx else -1
                filled.add((cx, cy))
            while cy != ty:
                cy += 1 if ty > cy else -1
                filled.add((cx, cy))

    def _trace_largest_loop(
        self,
        x_coords: list[float],
        y_coords: list[float],
        cells: set[tuple[int, int]],
    ) -> list[Point]:
        if not cells:
            return []

        directed_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for cell_x, cell_y in cells:
            if (cell_x, cell_y - 1) not in cells:
                directed_edges.append(((cell_x, cell_y), (cell_x + 1, cell_y)))
            if (cell_x + 1, cell_y) not in cells:
                directed_edges.append(((cell_x + 1, cell_y), (cell_x + 1, cell_y + 1)))
            if (cell_x, cell_y + 1) not in cells:
                directed_edges.append(((cell_x + 1, cell_y + 1), (cell_x, cell_y + 1)))
            if (cell_x - 1, cell_y) not in cells:
                directed_edges.append(((cell_x, cell_y + 1), (cell_x, cell_y)))

        outgoing: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
        for start, end in directed_edges:
            outgoing[start].append(end)

        loops: list[list[tuple[int, int]]] = []
        while outgoing:
            start = min(outgoing.keys(), key=lambda item: (item[1], item[0]))
            next_points = outgoing[start]
            current = next_points.pop()
            if not next_points:
                del outgoing[start]
            loop = [start]
            guard = 0
            while guard < 20000:
                guard += 1
                loop.append(current)
                if current == start:
                    break
                current_next = outgoing.get(current)
                if not current_next:
                    break
                nxt = current_next.pop()
                if not current_next:
                    del outgoing[current]
                current = nxt
            if len(loop) >= 4 and loop[-1] == loop[0]:
                loops.append(loop[:-1])

        if not loops:
            return []

        best_loop = max(
            loops,
            key=lambda loop: self._polygon_area([(x_coords[x], y_coords[y]) for x, y in loop]),
        )
        points = [(x_coords[x], y_coords[y]) for x, y in best_loop]
        return self._simplify_orthogonal_points(points)

    def _simplify_orthogonal_points(self, points: list[Point]) -> list[Point]:
        if len(points) < 3:
            return points
        cleaned = points[:]
        changed = True
        while changed and len(cleaned) >= 3:
            changed = False
            simplified: list[Point] = []
            length = len(cleaned)
            for idx in range(length):
                prev_pt = cleaned[(idx - 1) % length]
                cur_pt = cleaned[idx]
                next_pt = cleaned[(idx + 1) % length]
                vertical = abs(prev_pt[0] - cur_pt[0]) < 1e-9 and abs(cur_pt[0] - next_pt[0]) < 1e-9
                horizontal = abs(prev_pt[1] - cur_pt[1]) < 1e-9 and abs(cur_pt[1] - next_pt[1]) < 1e-9
                if vertical or horizontal:
                    changed = True
                    continue
                simplified.append(cur_pt)
            if not simplified:
                break
            cleaned = simplified
        return cleaned

    def _polygon_area(self, points: list[Point]) -> float:
        if len(points) < 3:
            return 0.0
        area = 0.0
        for idx, point in enumerate(points):
            next_point = points[(idx + 1) % len(points)]
            area += point[0] * next_point[1] - next_point[0] * point[1]
        return abs(area) * 0.5

    def generate_draft_contour(self) -> None:
        selected_rectangles = self._rectangles_for_selected_words()
        if not selected_rectangles:
            messagebox.showinfo("Нет данных", "Выберите слова с прямоугольниками для построения.", parent=self)
            return

        guide_rectangles = self._rectangles_for_page_words() or selected_rectangles
        snapped = self._snap_rectangles_to_guides(selected_rectangles, guide_rectangles)
        x_coords, y_coords, cells = self._build_grid_union(snapped)
        if not cells:
            messagebox.showwarning("Черновой контур", "Не удалось построить черновой контур.", parent=self)
            return

        connected_cells = self._connect_components_with_corridors(cells)
        draft_points = self._trace_largest_loop(x_coords, y_coords, connected_cells)
        if len(draft_points) < 3:
            messagebox.showwarning("Черновой контур", "Контур получился слишком маленьким.", parent=self)
            return

        if not self.contours:
            self.contours = [draft_points]
            self.active_contour = 0
        else:
            self.active_contour = max(0, min(self.active_contour, len(self.contours) - 1))
            self.contours[self.active_contour] = draft_points
        if self.label_position is None:
            self.label_position = draft_points[0]
        self._set_status_note(f"Черновой контур построен: точек {len(draft_points)}.")
        self.redraw()

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

    def rel_to_canvas(self, point: Point) -> Point:
        image_width, image_height = self.image_size
        return (self.pan_x + point[0] * image_width * self.zoom, self.pan_y + point[1] * image_height * self.zoom)

    def canvas_to_rel(self, x: float, y: float) -> Point | None:
        if self.image is None:
            return None
        image_width, image_height = self.image_size
        image_x = (x - self.pan_x) / self.zoom
        image_y = (y - self.pan_y) / self.zoom
        if image_x < 0 or image_y < 0 or image_x > image_width or image_y > image_height:
            return None
        return (clamp01(image_x / image_width), clamp01(image_y / image_height))

    def nearest_point(self, x: float, y: float) -> tuple[int, int] | None:
        best: tuple[int, int] | None = None
        best_d2 = 12 * 12
        for contour_index, contour in enumerate(self.contours):
            for point_index, point in enumerate(contour):
                px, py = self.rel_to_canvas(point)
                d2 = (px - x) ** 2 + (py - y) ** 2
                if d2 <= best_d2:
                    best, best_d2 = (contour_index, point_index), d2
        return best

    def on_left_down(self, event: tk.Event[tk.Misc]) -> None:
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return

        if self.wait_label_pick:
            self.wait_label_pick = False
            self.label_position = rel
            self._set_status_note("Метка стиха обновлена.")
            self.redraw()
            return

        mode = self._mode_key()
        if mode == "add":
            contour = self.contours[self.active_contour]
            if contour and self.snap_axis.get():
                px, py = contour[-1]
                dx, dy = abs(rel[0] - px), abs(rel[1] - py)
                rel = (px, rel[1]) if dx < dy else (rel[0], py)
            contour.append(rel)
            self.redraw()
            return

        near = self.nearest_point(event.x, event.y)
        if near is None:
            return
        contour_index, point_index = near
        if mode == "move":
            self.active_contour = contour_index
            self.drag_point = (contour_index, point_index)
            self.redraw()
            return
        if mode == "delete":
            self.contours[contour_index].pop(point_index)
            self.active_contour = contour_index
            self.redraw()

    def on_left_drag(self, event: tk.Event[tk.Misc]) -> None:
        if self.drag_point is None:
            return
        rel = self.canvas_to_rel(event.x, event.y)
        if rel is None:
            return
        contour_index, point_index = self.drag_point
        self.contours[contour_index][point_index] = rel
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
            self.last_pointer_rel = None
            self.pointer_outside = True
        else:
            self.last_pointer_rel = rel
            self.pointer_outside = False
        self._render_status()

    def new_contour(self) -> None:
        self.contours.append([])
        self.active_contour = len(self.contours) - 1
        self._set_status_note("Добавлен новый контур.")
        self.redraw()

    def delete_contour(self) -> None:
        if len(self.contours) <= 1:
            self.contours[0].clear()
            self.active_contour = 0
        else:
            self.contours.pop(self.active_contour)
            self.active_contour = max(0, self.active_contour - 1)
        self._set_status_note("Контур удален.")
        self.redraw()

    def pick_label(self) -> None:
        self.wait_label_pick = True
        self._set_status_note("Щелкните по изображению, чтобы поставить метку.")

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

        for contour_index, contour in enumerate(self.contours):
            if len(contour) < 1:
                continue
            color = "#00a06f" if contour_index == self.active_contour else "#0b8561"
            points = [self.rel_to_canvas(point) for point in contour]
            if len(points) >= 2:
                flat = [xy for point in points for xy in point]
                self.canvas.create_line(*flat, fill=color, width=3 if contour_index == self.active_contour else 2)
                if len(points) >= 3 and contour[0] != contour[-1]:
                    self.canvas.create_line(*points[-1], *points[0], fill=color, width=2, dash=(4, 4))
            for point_index, (x, y) in enumerate(points):
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

        if self.label_position is not None:
            lx, ly = self.rel_to_canvas(self.label_position)
            self.canvas.create_rectangle(lx - 5, ly - 5, lx + 5, ly + 5, outline="#ffe066", width=2)
            self.canvas.create_text(
                lx + 9,
                ly,
                text=f"{self.chapter_var.get()}:{self.verse_var.get()}",
                fill="#ffe066",
                anchor="w",
                font=("Segoe UI", 11, "bold"),
            )

        self._render_status()

    def filtered_contours(self) -> list[list[Point]]:
        result: list[list[Point]] = []
        for contour in self.contours:
            points = contour[:-1] if len(contour) >= 2 and contour[0] == contour[-1] else contour
            if len(points) >= 3:
                result.append(points)
        return result

    def _build_payload(self) -> dict[str, object] | None:
        contours = self.filtered_contours()
        if not contours:
            messagebox.showwarning("Сохранение", "Нужен хотя бы один контур с 3+ точками.", parent=self)
            return None

        label = self.label_position or contours[0][0]
        return {
            "verse_index": str(int(self.verse_index_var.get())),
            "chapter_number": str(int(self.chapter_var.get())),
            "verse_number": str(int(self.verse_var.get())),
            "label_x": f"{label[0]:.4f}",
            "label_y": f"{label[1]:.4f}",
            "word_indexes_json": json.dumps(self.selected_word_indexes, ensure_ascii=False),
            "contours_json": json.dumps(contours, ensure_ascii=False),
        }

    def _save_payload(self, payload: dict[str, object]) -> bool:
        if not self.on_save(payload, self.previous_verse_index):
            return False
        self.previous_verse_index = int(payload["verse_index"])
        self._set_status_note(
            f"Сохранено в БД: индекс={self.previous_verse_index} для {self.source_id}/{self.page_name}"
        )
        return True

    def _occupied_verse_indexes(self) -> set[int]:
        rows = getattr(self.parent_tool, "primary_source_verse_rows", [])
        occupied: set[int] = set()
        for row in rows:
            try:
                occupied.add(int(row["verse_index"] or 0))
            except (TypeError, ValueError, KeyError):
                continue
        return occupied

    def _next_free_verse_index(self, start: int) -> int:
        occupied = self._occupied_verse_indexes()
        candidate = max(0, int(start))
        while candidate in occupied:
            candidate += 1
        return candidate

    def _reset_editor_for_new_verse(self, *, next_index: int, next_verse_number: int) -> None:
        self.previous_verse_index = None
        self.verse_index_var.set(next_index)
        self.verse_var.set(next_verse_number)
        self.selected_word_indexes = []
        self.word_indexes_caption_var.set(self._word_indexes_caption())
        self.mode_label_var.set("Рисование")
        self.wait_label_pick = False
        self.drag_point = None
        self.label_position = None
        self.contours = [[]]
        self.active_contour = 0
        self._set_status_note(f"Стих сохранен. Подготовлен новый стих, индекс {next_index}.")
        self.redraw()

    def save_to_db_close(self) -> None:
        payload = self._build_payload()
        if payload is None:
            return
        if self._save_payload(payload):
            self.destroy()

    def save_to_db_and_prepare_new(self) -> None:
        payload = self._build_payload()
        if payload is None:
            return
        if not self._save_payload(payload):
            return
        current_index = int(payload["verse_index"])
        current_verse = int(payload["verse_number"])
        next_index = self._next_free_verse_index(current_index + 1)
        self._reset_editor_for_new_verse(next_index=next_index, next_verse_number=current_verse + 1)

    def _install_tooltips(self, items: list[tuple[tk.Widget, str]]) -> None:
        for widget, text in items:
            self._tooltips.append(_ToolTip(widget, text))
