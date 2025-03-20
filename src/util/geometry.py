from math import cos, pi, sin

from PySide6.QtCore import QPointF


def rotate_point(point: QPointF, angle: float, center: QPointF | None = None) -> QPointF:
    if center is None:
        center = QPointF(0, 0)

    x1, y1 = point.x(), point.y()
    x0, y0 = center.x(), center.y()

    c, s = cos(pi * angle), sin(pi * angle)

    x = (x1 - x0) * c - (y1 - y0) * s
    y = (x1 - x0) * s + (y1 - y0) * c

    return QPointF(x, y)
