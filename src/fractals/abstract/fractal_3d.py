from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QMouseEvent, QWheelEvent

from .fragment_only_fractal import FragmentOnlyFractal
from .screenshotable_fractal import ScreenshotableFractal

__all__ = ["Fractal3D"]


class Fractal3D(FragmentOnlyFractal, ScreenshotableFractal):
    def __init__(self, name: str, fragment_shader_path: str, *args, **kwargs):
        super().__init__(fragment_shader_path, name, *args, **kwargs)

        self._h_angle = 0.0
        self._v_angle = 0.0

        self._zoom_factor = 3.0

        self._last_mouse_pos = self._current_mouse_pos

    @property
    def v_angle(self) -> float:
        return self._v_angle

    @v_angle.setter
    def v_angle(self, new_value: float) -> None:
        self._v_angle = new_value
        self.update()

    @property
    def h_angle(self) -> float:
        return self._h_angle

    @h_angle.setter
    def h_angle(self, new_value: float) -> None:
        self._h_angle = new_value
        self.update()

    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, new_value: float) -> None:
        self._zoom_factor = new_value
        self.update()

    def fractal_controls(self) -> list[Any]:
        return ScreenshotableFractal.fractal_controls(self)

    def animation_controls(self) -> list[Any]:
        return []

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        match (event.buttons()):
            case Qt.MouseButton.LeftButton:
                diff = self._current_mouse_pos - self._last_mouse_pos
                self.h_angle -= diff.x() / 100
                self.v_angle -= diff.y() / 100

        self._last_mouse_pos = self._current_mouse_pos

    def mousePressEvent(self, event: QMouseEvent) -> None:
        match (event.button()):
            case Qt.MouseButton.LeftButton:
                self._last_mouse_pos = self._current_mouse_pos
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        match (event.button()):
            case Qt.MouseButton.LeftButton:
                self.unsetCursor()

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoom_factor /= 1.01 ** (event.angleDelta().y() / 100)
