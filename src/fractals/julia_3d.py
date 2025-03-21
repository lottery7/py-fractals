import json
from math import cos, pi, sin
from typing import Any

import OpenGL.GL as gl
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from frontend.components import NamedCheckBox, NamedSlider
from util import use_setter

from .abstract import (
    AAFractal,
    BGColorableFractal,
    ColorableFractal,
    Fractal3D,
    IterableFractal,
    StatefulFractal,
)


class Julia3D(StatefulFractal, AAFractal, IterableFractal, ColorableFractal, BGColorableFractal, Fractal3D):
    def __init__(self, name: str, fragment_shader_path: str, *args, **kwargs):
        super().__init__(7, name, fragment_shader_path, *args, **kwargs)

        self._abs_c = 0.8776
        self._argx_c = 2.0
        self._argy_c = 2.67
        self._cut = False
        self._shadows = True
        self._depth = 400
        self._ao = 120
        self._power = 7
        self._rotate_y = 0.0

    @property
    def abs_c(self) -> float:
        return self._abs_c

    @abs_c.setter
    def abs_c(self, new_value: float) -> None:
        self._abs_c = new_value
        self.update()

    @property
    def argx_c(self) -> float:
        return self._argx_c

    @argx_c.setter
    def argx_c(self, new_value: float) -> None:
        self._argx_c = new_value
        self.update()

    @property
    def argy_c(self) -> float:
        return self._argy_c

    @argy_c.setter
    def argy_c(self, new_value: float) -> None:
        self._argy_c = new_value
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

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, new_value: int) -> None:
        self._power = new_value
        self.update()

    @property
    def rotate_y(self) -> float:
        return self._rotate_y

    @rotate_y.setter
    def rotate_y(self, new_value: float) -> None:
        self._rotate_y = new_value
        self.update()

    def fractal_controls(self) -> list[Any]:
        return (
            StatefulFractal.fractal_controls(self)
            + Fractal3D.fractal_controls(self)
            + ColorableFractal.fractal_controls(self)
            + BGColorableFractal.fractal_controls(self)
            + AAFractal.fractal_controls(self)
            + IterableFractal.fractal_controls(self)
            + [
                NamedSlider(
                    name="Abs(C)",
                    scope=(0, 10000),
                    initial=self.abs_c * 5000,
                    handlers=[lambda value: use_setter(self, "abs_c", value / 5000)],
                ),
                NamedSlider(
                    name="ArgX(C)",
                    scope=(0, 2000 * pi),
                    initial=self.argx_c * 1000,
                    handlers=[lambda value: use_setter(self, "argx_c", value / 1000)],
                ),
                NamedSlider(
                    name="ArgY(C)",
                    scope=(0, 2000 * pi),
                    initial=self.argy_c * 1000,
                    handlers=[lambda value: use_setter(self, "argy_c", value / 1000)],
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
                NamedSlider(
                    name="Power",
                    scope=(2, 10),
                    initial=self.power,
                    handlers=[lambda value: use_setter(self, "power", value)],
                ),
                NamedSlider(
                    name="Rotate Y",
                    scope=(0, 10_000),
                    initial=self.rotate_y * 10_000 / (2 * pi),
                    handlers=[lambda value: use_setter(self, "rotate_y", value / 10_000 * 2 * pi)],
                ),
            ]
        )

    def motion_controls(self) -> list[Any]:
        return []

    def paintGL(self) -> None:
        self.makeCurrent()
        gl.glUseProgram(self._program)
        gl.glViewport(0, 0, *self._widget_size)

        location = lambda key: gl.glGetUniformLocation(self._program, key)

        gl.glUniform1i(location("MAX_ITER"), self.max_iter)
        gl.glUniform2f(location("RES"), *self._widget_size)
        gl.glUniform1f(location("PHI"), self.h_angle)
        gl.glUniform1f(location("THETA"), self.v_angle)

        gl.glUniform4f(
            location("COLOR"),
            self.color.redF(),
            self.color.greenF(),
            self.color.blueF(),
            self.color.alphaF(),
        )

        gl.glUniform4f(
            location("BG_COLOR"),
            self.bg_color.redF(),
            self.bg_color.greenF(),
            self.bg_color.blueF(),
            self.bg_color.alphaF(),
        )

        gl.glUniform1f(location("ZOOM"), self.zoom_factor)
        gl.glUniform1f(location("POWER"), float(self.power))
        gl.glUniform1i(location("CUT"), self.cut)
        gl.glUniform3f(location("C"), *self._get_c())
        gl.glUniform1i(location("MAX_STEPS"), self.depth)
        gl.glUniform1f(location("ROTATE_Y"), self.rotate_y)
        gl.glUniform1f(location("AO_COEF"), self.ao)
        gl.glUniform1i(location("SHADOWS"), int(self.shadows))
        gl.glUniform1i(location("AA"), 2 if self.antialiasing else 1)

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

    def _get_c(self):
        a, b, r = self.argx_c, self.argy_c, self.abs_c
        return r * cos(a) * cos(b), r * sin(a) * cos(b), r * sin(b)

    def _save_state(self, filename: str) -> None:
        state = {
            "max_iter": self.max_iter,
            "h_angle": self.h_angle,
            "v_angle": self.v_angle,
            "color": {
                "red": self.color.redF(),
                "green": self.color.greenF(),
                "blue": self.color.blueF(),
                "alpha": self.color.alphaF(),
            },
            "bg_color": {
                "red": self.bg_color.redF(),
                "green": self.bg_color.greenF(),
                "blue": self.bg_color.blueF(),
                "alpha": self.bg_color.alphaF(),
            },
            "zoom_factor": self.zoom_factor,
            "power": self.power,
            "cut": self.cut,
            "abs_c": self.abs_c,
            "argx_c": self.argx_c,
            "argy_c": self.argy_c,
            "depth": self.depth,
            "rotate_y": self.rotate_y,
            "ao": self.ao,
            "shadows": self.shadows,
            "antialiasing": self.antialiasing,
        }
        with open(filename, "w") as f:
            json.dump(state, f)

    def _load_state(self, filename: str) -> None:
        with open(filename, "r") as f:
            state = json.load(f)

        self.max_iter = state["max_iter"]
        self.h_angle = state["h_angle"]
        self.v_angle = state["v_angle"]
        self.color.setRedF(state["color"]["red"])
        self.color.setGreenF(state["color"]["green"])
        self.color.setBlueF(state["color"]["blue"])
        self.color.setAlphaF(state["color"]["alpha"])
        self.bg_color.setRedF(state["bg_color"]["red"])
        self.bg_color.setGreenF(state["bg_color"]["green"])
        self.bg_color.setBlueF(state["bg_color"]["blue"])
        self.bg_color.setAlphaF(state["bg_color"]["alpha"])
        self.zoom_factor = state["zoom_factor"]
        self.power = state["power"]
        self.cut = state["cut"]
        self.abs_c = state["abs_c"]
        self.argx_c = state["argx_c"]
        self.argy_c = state["argy_c"]
        self.depth = state["depth"]
        self.rotate_y = state["rotate_y"]
        self.ao = state["ao"]
        self.shadows = state["shadows"]
        self.antialiasing = state["antialiasing"]

        self.update()
