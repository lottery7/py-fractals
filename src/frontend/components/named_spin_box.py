from typing import Callable

from PySide6.QtWidgets import QDoubleSpinBox, QLabel, QVBoxLayout, QWidget


class NamedSpinBox(QWidget):
    def __init__(
        self,
        name: str,
        scope: tuple[float, float],
        step: float,
        initial: float,
        handlers: list[Callable],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.label = QLabel(name)

        self.spin_box = QDoubleSpinBox()
        self.spin_box.setRange(*scope)
        self.spin_box.setSingleStep(step)
        self.spin_box.setValue(initial)

        for handler in handlers:
            self.spin_box.valueChanged.connect(handler)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spin_box)

        self.setLayout(layout)
