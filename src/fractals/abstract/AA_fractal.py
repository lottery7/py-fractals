from typing import Any

from frontend.components import NamedCheckBox
from util import use_setter

from .fractal_abc import FractalABC


class AAFractal(FractalABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enable_AA = False

    @property
    def antialiasing(self) -> bool:
        return self._enable_AA

    @antialiasing.setter
    def antialiasing(self, new_value: bool) -> None:
        self._enable_AA = new_value
        self.update()

    def fractal_controls(self) -> list[Any]:
        return [
            NamedCheckBox(
                name="Antialiasing",
                initial=self.antialiasing,
                handlers=[lambda value: use_setter(self, "antialiasing", value)],
            ),
        ]
