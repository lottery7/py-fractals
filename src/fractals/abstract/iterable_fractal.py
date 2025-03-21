from frontend.components import NamedSlider
from util import use_setter

from .fractal_abc import FractalABC


class IterableFractal(FractalABC):
    def __init__(self, max_iter: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_iter = max_iter

    @property
    def max_iter(self) -> int:
        return self._max_iter

    @max_iter.setter
    def max_iter(self, new_value: int) -> None:
        self._max_iter = new_value
        self.update()

    def fractal_controls(self):
        return [
            NamedSlider(
                name="Iterations Limit",
                scope=(0, 500),
                initial=self.max_iter,
                handlers=[lambda value: use_setter(self, "max_iter", value)],
            ),
        ]
