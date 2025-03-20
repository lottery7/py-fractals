from typing import Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QCursor, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QColorDialog

from frontend.components import ColoredButton, NamedCheckBox, NamedSlider
from frontend.constants import get_color
from util import rotate_point, use_setter

from .fractal_abc import FractalABC

__all__ = ["Fractal2D"]


class Fractal2D(FractalABC):
    # default_settings = {
    #     "ANIMATION": False,
    #     "ANIMATION_PARAM": "ZOOM",
    #     "ANIMATION_SPEED": 1,
    #     "HIGH_SCR_QUALITY": False,
    #     "HIGH_VIDEO_QUALITY": False,
    #     "SHADER_SRC": "src/shaders/julia2d.frag",
    # }

    def __init__(
        self,
        fragment_shader_path: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._max_iter = 100
        self._fragment_shader_path = fragment_shader_path
        self._offset = QPointF(0.0, 0.0)
        self._zoom_factor = 1.0
        self._color = QColor(255, 255, 255, 255)
        self._central_lines = False
        self._enable_AA = False
        self._rotation_angle = 0.0

        self._last_mouse_pos = self._current_mouse_pos

    @property
    def max_iter(self) -> int:
        return self._max_iter

    @max_iter.setter
    def max_iter(self, new_value: int) -> None:
        self._max_iter = new_value
        self.update()

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

    @property
    def antialiasing(self) -> bool:
        return self._enable_AA

    @antialiasing.setter
    def antialiasing(self, new_value: bool) -> None:
        self._enable_AA = new_value
        self.update()

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, new_value: QColor) -> None:
        self._color = new_value
        self.update()

    def fractal_controls(self) -> list[Any]:
        return [
            ColoredButton(name="Choose color", color=get_color("blue"), handlers=[self._show_color_picker]),
            NamedSlider(
                name="Iterations Limit",
                scope=(0, 500),
                initial=self.max_iter,
                handlers=[lambda value: use_setter(self, "max_iter", value)],
            ),
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
            NamedCheckBox(
                name="Antialiasing",
                initial=self.antialiasing,
                handlers=[lambda value: use_setter(self, "antialiasing", value)],
            ),
        ]

    # animation_params = {
    #     "ZOOM": (lambda x, sp: x ** (1.01**sp)),
    #     "PHI": (lambda x, sp: x + 0.001 * sp),
    #     "ARG_C": (lambda x, sp: x + 0.02 * sp),
    #     "ABS_C": (lambda x, sp: x + 0.02 * sp),
    # }

    def motion_controls(self) -> list[Any]:
        return []

    def _show_color_picker(self) -> None:
        picker = QColorDialog(self)
        picker.setStyleSheet("QSpinBox { min-width: 50px; max-width: 50px; }")
        picker.setCurrentColor(self.color)
        picker.currentColorChanged.connect(lambda color: use_setter(self, "color", color))
        picker.exec()

    def _fragment_shader_code(self) -> str:
        with open(self._fragment_shader_path) as fragment_shader_file:
            return fragment_shader_file.read()

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

    # def setup_ui(self):
    #     super().setup_ui()

    # # New items
    # ...

    # self._setup_status_bar()

    def _translate_point(self, point: QPointF) -> QPointF:
        """Translates widget's point to fractal's point"""

        point -= QPointF(self.width(), self.height()) / 2
        point = rotate_point(point, self.rotation_angle, self.offset)

        factor = 2 / min(self.width(), self.height()) / self.zoom_factor

        point *= factor
        point.setY(-point.y())

        return point
