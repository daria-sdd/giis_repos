import tkinter as tk
from tkinter import filedialog, messagebox
from transformation_logic import read_model, apply_transformation, project_point, project_point_orthographic


class TransformationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №4. 3D Преобразования для Куба")
        self.geometry("1000x700")

        # Режим проекции (перспектива или ортографическая)
        self.projection_mode = tk.StringVar(value="perspective")

        self.create_widgets()

        # Параметры проекции
        self.projection_distance = 500

        # Модель: списки 3D точек и рёбер
        self.model_points = []  # исходные 3D-координаты
        self.model_edges = []  # пары индексов вершин
        self.transformed_points = []  # точки после преобразования

        # Загружаем модель из файла "cube.txt" (если файл найден)
        try:
            self.load_model("cube.txt")
        except Exception as ex:
            messagebox.showerror("Ошибка", f"Не удалось загрузить модель:\n{ex}")

        # Привязываем клавиатурный обработчик (вращение с клавиатуры)
        self.focus_set()
        self.bind("<Key>", self.key_handler)

    def create_widgets(self):
        # Главные фреймы: левый для Canvas, правый для панели параметров
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self, width=300, bg="lightgray")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Холст для рисования
        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Панель параметров
        header = tk.Label(self.right_frame, text="Параметры\nпреобразования", bg="lightgray",
                          font=("Arial", 14, "bold"))
        header.pack(pady=10)

        # Группы параметров располагаем в отдельные строки (внутри каждого фрейма – горизонтально)
        # 1. Смещение
        trans_frame = tk.Frame(self.right_frame, bg="lightgray")
        trans_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(trans_frame, text="Смещение:", bg="lightgray").pack(side=tk.LEFT)
        tk.Label(trans_frame, text="X:", bg="lightgray").pack(side=tk.LEFT, padx=(5, 0))
        self.tx_entry = tk.Entry(trans_frame, width=5)
        self.tx_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(trans_frame, text="Y:", bg="lightgray").pack(side=tk.LEFT)
        self.ty_entry = tk.Entry(trans_frame, width=5)
        self.ty_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(trans_frame, text="Z:", bg="lightgray").pack(side=tk.LEFT)
        self.tz_entry = tk.Entry(trans_frame, width=5)
        self.tz_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.tx_entry.insert(0, "0")
        self.ty_entry.insert(0, "0")
        self.tz_entry.insert(0, "0")

        # 2. Поворот
        rot_frame = tk.Frame(self.right_frame, bg="lightgray")
        rot_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(rot_frame, text="Поворот (°):", bg="lightgray").pack(side=tk.LEFT)
        tk.Label(rot_frame, text="X:", bg="lightgray").pack(side=tk.LEFT, padx=(5, 0))
        self.rx_entry = tk.Entry(rot_frame, width=5)
        self.rx_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(rot_frame, text="Y:", bg="lightgray").pack(side=tk.LEFT)
        self.ry_entry = tk.Entry(rot_frame, width=5)
        self.ry_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(rot_frame, text="Z:", bg="lightgray").pack(side=tk.LEFT)
        self.rz_entry = tk.Entry(rot_frame, width=5)
        self.rz_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.rx_entry.insert(0, "0")
        self.ry_entry.insert(0, "0")
        self.rz_entry.insert(0, "0")

        # 3. Масштабирование
        scale_frame = tk.Frame(self.right_frame, bg="lightgray")
        scale_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(scale_frame, text="Масштаб:", bg="lightgray").pack(side=tk.LEFT)
        tk.Label(scale_frame, text="X:", bg="lightgray").pack(side=tk.LEFT, padx=(5, 0))
        self.sx_entry = tk.Entry(scale_frame, width=5)
        self.sx_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(scale_frame, text="Y:", bg="lightgray").pack(side=tk.LEFT)
        self.sy_entry = tk.Entry(scale_frame, width=5)
        self.sy_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(scale_frame, text="Z:", bg="lightgray").pack(side=tk.LEFT)
        self.sz_entry = tk.Entry(scale_frame, width=5)
        self.sz_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.sx_entry.insert(0, "1")
        self.sy_entry.insert(0, "1")
        self.sz_entry.insert(0, "1")

        # 4. Режим проекции
        proj_frame = tk.Frame(self.right_frame, bg="lightgray")
        proj_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(proj_frame, text="Проекция:", bg="lightgray").pack(side=tk.LEFT)
        tk.Radiobutton(proj_frame, text="Перспектива", variable=self.projection_mode,
                       value="perspective", bg="lightgray", command=self.draw_model).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(proj_frame, text="Ортогональная", variable=self.projection_mode,
                       value="ortho", bg="lightgray", command=self.draw_model).pack(side=tk.LEFT, padx=5)

        # 5. Кнопки управления – разместим их в ряд
        btn_frame = tk.Frame(self.right_frame, bg="lightgray")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        self.load_btn = tk.Button(btn_frame, text="Загрузить модель", command=self.load_model_dialog)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        self.apply_btn = tk.Button(btn_frame, text="Применить", command=self.apply_transformation)
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn = tk.Button(btn_frame, text="Сброс", command=self.reset_model)
        self.reset_btn.pack(side=tk.LEFT, padx=5)


        # Информация по клавишам (в отдельном фрейме)
        info_frame = tk.Frame(self.right_frame, bg="lightgray")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        info_text = "Клавиши: ←/→: поворот по Y, ↑/↓: поворот по X, Q/W: поворот по Z"
        info = tk.Label(info_frame, text=info_text, bg="lightgray", justify=tk.LEFT, wraplength=280)
        info.pack(anchor=tk.W)

    def load_model_dialog(self):
        filename = tk.filedialog.askopenfilename(title="Выберите файл модели",
                                                 filetypes=(("Text files", "*.txt"), ("Все файлы", "*.*")))
        if filename:
            try:
                self.load_model(filename)
            except Exception as ex:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке модели:\n{ex}")

    def load_model(self, filename):
        points, edges = read_model(filename)
        self.model_points = points
        self.model_edges = edges
        self.transformed_points = self.model_points.copy()
        self.draw_model()

    def apply_transformation(self):
        try:
            dx = float(self.tx_entry.get())
        except:
            dx = 0.0
        try:
            dy = float(self.ty_entry.get())
        except:
            dy = 0.0
        try:
            dz = float(self.tz_entry.get())
        except:
            dz = 0.0
        try:
            angle_x = float(self.rx_entry.get())
        except:
            angle_x = 0.0
        try:
            angle_y = float(self.ry_entry.get())
        except:
            angle_y = 0.0
        try:
            angle_z = float(self.rz_entry.get())
        except:
            angle_z = 0.0
        try:
            scale_x = float(self.sx_entry.get())
        except:
            scale_x = 1.0
        try:
            scale_y = float(self.sy_entry.get())
        except:
            scale_y = 1.0
        try:
            scale_z = float(self.sz_entry.get())
        except:
            scale_z = 1.0

        self.transformed_points = apply_transformation(self.model_points,
                                                       dx, dy, dz,
                                                       angle_x, angle_y, angle_z,
                                                       scale_x, scale_y, scale_z)
        self.draw_model()

    def reset_model(self):
        # Сброс значений в полях
        self.tx_entry.delete(0, tk.END);
        self.tx_entry.insert(0, "0")
        self.ty_entry.delete(0, tk.END);
        self.ty_entry.insert(0, "0")
        self.tz_entry.delete(0, tk.END);
        self.tz_entry.insert(0, "0")
        self.rx_entry.delete(0, tk.END);
        self.rx_entry.insert(0, "0")
        self.ry_entry.delete(0, tk.END);
        self.ry_entry.insert(0, "0")
        self.rz_entry.delete(0, tk.END);
        self.rz_entry.insert(0, "0")
        self.sx_entry.delete(0, tk.END);
        self.sx_entry.insert(0, "1")
        self.sy_entry.delete(0, tk.END);
        self.sy_entry.insert(0, "1")
        self.sz_entry.delete(0, tk.END);
        self.sz_entry.insert(0, "1")

        self.transformed_points = self.model_points.copy()
        self.draw_model()

    def draw_model(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10 or height < 10:
            width, height = 800, 600
        center_x = width / 2
        center_y = height / 2

        for edge in self.model_edges:
            i, j = edge
            if i < len(self.transformed_points) and j < len(self.transformed_points):
                p1 = self.transformed_points[i]
                p2 = self.transformed_points[j]
                if self.projection_mode.get() == "perspective":
                    proj1 = project_point(p1, self.projection_distance, center_x, center_y)
                    proj2 = project_point(p2, self.projection_distance, center_x, center_y)
                else:
                    proj1 = project_point_orthographic(p1, center_x, center_y)
                    proj2 = project_point_orthographic(p2, center_x, center_y)
                self.canvas.create_line(proj1[0], proj1[1], proj2[0], proj2[1],
                                        fill="blue", width=2)

    def key_handler(self, event):
        step = 5  # шаг поворота в градусах
        if event.keysym == "Left":
            try:
                current = float(self.ry_entry.get())
            except:
                current = 0
            self.ry_entry.delete(0, tk.END)
            self.ry_entry.insert(0, str(current - step))
            self.apply_transformation()
        elif event.keysym == "Right":
            try:
                current = float(self.ry_entry.get())
            except:
                current = 0
            self.ry_entry.delete(0, tk.END)
            self.ry_entry.insert(0, str(current + step))
            self.apply_transformation()
        elif event.keysym == "Up":
            try:
                current = float(self.rx_entry.get())
            except:
                current = 0
            self.rx_entry.delete(0, tk.END)
            self.rx_entry.insert(0, str(current - step))
            self.apply_transformation()
        elif event.keysym == "Down":
            try:
                current = float(self.rx_entry.get())
            except:
                current = 0
            self.rx_entry.delete(0, tk.END)
            self.rx_entry.insert(0, str(current + step))
            self.apply_transformation()
        elif event.char.lower() == "q":
            try:
                current = float(self.rz_entry.get())
            except:
                current = 0
            self.rz_entry.delete(0, tk.END)
            self.rz_entry.insert(0, str(current - step))
            self.apply_transformation()
        elif event.char.lower() == "w":
            try:
                current = float(self.rz_entry.get())
            except:
                current = 0
            self.rz_entry.delete(0, tk.END)
            self.rz_entry.insert(0, str(current + step))
            self.apply_transformation()


if __name__ == "__main__":
    app = TransformationApp()
    app.mainloop()
