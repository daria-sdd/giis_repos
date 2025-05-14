# curve_logic.py
def hermite_curve_segments(points):

    if len(points) < 2:
        return []
    n = len(points)
    # Вычисление касательных
    T = []
    T.append((points[1][0] - points[0][0], points[1][1] - points[0][1]))
    for i in range(1, n - 1):
        tangent = ((points[i + 1][0] - points[i - 1][0]) * 0.5,
                   (points[i + 1][1] - points[i - 1][1]) * 0.5)
        T.append(tangent)
    T.append((points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]))

    def hermite_basis(t):
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2
        return h00, h10, h01, h11

    segments = []
    # Для каждого сегмента между точками
    for i in range(n - 1):
        segment_points = []
        for step in range(21):
            t = step / 20.0
            h00, h10, h01, h11 = hermite_basis(t)
            x = h00 * points[i][0] + h10 * T[i][0] + h01 * points[i + 1][0] + h11 * T[i + 1][0]
            y = h00 * points[i][1] + h10 * T[i][1] + h01 * points[i + 1][1] + h11 * T[i + 1][1]
            segment_points.append((x, y))
        for j in range(len(segment_points) - 1):
            segments.append((segment_points[j][0], segment_points[j][1],
                             segment_points[j + 1][0], segment_points[j + 1][1]))
    return segments


def bezier_curve_segments(points):

    if len(points) < 2:
        return []
    if len(points) == 2:
        return [(points[0][0], points[0][1], points[1][0], points[1][1])]

    P0 = points[0]
    P2 = points[-1]
    n = len(points)
    sum_x = sum(p[0] for p in points[1:-1])
    sum_y = sum(p[1] for p in points[1:-1])
    count = n - 2
    C = (sum_x / count, sum_y / count)

    segments = []
    points_curve = []
    for i in range(101):
        t = i / 100.0
        omt = 1 - t
        x = (omt ** 2) * P0[0] + 2 * t * omt * C[0] + (t ** 2) * P2[0]
        y = (omt ** 2) * P0[1] + 2 * t * omt * C[1] + (t ** 2) * P2[1]
        points_curve.append((x, y))
    for j in range(len(points_curve) - 1):
        segments.append((points_curve[j][0], points_curve[j][1],
                         points_curve[j + 1][0], points_curve[j + 1][1]))
    return segments


def bspline_curve_segments(points):

    if len(points) < 4:
        return []
    segments = []
    for i in range(len(points) - 3):
        segment_points = []
        for step in range(21):
            t = step / 20.0
            B0 = ((1 - t) ** 3) / 6.0
            B1 = (3 * t ** 3 - 6 * t ** 2 + 4) / 6.0
            B2 = (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6.0
            B3 = (t ** 3) / 6.0
            x = (B0 * points[i][0] +
                 B1 * points[i + 1][0] +
                 B2 * points[i + 2][0] +
                 B3 * points[i + 3][0])
            y = (B0 * points[i][1] +
                 B1 * points[i + 1][1] +
                 B2 * points[i + 2][1] +
                 B3 * points[i + 3][1])
            segment_points.append((x, y))
        for j in range(len(segment_points) - 1):
            segments.append((segment_points[j][0], segment_points[j][1],
                             segment_points[j + 1][0], segment_points[j + 1][1]))
    return segments
