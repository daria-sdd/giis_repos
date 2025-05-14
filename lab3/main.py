import tkinter as tk
from tkinter import messagebox
from curve_logic import hermite_curve_segments, bezier_curve_segments, bspline_curve_segments

class CurveEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("Редактор точек и кривых")

        # Панель управления справа
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Кнопка переключения режима редактирования
        self.edit_mode = False
        self.edit_btn = tk.Button(self.control_frame,
                                  text="Режим редактирования: Выкл",
                                  command=self.toggle_edit_mode)
        self.edit_btn.pack(pady=5)

        # Кнопка для отладки – замедленное (пошаговое) рисование
        self.slow_draw = False
        self.debug_btn = tk.Button(self.control_frame,
                                   text="Отладка прямой: Выкл",
                                   command=self.toggle_slow_draw)
        self.debug_btn.pack(pady=5)

        # Выбор алгоритма для построения кривых
        tk.Label(self.control_frame, text="Алгоритм:").pack(pady=5)
        self.current_algo = tk.StringVar(value="Hermite")
        tk.Radiobutton(self.control_frame, text="Кривая Эрмита",
                       variable=self.current_algo,
                       value="Hermite", command=self.redraw_curve).pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(self.control_frame, text="Кривая Безье",
                       variable=self.current_algo,
                       value="Bezier", command=self.redraw_curve).pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(self.control_frame, text="Кривая B‑Spline",
                       variable=self.current_algo,
                       value="B-Spline", command=self.redraw_curve).pack(anchor="w", padx=5, pady=2)

        # Кнопка очистки холста
        self.btn_clear = tk.Button(self.control_frame, text="Очистить", width=15, command=self.clear_canvas)
        self.btn_clear.pack(pady=10)

        # Холст для рисования (рабочая область)
        self.canvas = tk.Canvas(master, bg="white", width=600, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Списки для хранения опорных точек и идентификаторов графических объектов
        self.points = []        # список кортежей (x, y)
        self.point_ids = []     # id для овалов (точек)
        self.label_ids = []     # id для текстовых ярлыков (номеров)

        # Данные для перетаскивания точки (drag and drop)
        self.drag_data = {"item": None, "x": 0, "y": 0, "index": None}

        # При клике по холсту – добавляем точку, если не кликаем по объекту с тегом "point"
        self.canvas.bind("<Button-1>", self.add_point)

        # Привязываем события для перетаскивания точек (с тегом "point")
        self.canvas.tag_bind("point", "<ButtonPress-1>", self.on_point_press)
        self.canvas.tag_bind("point", "<B1-Motion>", self.on_point_drag)
        self.canvas.tag_bind("point", "<ButtonRelease-1>", self.on_point_release)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_btn.config(text="Режим редактирования: Вкл")
        else:
            self.edit_btn.config(text="Режим редактирования: Выкл")

    def toggle_slow_draw(self):
        self.slow_draw = not self.slow_draw
        if self.slow_draw:
            self.debug_btn.config(text="Отладка прямой: Вкл")
        else:
            self.debug_btn.config(text="Отладка прямой: Выкл")
        self.redraw_curve()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.points = []
        self.point_ids = []
        self.label_ids = []

    def add_point(self, event):
        if self.edit_mode:
            return  # в режиме редактирования новые точки не ставятся
        current = self.canvas.find_withtag("current")
        if current and "point" in self.canvas.gettags(current[0]):
            return

        x, y = event.x, event.y
        self.points.append((x, y))
        r = 3  # радиус точки
        point_id = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                             fill="black", tags=("point",))
        self.point_ids.append(point_id)
        label_id = self.canvas.create_text(x + 10, y, text=str(len(self.points)),
                                            fill="black", font=("Arial", 10))
        self.label_ids.append(label_id)
        self.redraw_curve()

    def redraw_curve(self):
        self.canvas.delete("curve")
        algo = self.current_algo.get()
        if algo == "Hermite":
            segments = hermite_curve_segments(self.points)
            color = "red"
        elif algo == "Bezier":
            segments = bezier_curve_segments(self.points)
            color = "green"
        elif algo == "B-Spline":
            segments = bspline_curve_segments(self.points)
            color = "blue"
        else:
            segments = []
            color = "black"

        if self.slow_draw:
            self.debug_draw_segments(segments, color=color)
        else:
            for seg in segments:
                self.canvas.create_line(seg[0], seg[1], seg[2], seg[3],
                                        fill=color, width=2, tag="curve")

    def debug_draw_segments(self, segments, color, index=0):
        if index < len(segments):
            seg = segments[index]
            self.canvas.create_line(seg[0], seg[1], seg[2], seg[3],
                                    fill=color, width=2, tag="curve")
            self.master.after(100, lambda: self.debug_draw_segments(segments, color, index+1))

    def on_point_press(self, event):
        if not self.edit_mode:
            return
        item = self.canvas.find_closest(event.x, event.y)[0]
        if "point" not in self.canvas.gettags(item):
            return
        self.drag_data["item"] = item
        if item in self.point_ids:
            self.drag_data["index"] = self.point_ids.index(item)
        coords = self.canvas.coords(item)  # [x1, y1, x2, y2]
        cx = (coords[0] + coords[2]) / 2
        cy = (coords[1] + coords[3]) / 2
        self.drag_data["x"] = event.x - cx
        self.drag_data["y"] = event.y - cy

    def on_point_drag(self, event):
        if not self.edit_mode or self.drag_data["item"] is None:
            return
        item = self.drag_data["item"]
        index = self.drag_data["index"]
        new_x = event.x - self.drag_data["x"]
        new_y = event.y - self.drag_data["y"]
        r = 3
        self.canvas.coords(item, new_x - r, new_y - r, new_x + r, new_y + r)
        label_id = self.label_ids[index]
        self.canvas.coords(label_id, new_x + 10, new_y)
        self.points[index] = (new_x, new_y)
        self.redraw_curve()

    def on_point_release(self, event):
        if not self.edit_mode:
            return
        self.drag_data = {"item": None, "x": 0, "y": 0, "index": None}

if __name__ == "__main__":
    root = tk.Tk()
    app = CurveEditorApp(root)
    root.mainloop()
