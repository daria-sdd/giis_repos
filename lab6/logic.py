"""
Модуль логики работы с многоугольниками.
Содержит функции:
  - cross(o, a, b): вычисление векторного произведения трёх точек;
  - is_convex(vertices): проверка выпуклости многоугольника;
  - point_in_polygon(point, vertices): определение принадлежности точки многоугольнику;
  - internal_normals(vertices): вычисление внутренних нормалей для каждой стороны;
  - convex_hull(points): построение выпуклой оболочки методом Грэхема;
  - convex_hull_jarvis(points): построение выпуклой оболочки методом Джарвиса;
  - vector_cross(v, w): вычисление векторного произведения двух векторов;
  - segment_intersection(P, Q, R, S): поиск точки пересечения двух отрезков;
  - line_polygon_intersections(line, polygon): поиск точек пересечения линии с многоугольником;

  Алгоритмы заливки:
  - fill_polygon_ordered_edge_list(vertices, canvas, fill_color): заливка методом растровой развертки (упорядоченный список ребер);
  - fill_polygon_active_edge_list(vertices, canvas, fill_color): заливка методом растровой развертки с активным списком ребер;
  - simple_seed_fill(vertices, canvas, seed_point, fill_color): простой алгоритм заливки с затравкой;
  - scanline_seed_fill(vertices, canvas, seed_point, fill_color): построчная заливка с затравкой;

  Отладочные версии заливки (с задержкой) для пошагового отображения:
  - debug_fill_ordered_edge_list(vertices, canvas, fill_color, delay)
  - debug_fill_active_edge_list(vertices, canvas, fill_color, delay)
  - debug_seed_fill(vertices, canvas, seed_point, fill_color, delay)
  - debug_scanline_seed_fill(vertices, canvas, seed_point, fill_color, delay)
"""

def cross(o, a, b):
    """Вычисляет векторное произведение (a-o) x (b-o)."""
    return (a[0] - o[0])*(b[1] - o[1]) - (a[1] - o[1])*(b[0] - o[0])

def is_convex(vertices):
    """
    Проверяет выпуклость многоугольника (список вершин, каждый в виде (x, y)).
    Возвращает True, если все ненулевые векторные произведения имеют одинаковый знак.
    """
    if len(vertices) < 3:
        return False
    signs = []
    n = len(vertices)
    for i in range(n):
        p0 = vertices[i]
        p1 = vertices[(i + 1) % n]
        p2 = vertices[(i + 2) % n]
        cp = cross(p0, p1, p2)
        if cp != 0:
            signs.append(cp > 0)
    return all(signs) or (not any(signs))

def point_in_polygon(point, vertices):
    """
    Определяет принадлежность точки многоугольнику (метод трассировки луча).
    Возвращает True, если точка внутри, иначе False.
    """
    x, y = point
    inside = False
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i+1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1) + x1):
            inside = not inside
    return inside

def internal_normals(vertices):
    """
    Для данного многоугольника (список вершин) вычисляет нормали к каждому ребру,
    выбирая ту, которая направлена внутрь.
    Возвращает список нормалей, где каждая нормаль – кортеж (nx, ny).
    """
    normals = []
    n = len(vertices)
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i+1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        candidate1 = (-dy, dx)
        candidate2 = (dy, -dx)
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        test1 = (mid[0] + candidate1[0]*0.1, mid[1] + candidate1[1]*0.1)
        if point_in_polygon(test1, vertices):
            normals.append(candidate1)
        else:
            normals.append(candidate2)
    return normals

def convex_hull(points):
    """
    Построение выпуклой оболочки для набора точек (список (x, y))
    методом Грэхема. Если точек меньше трёх, возвращает исходный список.
    """
    if len(points) < 3:
        return points[:]
    points = sorted(points)
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    return hull

def dist_sq(a, b):
    """Возвращает квадрат расстояния между точками a и b."""
    return (b[0] - a[0])**2 + (b[1] - a[1])**2

def convex_hull_jarvis(points):
    """
    Построение выпуклой оболочки для набора точек методом Джарвиса (gift wrapping).
    Если точек меньше трёх, возвращает исходный список.
    """
    if len(points) < 3:
        return points[:]
    leftmost = min(points, key=lambda p: (p[0], p[1]))
    hull = []
    p = leftmost
    while True:
        hull.append(p)
        candidate = None
        for r in points:
            if r == p:
                continue
            if candidate is None:
                candidate = r
            else:
                cp = cross(p, candidate, r)
                if cp < 0:
                    candidate = r
                elif cp == 0:
                    if dist_sq(p, r) > dist_sq(p, candidate):
                        candidate = r
        p = candidate
        if p == leftmost:
            break
    return hull

# Функции для пересечения линии с многоугольником

def vector_cross(v, w):
    """
    Вычисляет векторное произведение двух векторов v и w, где v и w – (x, y).
    """
    return v[0]*w[1] - v[1]*w[0]

