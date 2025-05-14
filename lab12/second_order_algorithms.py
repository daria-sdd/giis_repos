import math
from first_order_algorithms import ipart, round_, fpart, rfpart

# Построение окружности по алгоритму Брезенхэма
def compute_circle_points(cx, cy, ex, ey):
    """Первая точка – центр, вторая – точка на окружности."""
    r = int(round(math.sqrt((ex - cx)**2 + (ey - cy)**2)))
    points = []
    x = 0
    y = r
    d = 3 - 2 * r

    def add_circle_points(cx, cy, x, y):
        pts = [
            (cx + x, cy + y, 1.0),
            (cx - x, cy + y, 1.0),
            (cx + x, cy - y, 1.0),
            (cx - x, cy - y, 1.0),
            (cx + y, cy + x, 1.0),
            (cx - y, cy + x, 1.0),
            (cx + y, cy - x, 1.0),
            (cx - y, cy - x, 1.0)
        ]
        for pt in pts:
            if pt not in points:
                points.append(pt)

    while x <= y:
        add_circle_points(cx, cy, x, y)
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1
    points.sort(key=lambda p: (p[0], p[1]))
    return points

# Построение эллипса (метод середины эллипса)
def compute_ellipse_points(cx, cy, ex, ey):
    """Первый клик – центр, второй задаёт полуоси: a = |ex - cx|, b = |ey - cy|."""
    points = []
    a = int(round(abs(ex - cx)))
    b = int(round(abs(ey - cy)))
    if a == 0: a = 1
    if b == 0: b = 1
    x = 0
    y = b
    d1 = (b * b) - (a * a) * b + (0.25 * a * a)
    dx = 2 * b * b * x
    dy = 2 * a * a * y

    while dx < dy:
        points.extend([
            (cx + x, cy + y, 1.0),
            (cx - x, cy + y, 1.0),
            (cx + x, cy - y, 1.0),
            (cx - x, cy - y, 1.0)
        ])
        if d1 < 0:
            x += 1
            dx += 2 * b * b
            d1 = d1 + dx + b * b
        else:
            x += 1
            y -= 1
            dx += 2 * b * b
            dy -= 2 * a * a
            d1 = d1 + dx - dy + b * b

    d2 = (b * b) * ((x + 0.5) ** 2) + (a * a) * ((y - 1) ** 2) - (a * a * b * b)
    while y >= 0:
        points.extend([
            (cx + x, cy + y, 1.0),
            (cx - x, cy + y, 1.0),
            (cx + x, cy - y, 1.0),
            (cx - x, cy - y, 1.0)
        ])
        if d2 > 0:
            y -= 1
            dy -= 2 * a * a
            d2 = d2 + a * a - dy
        else:
            x += 1
            y -= 1
            dx += 2 * b * b
            dy -= 2 * a * a
            d2 = d2 + dx - dy + a * a
    return points

# Построение симметричной гиперболы
def compute_hyperbola_points(cx, cy, ex, ey):
    """
    Построение гиперболы по уравнению:
       ((x - cx)^2)/(a^2) - ((y - cy)^2)/(b^2) = 1
    где a = |ex - cx|, b = |ey - cy|.
    Сначала строится правая ветвь (x >= cx + a), затем отражается по вертикали.
    """
    points = []
    a = abs(ex - cx)
    if a == 0:
        a = 1
    b = abs(ey - cy)
    if b == 0:
        b = 1
    x_start = cx + a
    x_end = ex if ex > (cx + a) else (cx + a + 100)
    for x in range(int(round(x_start)), int(round(x_end)) + 1):
        val = ((x - cx) ** 2) / (a * a) - 1
        if val < 0:
            continue
        try:
            y_offset = b * math.sqrt(val)
        except ValueError:
            continue
        points.append((x, cy + y_offset, 1.0))
        points.append((x, cy - y_offset, 1.0))
    # Отражаем полученную ветвь относительно вертикальной оси через cx
    mirror_points = []
    for (x, y, br) in points:
        mirror_points.append((2 * cx - x, y, br))
    all_points = points + mirror_points
    all_points.sort(key=lambda p: (p[0], p[1]))
    return all_points

# Построение параболы с вершиной, открывающейся вверх
def compute_parabola_points(cx, cy, ex, ey):
    """
    Построение параболы по уравнению:
         (x - cx)^2 = 4a * (y - cy)
    Чтобы парабола открывалась вверх, строим правую и левую ветви
    с вершиной в (cx, cy). Если ey > cy, вычисляем:
         a = (ex - cx)^2 / (4*(ey - cy))
    Если ey <= cy, используем a = 1.
    """
    points = []
    if ey <= cy:
        a_param = 1
        y_end = cy + 100
    else:
        a_param = ((ex - cx) ** 2) / (4 * (ey - cy))
        y_end = ey
    for y in range(int(round(cy)), int(round(y_end)) + 1):
        t = y - cy
        try:
            offset = math.sqrt(4 * a_param * t)
        except ValueError:
            continue
        points.append((cx + offset, y, 1.0))
        points.append((cx - offset, y, 1.0))
    return points
