from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog

from frontend.components import ColoredButton
from frontend.constants import get_color
from util import use_setter

from .fractal_abc import FractalABC


class BGColorableFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bg_color = QColor(45, 45, 45, 255)

    @property
    def bg_color(self) -> QColor:
        return self._bg_color

    @bg_color.setter
    def bg_color(self, new_value: QColor) -> None:
        self._bg_color = new_value
        self.update()

    def fractal_controls(self):
        return [
            ColoredButton(
                name="Choose BG Color",
                color=get_color("blue"),
                handlers=[self._show_bg_color_picker],
            ),
        ]

    def _show_bg_color_picker(self) -> None:
        picker = QColorDialog(self)
        picker.setStyleSheet("QSpinBox { min-width: 50px; max-width: 50px; }")
        picker.setCurrentColor(self.bg_color)
        picker.currentColorChanged.connect(lambda color: use_setter(self, "bg_color", color))
        picker.exec()