def segment_intersection(P, Q, R, S):
    """
    Определяет точку пересечения двух отрезков:
      от P до Q, от R до S.
    Если параметры t и u в диапазоне [0,1], возвращает (x, y); иначе None.
    """
    d1 = (Q[0]-P[0], Q[1]-P[1])
    d2 = (S[0]-R[0], S[1]-R[1])
    denom = vector_cross(d1, d2)
    if abs(denom) < 1e-10:
        return None
    diff = (R[0]-P[0], R[1]-P[1])
    t = vector_cross(diff, d2) / denom
    u = vector_cross(diff, d1) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (P[0] + t*d1[0], P[1] + t*d1[1])
    return None

def line_polygon_intersections(line, polygon):
    """
    Принимает:
      line – кортеж из двух точек (P, Q);
      polygon – список вершин (x, y) многоугольника.
    Для каждого ребра (от polygon[i] до polygon[(i+1)%n]) вычисляет точку пересечения.
    Возвращает список точек пересечения.
    """
    intersections = []
    P, Q = line
    n = len(polygon)
    for i in range(n):
        R = polygon[i]
        S = polygon[(i+1)%n]
        ip = segment_intersection(P, Q, R, S)
        if ip is not None:
            intersections.append(ip)
    return intersections

# Алгоритмы заливки многоугольника

def fill_polygon_ordered_edge_list(vertices, canvas, fill_color="yellow"):
    """
    Заливка методом растровой развертки с упорядоченным списком ребер.
    Для каждой строки от min_y до max_y вычисляются точки пересечения с ребрами,
    сортируются, и заполняются горизонтальные сегменты.
    """
    min_y = int(min(y for x, y in vertices))
    max_y = int(max(y for x, y in vertices))
    for y in range(min_y, max_y+1):
        intersections = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1)%n]
            if y1 == y2:
                continue
            if y >= min(y1, y2) and y < max(y1, y2):
                x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x_int)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i+1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i+1])
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)

def fill_polygon_active_edge_list(vertices, canvas, fill_color="cyan"):
    """
    Заливка методом растровой развертки с использованием активного списка ребер.
    Формируется таблица ребер, затем для каждой строки обновляется список активных ребер,
    и заливаются горизонтальные сегменты.
    """
    n = len(vertices)
    ET = []
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i+1)%n]
        if y1 == y2:
            continue
        if y1 < y2:
            ymin, ymax, x_at_ymin = y1, y2, x1
            inv_slope = (x2 - x1)/(y2 - y1)
        else:
            ymin, ymax, x_at_ymin = y2, y1, x2
            inv_slope = (x1 - x2)/(y1 - y2)
        ET.append({"ymin": int(ymin), "ymax": int(ymax), "x": x_at_ymin, "inv_slope": inv_slope})
    ET.sort(key=lambda e: e["ymin"])
    if not ET:
        return
    min_y = ET[0]["ymin"]
    max_y = max(e["ymax"] for e in ET)
    AEL = []
    et_index = 0
    for y in range(min_y, max_y):
        while et_index < len(ET) and ET[et_index]["ymin"] == y:
            AEL.append(ET[et_index])
            et_index += 1
        AEL = [edge for edge in AEL if edge["ymax"] > y]
        AEL.sort(key=lambda edge: edge["x"])
        for i in range(0, len(AEL), 2):
            if i+1 < len(AEL):
                x_start = int(AEL[i]["x"])
                x_end = int(AEL[i+1]["x"])
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)
        for edge in AEL:
            edge["x"] += edge["inv_slope"]

def simple_seed_fill(vertices, canvas, seed_point, fill_color="magenta"):
    """
    Простой алгоритм заливки с затравкой (flood fill) с использованием стека.
    Для каждого пикселя внутри ограничивающего прямоугольника, если он принадлежит многоугольнику,
    заливается одиночный пиксель.
    """
    min_x = int(min(x for x,y in vertices))
    max_x = int(max(x for x,y in vertices))
    min_y = int(min(y for x,y in vertices))
    max_y = int(max(y for x,y in vertices))
    stack = [(int(seed_point[0]), int(seed_point[1]))]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if point_in_polygon((x, y), vertices):
            canvas.create_line(x, y, x+1, y, fill=fill_color)
            if x+1 <= max_x:
                stack.append((x+1, y))
            if x-1 >= min_x:
                stack.append((x-1, y))
            if y+1 <= max_y:
                stack.append((x, y+1))
            if y-1 >= min_y:
                stack.append((x, y-1))

