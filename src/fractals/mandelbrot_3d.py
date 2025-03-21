from math import pi
from typing import Any

import OpenGL.GL as gl
from PySide6.QtGui import QColor

from frontend.components import NamedCheckBox, NamedSlider
from util import use_setter

from .abstract import AAFractal, ColorableFractal, Fractal3D, IterableFractal


class Mandelbrot3D(AAFractal, IterableFractal, ColorableFractal, Fractal3D):
    def __init__(self, fragment_shader_path: str, *args, **kwargs):
        super().__init__(10, fragment_shader_path, *args, **kwargs)

        self._power = 9.0
        self._bg_color = QColor(0, 0, 0)
        self._z_angle = 0.0
        self._cut = False
        self._shadows = True
        self._depth = 400
        self._ao = 150

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, new_value: int) -> None:
        self._power = new_value
        self.update()

    @property
    def z_angle(self) -> float:
        return self._z_angle

    @z_angle.setter
    def z_angle(self, new_value: float) -> None:
        self._z_angle = new_value
        self.update()

    @property
    def cut(self) -> bool:
        return self._cut

    @cut.setter
    def cut(self, new_value: bool) -> None:
        self._cut = new_value
        self.update()

    @property
    def shadows(self) -> bool:
        return self._shadows

    @shadows.setter
    def shadows(self, new_value: bool) -> None:
        self._shadows = new_value
        self.update()

    @property
    def depth(self) -> int:
        return self._depth

    @depth.setter
    def depth(self, new_value: int) -> None:
        self._depth = new_value
        self.update()

    @property
    def ao(self) -> int:
        return self._ao

    @ao.setter
    def ao(self, new_value: int) -> None:
        self._ao = new_value
        self.update()

    def name(self) -> str:
        return "Mandelbrot 3D Polar"

    def fractal_controls(self) -> list[Any]:
        return (
            Fractal3D.fractal_controls(self)
            + ColorableFractal.fractal_controls(self)
            + AAFractal.fractal_controls(self)
            + IterableFractal.fractal_controls(self)
            + [
                NamedSlider(
                    name="Power",
                    scope=(2, 10),
                    initial=self.power,
                    handlers=[lambda value: use_setter(self, "power", value)],
                ),
                NamedSlider(
                    name="Z-Rotation",
                    scope=(0, 10_000),
                    initial=self.z_angle * 10_000 / (2 * pi),
                    handlers=[lambda value: use_setter(self, "z_angle", value / 10_000 * 2 * pi)],
                ),
                NamedCheckBox(
                    name="Cut",
                    initial=self.cut,
                    handlers=[lambda value: use_setter(self, "cut", value)],
                ),
                NamedCheckBox(
                    name="Shadows",
                    initial=self.shadows,
                    handlers=[lambda value: use_setter(self, "shadows", value)],
                ),
                NamedSlider(
                    name="Depth",
                    scope=(1, 400),
                    initial=self.depth,
                    handlers=[lambda value: use_setter(self, "depth", value)],
                ),
                NamedSlider(
                    name="AO",
                    scope=(100, 500),
                    initial=600 - self.ao,
                    handlers=[lambda value: use_setter(self, "ao", 600 - value)],
                ),
            ]
        )

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
        gl.glUniform1f(location("PHI"), self.h_angle)
        gl.glUniform1f(location("THETA"), self.v_angle)

        gl.glUniform4f(
            location("COLOR"),
            self.color.redF(),
            self.color.greenF(),
            self.color.blueF(),
            self.color.alphaF(),
        )

        gl.glUniform1f(location("POWER"), float(self.power))
        gl.glUniform1i(location("AA"), 2 if self.antialiasing else 1)

        gl.glUniform4f(
            location("BG_COLOR"),
            self._bg_color.redF(),
            self._bg_color.greenF(),
            self._bg_color.blueF(),
            self._bg_color.alphaF(),
        )

        gl.glUniform1i(location("CUT"), self.cut)
        gl.glUniform1i(location("MAX_STEPS"), self.depth)

        gl.glUniform1f(location("ROTATE_Y"), self.z_angle)
        gl.glUniform1f(location("AO_COEF"), self.ao)
        gl.glUniform1i(location("SHADOWS"), int(self.shadows))

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)


#          "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
