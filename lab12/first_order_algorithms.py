import math

# Общие вспомогательные функции
def ipart(x):
    return int(math.floor(x))

def round_(x):
    return ipart(x + 0.5)

def fpart(x):
    return x - math.floor(x)

def rfpart(x):
    return 1 - fpart(x)

def intensity_to_hex(c):
    """Преобразует яркость (0..1) в оттенки серого.
       При c == 1 – получаем черный, при c == 0 – белый."""
    if c < 0:
        c = 0
    if c > 1:
        c = 1
    val = int(255 * (1 - c))
    return f"#{val:02x}{val:02x}{val:02x}"

# Алгоритм ЦДА
def compute_dda_points(x1, y1, x2, y2):
    """Возвращает список точек (x, y, яркость=1.0) для алгоритма ЦДА."""
    points = []
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    x_inc = dx / steps if steps != 0 else 0
    y_inc = dy / steps if steps != 0 else 0
    x = x1
    y = y1
    for _ in range(steps + 1):
        points.append((x, y, 1.0))
        x += x_inc
        y += y_inc
    return points

# Алгоритм Брезенхема
def compute_bresenham_points(x1, y1, x2, y2):
    """Возвращает список точек (x, y, яркость=1.0) для алгоритма Брезенхема."""
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1, 1.0))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points

# Алгоритм Ву для сглаживания
def compute_wu_points(x0, y0, x1, y1):
    """Возвращает список точек (x, y, яркость) для алгоритма Ву."""
    points = []
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1

    # Первый конечный пиксель
    xend = round_(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = ipart(yend)
    if steep:
        points.append((ypxl1,   xpxl1, rfpart(yend) * xgap))
        points.append((ypxl1 + 1, xpxl1, fpart(yend) * xgap))
    else:
        points.append((xpxl1, ypxl1,   rfpart(yend) * xgap))
        points.append((xpxl1, ypxl1 + 1, fpart(yend) * xgap))
    intery = yend + gradient

    # Второй конечный пиксель
    xend = round_(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = ipart(yend)

    # Основной цикл
    for x in range(xpxl1 + 1, xpxl2):
        if steep:
            points.append((ipart(intery),   x, rfpart(intery)))
            points.append((ipart(intery) + 1, x, fpart(intery)))
        else:
            points.append((x, ipart(intery),   rfpart(intery)))
            points.append((x, ipart(intery) + 1, fpart(intery)))
        intery += gradient

    if steep:
        points.append((ypxl2,   xpxl2, rfpart(yend) * xgap))
        points.append((ypxl2 + 1, xpxl2, fpart(yend) * xgap))
    else:
        points.append((xpxl2, ypxl2,   rfpart(yend) * xgap))
        points.append((xpxl2, ypxl2 + 1, fpart(yend) * xgap))
    return points
