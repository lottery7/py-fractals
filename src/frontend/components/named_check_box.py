from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget


class NamedCheckBox(QWidget):
    def __init__(
        self,
        name: str,
        initial: bool,
        handlers: list[Callable],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.label = QLabel(name)

        self.check_box = QCheckBox()
        self.check_box.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.check_box.setChecked(initial)

        for handler in handlers:
            self.check_box.stateChanged.connect(handler)

        layout = QHBoxLayout()
        layout.addWidget(self.check_box)
        layout.addWidget(self.label)
        layout.setStretch(1, 1)

        self.setLayout(layout)
