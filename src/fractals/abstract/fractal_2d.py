from typing import Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QCursor, QMouseEvent, QWheelEvent

from frontend.components import NamedCheckBox, NamedSlider
from util import rotate_point, use_setter

from .fragment_only_fractal import FragmentOnlyFractal
from .screenshotable_fractal import ScreenshotableFractal

__all__ = ["Fractal2D"]


class Fractal2D(FragmentOnlyFractal, ScreenshotableFractal):
    def __init__(self, fragment_shader_path: str, *args, **kwargs):
        super().__init__(fragment_shader_path, *args, **kwargs)

        self._offset = QPointF(0.0, 0.0)
        self._zoom_factor = 1.0
        self._central_lines = False
        self._rotation_angle = 0.0

        self._last_mouse_pos = self._current_mouse_pos

    @property
    def rotation_angle(self) -> float:
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, new_value: float) -> None:
        self._rotation_angle = new_value
        self.update()

    @property
    def central_lines(self) -> bool:
        return self._central_lines

    @central_lines.setter
    def central_lines(self, new_value: bool) -> None:
        self._central_lines = new_value
        self.update()

    @property
    def offset(self) -> QPointF:
        return self._offset

    @offset.setter
    def offset(self, new_value: QPointF) -> None:
        self._offset = new_value
        self.update()

    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, new_value: float) -> None:
        self._zoom_factor = new_value
        self.update()

    def fractal_controls(self) -> list[Any]:
        return ScreenshotableFractal.fractal_controls(self) + [
            NamedSlider(
                name="Rotation Angle",
                scope=(-5000, 5000),
                initial=self.rotation_angle,
                handlers=[lambda value: use_setter(self, "rotation_angle", value / 5000)],
            ),
            NamedCheckBox(
                name="Central Lines",
                initial=self.central_lines,
                handlers=[lambda value: use_setter(self, "central_lines", value)],
            ),
        ]

    def motion_controls(self) -> list[Any]:
        return []

    def _current_state(self) -> dict:
        raise RuntimeError()

    def _load_state(self, state: dict) -> None:
        raise RuntimeError()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        match (event.buttons()):
            case Qt.MouseButton.LeftButton:
                last_pos = self._translate_point(QPointF(self._last_mouse_pos))
                current_pos = self._translate_point(QPointF(self._current_mouse_pos))

                diff = current_pos - last_pos

                self.offset -= diff

        self._last_mouse_pos = self._current_mouse_pos

    def mousePressEvent(self, event: QMouseEvent) -> None:
        match (event.button()):
            case Qt.MouseButton.LeftButton:
                self._last_mouse_pos = self._current_mouse_pos
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

            case Qt.MouseButton.RightButton:
                self.offset += self._translate_point(QPointF(self._current_mouse_pos))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        match (event.button()):
            case Qt.MouseButton.LeftButton:
                self.unsetCursor()

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.zoom_factor *= 1.1 ** (event.angleDelta().y() / 100)

    # def _setup_status_bar(self):
    #     self.add_status("MAX_ITER", "ITER: {}")
    #     self.add_status("OFFSET", "POSITION: {0:.16f}, {1:.16f}", unpack=True)
    #     self.add_status("ZOOM", "ZOOM: {0:.5e}")
    #     self.add_status("ARG_C", "ARG: {0:.2f}")
    #     self.add_status("ABS_C", "ABS: {0:.4f}")
    #     self.add_status("POWER", "POWER: {0:.1f}")

    def _translate_point(self, point: QPointF) -> QPointF:
        """Translates widget's point to fractal's point"""

        point -= QPointF(self.width(), self.height()) / 2
        point = rotate_point(point, self.rotation_angle, self.offset)

        factor = 2 / min(self.width(), self.height()) / self.zoom_factor

        point *= factor
        point.setY(-point.y())

        return point
