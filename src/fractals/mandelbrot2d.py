from math import cos, pi, sin
from typing import Any

import numpy as np
import OpenGL.GL as gl
from PySide6.QtCore import QPointF

from frontend.components import NamedCheckBox, NamedSlider
from util import use_setter

from .abstract.fractal_2d import Fractal2D


class Mandelbrot2D(Fractal2D):
    def __init__(self, fragment_shader_path: str, *args, **kwargs):
        super().__init__(fragment_shader_path, *args, **kwargs)

        self._power = 2.0

        self._perturbation = False
        self._perturbation_array = np.array([0] * 100_000, np.float64)

    def initializeGL(self) -> None:
        super().initializeGL()

        ssbo = gl.glGenBuffers(1)
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 2, ssbo)
        gl.glBufferData(
            gl.GL_SHADER_STORAGE_BUFFER,
            self._perturbation_array.nbytes,
            self._perturbation_array,
            gl.GL_DYNAMIC_DRAW,
        )

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, new_value: int) -> None:
        self._power = new_value
        self.update()

    @property
    def perturbation(self) -> bool:
        return self._perturbation

    @perturbation.setter
    def perturbation(self, new_value: bool) -> None:
        self._perturbation = new_value
        self.update()

    def name(self) -> str:
        return "Mandelbrot 2D"

    def fractal_controls(self) -> list[Any]:
        return super().fractal_controls() + [
            NamedCheckBox(
                name="Use perturbation",
                initial=self.perturbation,
                handlers=[lambda value: use_setter(self, "perturbation", value)],
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

    def _update_perturbation_values(self):
        n = self.max_iter
        self._perturbation_array.fill(5)

        def zsqr(clx) -> list:
            return [clx[0] * clx[0] - clx[1] * clx[1], 2 * clx[0] * clx[1]]

        z = [0, 0]
        c = self.offset

        i = 0
        while i < n:
            z = zsqr(z)
            z[1] += c.y()
            z[0] += c.x()
            self._perturbation_array[2 * i] = z[0]
            self._perturbation_array[2 * i + 1] = z[1]
            i += 1
            if z[0] * z[0] + z[1] * z[1] >= 512:
                break

    def paintGL(self) -> None:
        self.makeCurrent()
        gl.glUseProgram(self._program)
        gl.glViewport(0, 0, *self._widget_size)

        location = lambda key: gl.glGetUniformLocation(self._program, key)

        gl.glUniform1i(location("MAX_ITER"), self.max_iter)
        gl.glUniform2f(location("RES"), *self._widget_size)
        gl.glUniform1d(location("ZOOM"), self.zoom_factor)
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
        gl.glUniform2d(location("OFFSET"), self.offset.x(), self.offset.y())
        gl.glUniform1i(location("AA"), 2 if self.antialiasing else 1)

        gl.glUniform1i(location("PERTURBATION"), int(self.perturbation))

        if self.perturbation:
            self._update_perturbation_values()
            gl.glBufferSubData(
                gl.GL_SHADER_STORAGE_BUFFER,
                0,
                self._perturbation_array.nbytes,
                self._perturbation_array,
            )

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
