import tkinter as tk
from tkinter import ttk

from first_order_algorithms import (
    compute_dda_points,
    compute_bresenham_points,
    compute_wu_points,
    intensity_to_hex
)
from second_order_algorithms import (
    compute_circle_points,
    compute_ellipse_points,
    compute_hyperbola_points,
    compute_parabola_points
)

# Функция для немедленного рисования точек (без задержки)
def draw_points_immediate(canvas, points):
    for pt in points:
        x, y, brightness = pt
        canvas.create_rectangle(int(x), int(y), int(x) + 1, int(y) + 1,
                                  fill=intensity_to_hex(brightness),
                                  outline=intensity_to_hex(brightness))

class DrawingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Графический редактор")
        self.geometry("1000x600")
        self.line_type = tk.StringVar(value="Линии первого порядка")
        self.debug_mode = tk.BooleanVar(value=False)
        self.debug_delay = tk.IntVar(value=100)  # задержка в мс для отладки

        # Основной контейнер
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель: выбор типа линий
        self.left_frame = ttk.Frame(self.main_frame, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(self.left_frame, text="Тип линий", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(self.left_frame, text="Линии первого порядка",
                   command=lambda: self.select_type("Линии первого порядка")).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(self.left_frame, text="Линии второго порядка",
                   command=lambda: self.select_type("Линии второго порядка")).pack(fill=tk.X, padx=5, pady=5)

        # Центральная панель: холст для рисования
        self.canvas = tk.Canvas(self.main_frame, bg="white", width=600, height=500)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правая панель: алгоритмы, параметры, режим отладки и отладочная таблица
        self.right_frame = ttk.Frame(self.main_frame, width=250)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.algorithm_label = ttk.Label(self.right_frame, text="Алгоритмы", font=("Arial", 12, "bold"))
        self.algorithm_label.pack(pady=5)

        self.algorithm = tk.StringVar()
        self.algorithm_combobox = ttk.Combobox(self.right_frame, textvariable=self.algorithm)
        self.algorithm_combobox.pack(fill=tk.X, padx=5, pady=5)
        self.update_algorithm_options()

        self.debug_check = ttk.Checkbutton(self.right_frame, text="Режим отладки", variable=self.debug_mode)
        self.debug_check.pack(pady=5)

        ttk.Label(self.right_frame, text="Скорость отладки (мс)").pack(pady=(10, 0))
        self.debug_speed_slider = tk.Scale(self.right_frame, from_=10, to=500,
                                           orient=tk.HORIZONTAL, variable=self.debug_delay)
        self.debug_speed_slider.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(self.right_frame, text="Очистить холст", command=self.clear_canvas).pack(fill=tk.X, padx=5, pady=5)

        # Отладочная таблица (Treeview)
        self.debug_tree = ttk.Treeview(self.right_frame, columns=("index", "x", "y", "brightness"),
                                       show="headings", height=10)
        self.debug_tree.heading("index", text="№")
        self.debug_tree.heading("x", text="X")
        self.debug_tree.heading("y", text="Y")
        self.debug_tree.heading("brightness", text="Яркость")
        self.debug_tree.column("index", width=30)
        self.debug_tree.column("x", width=50)
        self.debug_tree.column("y", width=50)
        self.debug_tree.column("brightness", width=70)
        self.debug_tree.pack(fill=tk.BOTH, padx=5, pady=5)

        # Обработка событий мыши на холсте
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Для линий второго порядка запоминаем центр (первый клик)
        self.temp_center = None

    def select_type(self, type_name):
        self.line_type.set(type_name)
        self.update_algorithm_options()

    def update_algorithm_options(self):
        lt = self.line_type.get()
        if lt == "Линии первого порядка":
            self.algorithm_combobox["values"] = ["ЦДА", "Брезенхем", "Ву"]
            self.algorithm_combobox.set("ЦДА")
            self.algorithm_label.config(text="Алгоритмы 1-го порядка")
        else:
            self.algorithm_combobox["values"] = ["Окружность", "Эллипс", "Гипербола", "Парабола"]
            self.algorithm_combobox.set("Окружность")
            self.algorithm_label.config(text="Алгоритмы 2-го порядка")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.clear_debug_table()

    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.line_type.get() == "Линии второго порядка":
            self.temp_center = (event.x, event.y)

    def on_release(self, event):
        end_x = event.x
        end_y = event.y
        lt = self.line_type.get()
        algo = self.algorithm.get()
        debug = self.debug_mode.get()
        if lt == "Линии первого порядка":
            if algo == "ЦДА":
                pts = compute_dda_points(self.start_x, self.start_y, end_x, end_y)
            elif algo == "Брезенхем":
                pts = compute_bresenham_points(self.start_x, self.start_y, end_x, end_y)
            elif algo == "Ву":
                pts = compute_wu_points(self.start_x, self.start_y, end_x, end_y)
            else:
                pts = []
            if debug:
                self.clear_debug_table()
                self.draw_points_debug(pts)
            else:
                draw_points_immediate(self.canvas, pts)
        else:  # Линии второго порядка
            if algo == "Окружность":
                if self.temp_center is None:
                    return
                cx, cy = self.temp_center
                pts = compute_circle_points(cx, cy, end_x, end_y)
            elif algo == "Эллипс":
                if self.temp_center is None:
                    return
                cx, cy = self.temp_center
                pts = compute_ellipse_points(cx, cy, end_x, end_y)
            elif algo == "Гипербола":
                if self.temp_center is None:
                    return
                cx, cy = self.temp_center
                pts = compute_hyperbola_points(cx, cy, end_x, end_y)
            elif algo == "Парабола":
                if self.temp_center is None:
                    return
                cx, cy = self.temp_center
                pts = compute_parabola_points(cx, cy, end_x, end_y)
            else:
                pts = []
            if pts:
                if debug:
                    self.clear_debug_table()
                    self.draw_points_debug(pts)
                else:
                    draw_points_immediate(self.canvas, pts)
            self.temp_center = None

    def clear_debug_table(self):
        for item in self.debug_tree.get_children():
            self.debug_tree.delete(item)

    def draw_points_debug(self, points, index=0):
        if index >= len(points):
            return
        x, y, brightness = points[index]
        self.canvas.create_rectangle(int(x), int(y), int(x)+1, int(y)+1,
                                       fill=intensity_to_hex(brightness),
                                       outline=intensity_to_hex(brightness))
        self.debug_tree.insert("", "end",
                               values=(index, f"{x:.2f}", f"{y:.2f}", f"{brightness:.2f}"))
        delay = self.debug_delay.get()
        self.after(delay, lambda: self.draw_points_debug(points, index+1))
