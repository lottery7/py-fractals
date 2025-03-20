from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QLabel, QSlider, QVBoxLayout, QWidget


class NamedSlider(QWidget):
    def __init__(
        self,
        name: str,
        scope: tuple[int, int],
        initial: int,
        handlers: list[Callable],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.label = QLabel(name)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider.setMinimum(scope[0])
        self.slider.setMaximum(scope[1])
        self.slider.setValue(initial)

        for handler in handlers:
            self.slider.valueChanged.connect(handler)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)

        self.setLayout(layout)
