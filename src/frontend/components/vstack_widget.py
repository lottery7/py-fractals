from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class VStackWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def add(self, widget: QWidget) -> None:
        self.layout().addWidget(widget)

    def add_all(self, widgets: list[QWidget]) -> None:
        for widget in widgets:
            self.add(widget)

    def clear(self) -> None:
        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
