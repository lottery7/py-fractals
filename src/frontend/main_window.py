from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QWidget,
)

from fractals.abstract import FractalABC

from .components import VStackWidget


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowTitle("PyFractal")
        self.setWindowIcon(QIcon("res/icons/main_window.ico"))
        with open("res/styles/main_window.qss") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        self._tabs = QTabWidget()
        self._tabs.setMinimumWidth(220)
        self._tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._create_fractal_tab()
        self._fractals = {}

        self._create_animation_tab()

        self._canvas_frame = QFrame()
        self._canvas_frame.setMinimumSize(QSize(480, 480))
        self._canvas_frame.setLayout(QGridLayout())

        central_layout = QHBoxLayout()

        central_layout.addWidget(self._tabs)
        central_layout.addWidget(self._canvas_frame)

        central_layout.setStretch(0, 1)
        central_layout.setStretch(1, 6)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)

    def _set_current_fractal(self, index: int) -> None:
        fractal: FractalABC = self._fractals_list.itemData(index)

        layout: QGridLayout = self._canvas_frame.layout()
        prev = layout.itemAtPosition(0, 0)
        if prev:
            layout.replaceWidget(prev.widget(), fractal)
            prev.widget().setParent(None)
        else:
            layout.addWidget(fractal, 0, 0)

        self._fractal_controls.clear()
        self._fractal_controls.add(self._fractals_list)

        self._fractal_controls.add_all(fractal.fractal_controls())

        self._fractal_controls.layout().addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self._fractal_tab.verticalScrollBar().setValue(0)

        self._animation_controls.clear()
        self._animation_controls.add_all(fractal.animation_controls())

        self._animation_controls.layout().addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        fractal.update()

    def _create_fractal_tab(self) -> None:
        self._fractals_list = QComboBox()
        self._fractals_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._fractals_list.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self._fractals_list.currentIndexChanged.connect(self._set_current_fractal)

        self._fractal_controls = VStackWidget()
        self._fractal_controls.add(self._fractals_list)

        self._fractal_tab = QScrollArea()
        self._fractal_tab.setWidgetResizable(True)
        self._fractal_tab.setWidget(self._fractal_controls)

        self._tabs.addTab(self._fractal_tab, "Fractal")

    def _create_animation_tab(self) -> None:
        self._animation_controls = VStackWidget()

        self._animation_tab = QScrollArea()
        self._animation_tab.setWidgetResizable(True)
        self._animation_tab.setWidget(self._animation_controls)

        self._tabs.addTab(self._animation_tab, "Animation")

    def _get_registered_fractals(self) -> list[FractalABC]:
        return [self._fractals_list.itemData(i) for i in range(self._fractals_list.count())]

    def register_fractal(self, fractal: FractalABC) -> None:
        if fractal.name in map(lambda f: f.name, self._get_registered_fractals()):
            raise RuntimeError(f"Fractal with name {fractal.name()} already registered")

        self._fractals_list.addItem(fractal.name, userData=fractal)
