from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import QPushButton

from ..constants import get_qss_color_template


class ColoredButton(QPushButton):
    _QSS_TEMPLATE = get_qss_color_template("QPushButton")

    def __init__(
        self,
        name: str,
        color: QColor,
        handlers: list[Callable],
        *args,
        **kwargs,
    ):
        super().__init__(name, *args, **kwargs)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setColor(color)

        for handler in handlers:
            self.clicked.connect(handler)

    def setColor(self, color: QColor):
        bgColor = color.name(QColor.NameFormat.HexArgb)
        hoverBgColor = QColor(color.red(), color.green(), color.blue(), 60).name(QColor.NameFormat.HexArgb)
        pressedBgColor = QColor(color.red(), color.green(), color.blue(), 90).name(QColor.NameFormat.HexArgb)

        self.setStyleSheet(
            self._QSS_TEMPLATE.format(
                bgColor=bgColor,
                hoverBgColor=hoverBgColor,
                pressedBgColor=pressedBgColor,
            )
        )
