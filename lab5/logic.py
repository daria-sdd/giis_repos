"""
  - cross(o, a, b): вычисление векторного произведения трёх точек;
  - is_convex(vertices): проверка выпуклости многоугольника;
  - point_in_polygon(point, vertices): определение принадлежности точки многоугольнику;
  - internal_normals(vertices): вычисление внутренних нормалей для каждой стороны;
  - convex_hull(points): построение выпуклой оболочки методом Грэхема;
  - convex_hull_jarvis(points): построение выпуклой оболочки методом Джарвиса;
  - vector_cross(v, w): вычисление векторного произведения двух векторов;
  - segment_intersection(P, Q, R, S): поиск точки пересечения двух отрезков;
  - line_polygon_intersections(line, polygon): поиск точек пересечения линии с многоугольником.
"""
#вычисление векторного произведения трёх точек
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

#проверка выпуклости многоугольника
def is_convex(vertices):
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

#определение принадлежности точки многоугольнику
def point_in_polygon(point, vertices):
    x, y = point
    inside = False
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and \
           (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

#вычисление внутренних нормалей для каждой стороны
def internal_normals(vertices):
    normals = []
    n = len(vertices)
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        # Два кандидата – перпендикуляры к ребру
        candidate1 = (-dy, dx)
        candidate2 = (dy, -dx)
        mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        test1 = (mid[0] + candidate1[0] * 0.1, mid[1] + candidate1[1] * 0.1)
        if point_in_polygon(test1, vertices):
            normals.append(candidate1)
        else:
            normals.append(candidate2)
    return normals

#построение выпуклой оболочки методом Грэхема
def convex_hull(points):
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
    return (b[0] - a[0])**2 + (b[1] - a[1])**2


def convex_hull_jarvis(points):
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

# Функции для нахождения точек пересечения линии с многоугольником

def vector_cross(v, w):
    return v[0] * w[1] - v[1] * w[0]

#поиск точки пересечения двух отрезков
def segment_intersection(P, Q, R, S):
    d1 = (Q[0] - P[0], Q[1] - P[1])
    d2 = (S[0] - R[0], S[1] - R[1])
    denom = vector_cross(d1, d2)
    if abs(denom) < 1e-10:
        return None  # Отрезки параллельны или коллинеарны
    diff = (R[0] - P[0], R[1] - P[1])
    t = vector_cross(diff, d2) / denom
    u = vector_cross(diff, d1) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (P[0] + t * d1[0], P[1] + t * d1[1])
    return None

def line_polygon_intersections(line, polygon):
    intersections = []
    P, Q = line
    n = len(polygon)
    for i in range(n):
        R = polygon[i]
        S = polygon[(i + 1) % n]
        ip = segment_intersection(P, Q, R, S)
        if ip is not None:
            intersections.append(ip)
    return intersections

if __name__ == "__main__":
    test_line = ((50, 50), (250, 150))
    test_polygon = [(100, 30), (300, 30), (300, 200), (100, 200)]
    pts = line_polygon_intersections(test_line, test_polygon)
    print("Точки пересечения линии и многоугольника:")
    for pt in pts:
        print(pt)