def scanline_seed_fill(vertices, canvas, seed_point, fill_color="orange"):
    """
    Построчный алгоритм заливки с затравкой.
    Из затравочной точки заполняется текущая строка, затем соседние строки.
    """
    def fill_line(x, y):
        x_left = x
        while point_in_polygon((x_left-1, y), vertices):
            x_left -= 1
        x_right = x
        while point_in_polygon((x_right+1, y), vertices):
            x_right += 1
        canvas.create_line(x_left, y, x_right, y, fill=fill_color)
        return x_left, x_right

    stack = [(int(seed_point[0]), int(seed_point[1]))]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if not point_in_polygon((x, y), vertices):
            continue
        x_left, x_right = fill_line(x, y)
        for new_y in (y-1, y+1):
            for new_x in range(x_left, x_right+1):
                if (new_x, new_y) not in visited and point_in_polygon((new_x, new_y), vertices):
                    stack.append((new_x, new_y))

# Отладочные версии (пошаговые заливки)

def debug_fill_ordered_edge_list(vertices, canvas, fill_color="yellow", delay=50):
    """
    Отладочная заливка методом растровой развертки с упорядоченным списком ребер.
    После отрисовки каждой сканирующей строки вызывается update() и задержка delay.
    """
    min_y = int(min(y for x,y in vertices))
    max_y = int(max(y for x,y in vertices))
    for y in range(min_y, max_y+1):
        intersections = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i+1)%n]
            if y1 == y2:
                continue
            if y >= min(y1, y2) and y < max(y1, y2):
                x_int = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x_int)
        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i+1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i+1])
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)
        canvas.update()
        canvas.after(delay)

def debug_fill_active_edge_list(vertices, canvas, fill_color="cyan", delay=50):
    """
    Отладочная заливка методом растровой развертки с активным списком ребер.
    После каждой строки обновляется холст и делается задержка.
    """
    n = len(vertices)
    ET = []
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i+1)%n]
        if y1 == y2:
            continue
        if y1 < y2:
            ymin, ymax, x_at_ymin = y1, y2, x1
            inv_slope = (x2-x1)/(y2-y1)
        else:
            ymin, ymax, x_at_ymin = y2, y1, x2
            inv_slope = (x1-x2)/(y1-y2)
        ET.append({"ymin": int(ymin), "ymax": int(ymax), "x": x_at_ymin, "inv_slope": inv_slope})
    ET.sort(key=lambda e: e["ymin"])
    if not ET:
        return
    min_y = ET[0]["ymin"]
    max_y = max(e["ymax"] for e in ET)
    AEL = []
    et_index = 0
    for y in range(min_y, max_y):
        while et_index < len(ET) and ET[et_index]["ymin"] == y:
            AEL.append(ET[et_index])
            et_index += 1
        AEL = [edge for edge in AEL if edge["ymax"] > y]
        AEL.sort(key=lambda edge: edge["x"])
        for i in range(0, len(AEL), 2):
            if i+1 < len(AEL):
                x_start = int(AEL[i]["x"])
                x_end = int(AEL[i+1]["x"])
                canvas.create_line(x_start, y, x_end, y, fill=fill_color)
        for edge in AEL:
            edge["x"] += edge["inv_slope"]
        canvas.update()
        canvas.after(delay)

def debug_seed_fill(vertices, canvas, seed_point, fill_color="magenta", delay=50):
    """
    Отладочная (пошаговая) заливка методом простого заполнения с затравкой.
    После заливки каждого пикселя вызывается canvas.update() и задержка delay.
    """
    min_x = int(min(x for x,y in vertices))
    max_x = int(max(x for x,y in vertices))
    min_y = int(min(y for x,y in vertices))
    max_y = int(max(y for x,y in vertices))
    stack = [(int(seed_point[0]), int(seed_point[1]))]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x,y) in visited:
            continue
        visited.add((x,y))
        if not point_in_polygon((x,y), vertices):
            continue
        canvas.create_line(x, y, x+1, y, fill=fill_color)
        canvas.update()
        canvas.after(delay)
        if x+1 <= max_x:
            stack.append((x+1, y))
        if x-1 >= min_x:
            stack.append((x-1, y))
        if y+1 <= max_y:
            stack.append((x, y+1))
        if y-1 >= min_y:
            stack.append((x, y-1))

def debug_scanline_seed_fill(vertices, canvas, seed_point, fill_color="orange", delay=0.2):
    def fill_line(x, y):
        x_left = x
        while point_in_polygon((x_left-1, y), vertices):
            x_left -= 1
        x_right = x
        while point_in_polygon((x_right+1, y), vertices):
            x_right += 1
        canvas.create_line(x_left, y, x_right, y, fill=fill_color)
        canvas.update()
        canvas.after(delay)
        return x_left, x_right

    stack = [(int(seed_point[0]), int(seed_point[1]))]
    visited = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if not point_in_polygon((x, y), vertices):
            continue
        x_left, x_right = fill_line(x, y)
        for new_y in (y-1, y+1):
            for new_x in range(x_left, x_right+1):
                if (new_x, new_y) not in visited and point_in_polygon((new_x, new_y), vertices):
                    stack.append((new_x, new_y))


