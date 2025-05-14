import math
import numpy as np


def read_model(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    clean_lines = []
    for line in lines:
        l = line.strip()
        if l and not l.startswith('#'):
            clean_lines.append(l)
    if not clean_lines:
        raise ValueError("Файл модели пуст или имеет неверный формат")

    n = int(clean_lines[0])
    points = []
    for i in range(1, n + 1):
        parts = clean_lines[i].split()
        points.append((float(parts[0]), float(parts[1]), float(parts[2])))
    m = int(clean_lines[n + 1])
    edges = []
    for i in range(n + 2, n + 2 + m):
        parts = clean_lines[i].split()
        edges.append((int(parts[0]), int(parts[1])))
    return points, edges


def build_transformation_matrix(dx, dy, dz, angle_x, angle_y, angle_z, scale_x, scale_y, scale_z):
    # Перевод углов в радианы
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Матрица масштабирования S
    S = np.array([
        [scale_x, 0, 0, 0],
        [0, scale_y, 0, 0],
        [0, 0, scale_z, 0],
        [0, 0, 0, 1]
    ])

    # Матрица поворота вокруг X: Rx
    Rx = np.array([
        [1, 0, 0, 0],
        [0, math.cos(ax), -math.sin(ax), 0],
        [0, math.sin(ax), math.cos(ax), 0],
        [0, 0, 0, 1]
    ])

    # Матрица поворота вокруг Y: Ry
    Ry = np.array([
        [math.cos(ay), 0, math.sin(ay), 0],
        [0, 1, 0, 0],
        [-math.sin(ay), 0, math.cos(ay), 0],
        [0, 0, 0, 1]
    ])

    # Матрица поворота вокруг Z: Rz
    Rz = np.array([
        [math.cos(az), -math.sin(az), 0, 0],
        [math.sin(az), math.cos(az), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    # Матрица смещения T
    T = np.array([
        [1, 0, 0, dx],
        [0, 1, 0, dy],
        [0, 0, 1, dz],
        [0, 0, 0, 1]
    ])

    # Композиция преобразований:
    # M = T * Rz * Ry * Rx * S
    M = T @ Rz @ Ry @ Rx @ S
    return M


def apply_transformation(points, dx, dy, dz, angle_x, angle_y, angle_z, scale_x, scale_y, scale_z):
    M = build_transformation_matrix(dx, dy, dz, angle_x, angle_y, angle_z, scale_x, scale_y, scale_z)
    transformed_points = []
    for (x, y, z) in points:
        vec = np.array([x, y, z, 1])
        new_vec = M @ vec  # матричное умножение
        transformed_points.append((new_vec[0], new_vec[1], new_vec[2]))
    return transformed_points


def project_point(point, d, center_x, center_y):
    x, y, z = point
    factor = d / (z + d) if (z + d) != 0 else d
    x_proj = center_x + x * factor
    y_proj = center_y - y * factor  # инвертируем y, так как в Canvas ось Y растёт вниз
    return (x_proj, y_proj)


def project_point_orthographic(point, center_x, center_y):
    x, y, z = point
    return (center_x + x, center_y - y)



