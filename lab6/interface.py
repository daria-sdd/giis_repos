import tkinter as tk
from tkinter import messagebox
from logic import (is_convex, internal_normals, convex_hull, convex_hull_jarvis,
                   line_polygon_intersections, point_in_polygon)

class PolygonEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №5-6. Редактор полигонов и заливка")
        self.geometry("900x600")
        # Список вершин многоугольника (каждая вершина – (x, y))
        self.vertices = []
        self.is_closed = False
        # Выбор метода построения выпуклой оболочки ("graham" или "jarvis")
        self.hull_method_var = tk.StringVar(value="graham")
        # Выбор метода заливки: "ordered", "active", "seed", "scanline"
        self.fill_method_var = tk.StringVar(value="ordered")
        # Флаги для режимов рисования
        self.line_drawing_mode = False  # режим рисования линии
        self.point_mode = False         # режим проверки принадлежности точки
        self.line_points = []           # для линии – два конца
        self.test_point = None
        self.create_widgets()

    def create_widgets(self):
        # Левый фрейм для кнопок и переключателей
        self.btn_frame = tk.Frame(self, width=200, padx=5, pady=5, bg="lightgrey")
        self.btn_frame.pack(side=tk.LEFT, fill=tk.Y)

        btn_clear = tk.Button(self.btn_frame, text="Очистить", command=self.clear_canvas, width=20)
        btn_close = tk.Button(self.btn_frame, text="Замкнуть многоугольник", command=self.close_polygon, width=20)
        btn_check = tk.Button(self.btn_frame, text="Проверить выпуклость", command=self.check_convexity, width=20)
        btn_normals = tk.Button(self.btn_frame, text="Показать нормали", command=self.show_normals, width=20)
        btn_hull = tk.Button(self.btn_frame, text="Выпуклая оболочка", command=self.draw_convex_hull, width=20)
        btn_start_line = tk.Button(self.btn_frame, text="Начать рисование линии", command=self.start_line_drawing, width=20)
        btn_line_intersections = tk.Button(self.btn_frame, text="Найти пересечения линии", command=self.find_line_intersections, width=20)
        btn_point_membership = tk.Button(self.btn_frame, text="Определить принадлежность точки", command=self.start_point_membership, width=20)
        btn_fill = tk.Button(self.btn_frame, text="Заполнить многоугольник", command=self.fill_polygon, width=20)
        btn_debug_fill = tk.Button(self.btn_frame, text="Отладка заливки", command=self.debug_fill, width=20)

        btn_clear.pack(pady=5)
        btn_close.pack(pady=5)
        btn_check.pack(pady=5)
        btn_normals.pack(pady=5)
        btn_hull.pack(pady=5)
        btn_start_line.pack(pady=5)
        btn_line_intersections.pack(pady=5)
        btn_point_membership.pack(pady=5)
        btn_fill.pack(pady=5)
        btn_debug_fill.pack(pady=5)

        # Радиокнопки для выбора метода построения выпуклой оболочки
        hull_frame = tk.Frame(self.btn_frame, bg="lightgrey")
        hull_frame.pack(pady=10, fill=tk.X)
        lbl_hull = tk.Label(hull_frame, text="Метод оболочки:", bg="lightgrey")
        lbl_hull.pack(anchor="w")
        rb_graham = tk.Radiobutton(hull_frame, text="Грэхема", variable=self.hull_method_var,
                                   value="graham", bg="lightgrey")
        rb_jarvis = tk.Radiobutton(hull_frame, text="Джарвиса", variable=self.hull_method_var,
                                   value="jarvis", bg="lightgrey")
        rb_graham.pack(anchor="w")
        rb_jarvis.pack(anchor="w")

        # Радиокнопки для выбора метода заливки
        fill_frame = tk.Frame(self.btn_frame, bg="lightgrey")
        fill_frame.pack(pady=10, fill=tk.X)
        lbl_fill = tk.Label(fill_frame, text="Метод заливки:", bg="lightgrey")
        lbl_fill.pack(anchor="w")
        rb_ordered = tk.Radiobutton(fill_frame, text="Растровая (упоряд. список ребер)",
                                    variable=self.fill_method_var, value="ordered", bg="lightgrey", wraplength=180, justify="left")
        rb_active = tk.Radiobutton(fill_frame, text="Растровая (актив. список ребер)",
                                   variable=self.fill_method_var, value="active", bg="lightgrey", wraplength=180, justify="left")
        rb_seed = tk.Radiobutton(fill_frame, text="Простая заливка с затравкой",
                                 variable=self.fill_method_var, value="seed", bg="lightgrey", wraplength=180, justify="left")
        rb_scanline = tk.Radiobutton(fill_frame, text="Построчная заливка с затравкой",
                                     variable=self.fill_method_var, value="scanline", bg="lightgrey", wraplength=180, justify="left")
        rb_ordered.pack(anchor="w")
        rb_active.pack(anchor="w")
        rb_seed.pack(anchor="w")
        rb_scanline.pack(anchor="w")

        # Рабочая область – холст
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)

    def canvas_click(self, event):
        x, y = event.x, event.y
        if not self.is_closed:
            # Режим добавления вершин многоугольника
            self.vertices.append((x, y))
            r = 3
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")
            if len(self.vertices) > 1:
                x0, y0 = self.vertices[-2]
                self.canvas.create_line(x0, y0, x, y, fill="blue", width=2)
        elif self.line_drawing_mode:
            # Режим рисования линии
            self.line_points.append((x, y))
            r = 3
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="orange", tags="line")
            if len(self.line_points) == 2:
                p1, p2 = self.line_points
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                        fill="orange", width=2, dash=(4,2), tags="line")
                self.line_drawing_mode = False
        elif self.point_mode:
            # Режим определения принадлежности точки
            self.test_point = (x, y)
            inside = point_in_polygon(self.test_point, self.vertices)
            color = "green" if inside else "red"
            messagebox.showinfo("Результат", "Точка принадлежит многоугольнику." if inside else "Точка не принадлежит многоугольнику.")
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill=color, outline=color, tags="test_point")
            self.point_mode = False

    def close_polygon(self):
        if len(self.vertices) < 3:
            messagebox.showerror("Ошибка", "Для замыкания многоугольника нужно минимум 3 вершины!")
            return
        x0, y0 = self.vertices[-1]
        x1, y1 = self.vertices[0]
        self.canvas.create_line(x0, y0, x1, y1, fill="blue", width=2)
        self.is_closed = True

    def clear_canvas(self):
        self.canvas.delete("all")
        self.vertices = []
        self.is_closed = False
        self.line_points = []
        self.line_drawing_mode = False
        self.point_mode = False

    def check_convexity(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        if is_convex(self.vertices):
            messagebox.showinfo("Проверка выпуклости", "Многоугольник выпуклый.")
        else:
            messagebox.showinfo("Проверка выпуклости", "Многоугольник невыпуклый.")

    def show_normals(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        normals = internal_normals(self.vertices)
        n = len(self.vertices)
        scale = 30
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i+1)%n]
            mid = ((x1+x2)/2, (y1+y2)/2)
            nx, ny = normals[i]
            x_end = mid[0] + nx * scale
            y_end = mid[1] + ny * scale
            self.canvas.create_line(mid[0], mid[1], x_end, y_end,
                                    fill="red", width=2, arrow=tk.LAST)

    def draw_convex_hull(self):
        if not self.vertices:
            messagebox.showerror("Ошибка", "Нет точек для построения оболочки!")
            return
        method = self.hull_method_var.get()
        if method == "graham":
            hull = convex_hull(self.vertices)
        else:
            hull = convex_hull_jarvis(self.vertices)
        if len(hull) < 3:
            messagebox.showinfo("Выпуклая оболочка", "Недостаточно точек для построения оболочки.")
            return
        coords = []
        for (x, y) in hull:
            coords.extend([x, y])
        self.canvas.create_polygon(coords, outline="green", fill="", width=2)

    def start_line_drawing(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        self.line_drawing_mode = True
        self.line_points = []
        self.canvas.delete("line")
        messagebox.showinfo("Рисование линии", "Нажмите два раза на холсте для задания концов линии.")

    def find_line_intersections(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        if len(self.line_points) != 2:
            messagebox.showerror("Ошибка", "Сначала нарисуйте линию (два клика)!")
            return
        self.canvas.delete("intersection")
        intersections = line_polygon_intersections(tuple(self.line_points), self.vertices)
        for pt in intersections:
            x, y = pt
            r = 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="purple", tags="intersection")
        if intersections:
            messagebox.showinfo("Пересечения линии", f"Найдено {len(intersections)} пересечение(ий).")
        else:
            messagebox.showinfo("Пересечения линии", "Пересечений не найдено.")

    def start_point_membership(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        self.point_mode = True
        messagebox.showinfo("Определение точки", "Нажмите на холсте, чтобы выбрать точку для проверки.")

    def fill_polygon(self):
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        method = self.fill_method_var.get()
        if method == "ordered":
            from logic import fill_polygon_ordered_edge_list
            fill_polygon_ordered_edge_list(self.vertices, self.canvas, fill_color="yellow")
        elif method == "active":
            from logic import fill_polygon_active_edge_list
            fill_polygon_active_edge_list(self.vertices, self.canvas, fill_color="cyan")
        elif method == "seed":
            from logic import simple_seed_fill
            cx = sum(x for x, y in self.vertices) / len(self.vertices)
            cy = sum(y for x, y in self.vertices) / len(self.vertices)
            simple_seed_fill(self.vertices, self.canvas, (cx, cy), fill_color="magenta")
        elif method == "scanline":
            from logic import scanline_seed_fill
            cx = sum(x for x,y in self.vertices) / len(self.vertices)
            cy = sum(y for x,y in self.vertices) / len(self.vertices)
            scanline_seed_fill(self.vertices, self.canvas, (cx, cy), fill_color="orange")

    def debug_fill(self):
        """
        Отладка заливки: пошаговое отображение процесса заполнения,
        подстраивающееся под выбранный метод заливки.
        """
        if not self.is_closed:
            messagebox.showerror("Ошибка", "Сначала замкните многоугольник!")
            return
        from logic import (debug_fill_ordered_edge_list, debug_fill_active_edge_list,
                           debug_seed_fill, debug_scanline_seed_fill)
        cx = sum(x for x,y in self.vertices)/len(self.vertices)
        cy = sum(y for x,y in self.vertices)/len(self.vertices)
        method = self.fill_method_var.get()
        if method == "ordered":
            debug_fill_ordered_edge_list(self.vertices, self.canvas, fill_color="yellow", delay=50)
        elif method == "active":
            debug_fill_active_edge_list(self.vertices, self.canvas, fill_color="cyan", delay=50)
        elif method == "seed":
            debug_seed_fill(self.vertices, self.canvas, (cx, cy), fill_color="magenta", delay=50)
        elif method == "scanline":
            debug_scanline_seed_fill(self.vertices, self.canvas, (cx, cy), fill_color="orange", delay=50)

if __name__ == "__main__":
    app = PolygonEditor()
    app.mainloop()
