from datetime import datetime

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog

from frontend.components import ColoredButton
from frontend.constants import get_color
from util import use_setter

from .fractal_abc import FractalABC


class ColorableFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = QColor(255, 255, 255, 255)

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, new_value: QColor) -> None:
        self._color = new_value
        self.update()

    def fractal_controls(self):
        return [
            ColoredButton(
                name="Choose color",
                color=get_color("blue"),
                handlers=[self._show_color_picker],
            ),
        ]

    def _show_color_picker(self) -> None:
        picker = QColorDialog(self)
        picker.setStyleSheet("QSpinBox { min-width: 50px; max-width: 50px; }")
        picker.setCurrentColor(self.color)
        picker.currentColorChanged.connect(lambda color: use_setter(self, "color", color))
        picker.exec()
