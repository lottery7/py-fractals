from math import cos, pi, sin
from typing import Any

import OpenGL.GL as gl
from PySide6.QtCore import QPointF

from frontend.components import NamedSlider
from util import use_setter

from .abstract.fractal_2d import Fractal2D


class Julia2D(Fractal2D):
    def __init__(self, fragment_shader_path: str, *args, **kwargs):
        super().__init__(fragment_shader_path, *args, **kwargs)

        self._C_polar = QPointF(pi, 0.7)
        self._power = 2.0

    @property
    def arg_c(self) -> float:
        return self._C_polar.x()

    @arg_c.setter
    def arg_c(self, new_value: float) -> None:
        self._C_polar.setX(new_value)
        self.update()

    @property
    def abs_c(self) -> float:
        return self._C_polar.y()

    @abs_c.setter
    def abs_c(self, new_value: float) -> None:
        self._C_polar.setY(new_value)
        self.update()

    @property
    def cartesian_c(self) -> complex:
        r, a = self.abs_c, self.arg_c
        return complex(r * cos(a), r * sin(a))

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, new_value: int) -> None:
        self._power = new_value
        self.update()

    def name(self) -> str:
        return "Julia 2D"

    def fractal_controls(self) -> list[Any]:
        return super().fractal_controls() + [
            NamedSlider(
                name="Arg(C)",
                scope=(0, 10_000),
                initial=self.arg_c * 5000 / pi,
                handlers=[lambda value: use_setter(self, "arg_c", value / 5000 * pi)],
            ),
            NamedSlider(
                name="Abs(C)",
                scope=(0, 10_000),
                initial=self.abs_c * 5000,
                handlers=[lambda value: use_setter(self, "abs_c", value / 5000)],
            ),
            NamedSlider(
                name="Power",
                scope=(2, 10),
                initial=self.power,
                handlers=[lambda value: use_setter(self, "power", value)],
            ),
        ]

    def motion_controls(self) -> list[Any]:
        return super().motion_controls() + []

    def paintGL(self) -> None:
        self.makeCurrent()
        gl.glUseProgram(self._program)
        gl.glViewport(0, 0, *self._widget_size)

        location = lambda key: gl.glGetUniformLocation(self._program, key)

        gl.glUniform1i(location("MAX_ITER"), self.max_iter)
        gl.glUniform2f(location("RES"), *self._widget_size)
        gl.glUniform1f(location("ZOOM"), self.zoom_factor)
        gl.glUniform1i(location("DRAW_LINES"), int(self.central_lines))
        gl.glUniform1f(location("PHI"), self.rotation_angle)

        gl.glUniform4f(
            location("COLOR"),
            self._color.redF(),
            self._color.greenF(),
            self._color.blueF(),
            self._color.alphaF(),
        )

        gl.glUniform1f(location("POWER"), float(self.power))
        gl.glUniform2f(location("OFFSET"), self.offset.x(), self.offset.y())
        gl.glUniform1i(location("AA"), 2 if self.antialiasing else 1)

        gl.glUniform2f(location("C"), self.cartesian_c.real, self.cartesian_c.imag)

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
