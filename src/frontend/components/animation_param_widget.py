from typing import Callable

from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from .named_check_box import NamedCheckBox
from .named_spin_box import NamedSpinBox


class AnimationParameterWidget(QWidget):
    def __init__(
        self,
        name: str,
        initial: float,
        check_handlers: list[Callable],
        start_handlers: list[Callable],
        end_handlers: list[Callable],
        step: float = 0.1,
        scope: tuple[float, float] = (-100000, 100000),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._use = NamedCheckBox(
            name=name,
            initial=False,
            handlers=[self._update_enabled_state] + check_handlers,
        )

        for handler in check_handlers:
            handler(False)

        self._start_spin_box = NamedSpinBox(
            name="Start Value",
            scope=scope,
            step=step,
            initial=initial,
            handlers=start_handlers,
        )

        for handler in start_handlers:
            handler(initial)

        self._end_spin_box = NamedSpinBox(
            name="End Value",
            scope=scope,
            step=step,
            initial=initial,
            handlers=end_handlers,
        )

        for handler in end_handlers:
            handler(initial)

        layout = QVBoxLayout()
        layout.addWidget(self._use)
        layout.addWidget(self._start_spin_box)
        layout.addWidget(self._end_spin_box)
        layout.setContentsMargins(0, 0, 0, 0)

        self._frame = QFrame()
        self._frame.setObjectName("motionParamWidgetFrame")
        self._frame.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._frame)

        self.setLayout(main_layout)

        self._update_enabled_state(False)

    def _update_enabled_state(self, enable: bool) -> None:
        self._start_spin_box.setEnabled(enable)
        self._end_spin_box.setEnabled(enable)
