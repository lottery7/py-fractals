from abc import abstractmethod

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFileDialog

from frontend.components import ColoredButton
from frontend.constants import get_color

from .fractal_abc import FractalABC


class StatefulFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def _save_state(self, filename: str) -> None:
        pass

    @abstractmethod
    def _load_state(self, filename: str) -> None:
        pass

    def fractal_controls(self):
        return [
            ColoredButton(
                name="Save State",
                color=get_color("blue"),
                handlers=[self._save_state_dialog],
            ),
            ColoredButton(
                name="Load State",
                color=get_color("green"),
                handlers=[self._load_state_dialog],
            ),
        ]

    def _save_state_dialog(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Save State", "", "JSON Files (*.json)")
        if filename:
            self._save_state(filename)

    def _load_state_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Load State", "", "JSON Files (*.json)")
        if filename:
            self._load_state(filename)
