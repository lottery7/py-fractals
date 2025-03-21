from typing import Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QCursor, QMouseEvent, QWheelEvent

from frontend.components import ColoredButton, NamedCheckBox, NamedSlider
from frontend.constants import get_color
from util import rotate_point, use_setter

from .fractal_abc import FractalABC

__all__ = ["Fractal3D"]


class Fractal3D(FractalABC):
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
        return super().fractal_controls() + [
            ColoredButton(
                name="Choose color",
                color=get_color("blue"),
                handlers=[self._show_color_picker],
            ),
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

    def motion_controls(self) -> list[Any]:
        return []

    def _current_state(self) -> dict:
        raise RuntimeError()

    def _load_state(self, state: dict) -> None:
        raise RuntimeError()

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

    def _translate_point(self, point: QPointF) -> QPointF:
        """Translates widget's point to fractal's point"""

        point -= QPointF(self.width(), self.height()) / 2
        point = rotate_point(point, self.rotation_angle, self.offset)

        factor = 2 / min(self.width(), self.height()) / self.zoom_factor

        point *= factor
        point.setY(-point.y())

        return point

    def _show_color_picker(self) -> None:
        picker = QColorDialog(self)
        picker.setStyleSheet("QSpinBox { min-width: 50px; max-width: 50px; }")
        picker.setCurrentColor(self.color)
        picker.currentColorChanged.connect(lambda color: use_setter(self, "color", color))
        picker.exec()

    # def eventFilter(self, source, event):
    #     if event.type() == QEvent.MouseMove:
    #         if event.buttons() == Qt.LeftButton:
    #             self.draw = True
    #             old_pos = self.mouse_position
    #             new_pos = self._get_mouse_position()
    #             difference = new_pos - old_pos
    #             self.settings["PHI"] -= difference.x() / 100
    #             self.settings["THETA"] -= difference.y() / 100
    #             self.mouse_position = new_pos

    #     elif event.type() == QEvent.MouseButtonPress:
    #         if event.buttons() == Qt.LeftButton:
    #             self.mouse_position = self._get_mouse_position()
    #             self.setCursor(QCursor(Qt.ClosedHandCursor))

    #     elif event.type() == QEvent.MouseButtonRelease:
    #         self.unsetCursor()

    #     elif event.type() == QEvent.Wheel:
    #         self.draw = True
    #         self.settings["ZOOM"] /= 1.01 ** (event.angleDelta().y() / 100)
    #     elif event.type() == QEvent.KeyRelease:
    #         if event.key() == Qt.Key_Escape:
    #             dlg = QMessageBox(self)
    #             dlg.setWindowTitle("Info")
    #             dlg.setIcon(QMessageBox.Question)
    #             yes_btn = dlg.addButton(QMessageBox.Yes)
    #             dlg.addButton(QMessageBox.Cancel)
    #             dlg.setText(f"Are you sure you want to exit?")
    #             dlg.setStyleSheet(
    #                 """QLabel{height: 30px; min-height: 30px; max-height: 30px;
    #                                                          width: 300px; min-width:300px; max-width:300px;}"""
    #             )
    #             dlg.exec_()
    #             if dlg.clickedButton() == yes_btn:
    #                 quit(-1)
    #     else:
    #         return False

    #     return True
