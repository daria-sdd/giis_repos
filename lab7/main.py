import tkinter as tk
import numpy as np
import scipy.spatial
import math


def voronoi_finite_polygons_2d(vor, radius=None):

    if vor.points.shape[1] != 2:
        raise ValueError("Функция работает только с 2D данными")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max() * 2

    # Строим словарь: для каждой точки собираем все рёбра (ridges)
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Для каждой точки восстанавливаем конечный полигон
    for p_idx, region_idx in enumerate(vor.point_region):
        vertices = vor.regions[region_idx]
        # Если все вершины конечные — оставляем регион как есть
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue

        # Иначе восстанавливаем регион
        ridges = all_ridges[p_idx]
        region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            # Если v2 == -1, меняем местами
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0 and v2 >= 0:
                continue  # это ребро конечное

            # Ребро бесконечное: вычисляем новую вершину
            t = vor.points[p2] - vor.points[p_idx]
            t /= np.linalg.norm(t)
            # Перпендикуляр к направлению
            n = np.array([-t[1], t[0]])

            midpoint = vor.points[[p_idx, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # Сортируем вершины полигона против часовой стрелки
        vs = np.array([new_vertices[v] for v in region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        region = [v for _, v in sorted(zip(angles, region))]
        new_regions.append(region)

    return new_regions, np.array(new_vertices)


class VoronoiTriangulationApp:
    def __init__(self, root):
        self.root = root
        root.title("Лабораторная работа: Компьютерная графика")
        self.canvas_width = 600
        self.canvas_height = 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=5, pady=5)

        # Панель с кнопками
        button_frame = tk.Frame(root)
        button_frame.pack(padx=5, pady=5)

        self.mode = "cursor"  # Возможные режимы: "cursor", "add"
        self.points = []  # Будем хранить список точек в виде (x, y)

        self.btn_cursor = tk.Button(button_frame, text="Курсор", command=self.set_mode_cursor)
        self.btn_cursor.pack(side=tk.LEFT, padx=2)

        self.btn_add = tk.Button(button_frame, text="Добавить точки", command=self.set_mode_add)
        self.btn_add.pack(side=tk.LEFT, padx=2)

        self.btn_triangulation = tk.Button(button_frame, text="Триангуляция", command=self.draw_triangulation)
        self.btn_triangulation.pack(side=tk.LEFT, padx=2)

        self.btn_voronoi = tk.Button(button_frame, text="Диаграмма Вороного", command=self.draw_voronoi)
        self.btn_voronoi.pack(side=tk.LEFT, padx=2)

        self.btn_clear = tk.Button(button_frame, text="Очистить", command=self.clear_canvas)
        self.btn_clear.pack(side=tk.LEFT, padx=2)

        # Обработчик кликов по Canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def set_mode_cursor(self):
        self.mode = "cursor"

    def set_mode_add(self):
        self.mode = "add"

    def on_canvas_click(self, event):
        if self.mode == "add":
            x, y = event.x, event.y
            self.points.append((x, y))
            self.draw_point(x, y)

    def draw_point(self, x, y, color="black"):
        r = 3
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=color)

    def draw_triangulation(self):
        """Рисует триангуляцию Делоне (синие линии) по набранным точкам."""
        if len(self.points) < 3:
            return
        pts = np.array(self.points)
        delaunay = scipy.spatial.Delaunay(pts)
        for simplex in delaunay.simplices:
            # Рисуем замкнутую ломаную по вершинам треугольника
            pts_line = [tuple(pts[i]) for i in simplex] + [tuple(pts[simplex[0]])]
            self.canvas.create_line(pts_line, fill="blue", width=1)
        # Повторно рисуем точки, чтобы они были поверх линий
        for x, y in self.points:
            self.draw_point(x, y)

    def draw_voronoi(self):
        """Рисует диаграмму Вороного (красные пунктирные линии) по набранным точкам."""
        if len(self.points) < 2:
            return
        pts = np.array(self.points)
        vor = scipy.spatial.Voronoi(pts)
        regions, vertices = voronoi_finite_polygons_2d(vor, radius=1000)

        # Рисуем каждую область как ломаную линию
        for region in regions:
            polygon = vertices[region]
            # При необходимости—клиппинг к границам Canvas
            clipped_polygon = []
            for x, y in polygon:
                x = max(0, min(self.canvas_width, x))
                y = max(0, min(self.canvas_height, y))
                clipped_polygon.append((x, y))
            if len(clipped_polygon) > 1:
                points_line = []
                for pt in clipped_polygon:
                    points_line.extend(pt)
                # Замыкаем полигон
                points_line.extend(clipped_polygon[0])
                self.canvas.create_line(points_line, fill="red", width=1, dash=(4, 2))

        # Перерисовываем точки
        for x, y in self.points:
            self.draw_point(x, y)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.points = []


if __name__ == "__main__":
    root = tk.Tk()
    app = VoronoiTriangulationApp(root)
    root.mainloop()
