from math import cos, pi, sin
from typing import Any

import OpenGL.GL as gl
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox

from frontend.components import NamedCheckBox, NamedSlider
from util import use_setter

from .abstract import (
    AAFractal,
    BGColorableFractal,
    ColorableFractal,
    Fractal3D,
    IterableFractal,
)


class Mandelbox(AAFractal, IterableFractal, ColorableFractal, BGColorableFractal, Fractal3D):
    def __init__(self, name: str, fragment_shader_path: str, *args, **kwargs):
        super().__init__(20, name, fragment_shader_path, *args, **kwargs)

        self._depth = 300
        self._ao = 250
        self._folding = 4.245
        self._scale = 2.051
        self._out_rad = 5.0
        self._in_rad = 3.238
        self._shadows = False
        self._offset = [0.0, 0.0, 50.0]
        self._speed = 0.1

        self._move_dict = {
            "FORWARD": False,
            "BACK": False,
            "LEFT": False,
            "RIGHT": False,
            "UP": False,
            "DOWN": False,
        }
        self._is_moving = False

        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self.update)

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
    def folding(self) -> float:
        return self._folding

    @folding.setter
    def folding(self, new_value: float) -> None:
        self._folding = new_value
        self.update()

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, new_value: float) -> None:
        self._scale = new_value
        self.update()

    @property
    def out_rad(self) -> float:
        return self._out_rad

    @out_rad.setter
    def out_rad(self, new_value: float) -> None:
        self._out_rad = new_value
        self.update()

    @property
    def in_rad(self) -> float:
        return self._in_rad

    @in_rad.setter
    def in_rad(self, new_value: float) -> None:
        self._in_rad = new_value
        self.update()

    @property
    def shadows(self) -> bool:
        return self._shadows

    @shadows.setter
    def shadows(self, new_value: bool) -> None:
        self._shadows = new_value
        self.update()

    @property
    def offset(self) -> list[float]:
        return self._offset

    @offset.setter
    def offset(self, new_value: list[float]) -> None:
        self._offset = new_value
        self.update()

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, new_value: float) -> None:
        self._speed = new_value
        self.update()

    def do_move(self):
        if self._move_dict["FORWARD"]:
            self._offset[0] -= self._speed * sin(self.h_angle) * cos(self.v_angle)
            self._offset[1] -= self._speed * -sin(self.v_angle)
            self._offset[2] -= self._speed * cos(self.h_angle) * cos(self.v_angle)
        if self._move_dict["BACK"]:
            self._offset[0] += self._speed * sin(self.h_angle) * cos(self.v_angle)
            self._offset[1] += self._speed * -sin(self.v_angle)
            self._offset[2] += self._speed * cos(self.h_angle) * cos(self.v_angle)
        if self._move_dict["LEFT"]:
            self._offset[0] -= self._speed * cos(self.h_angle)
            self._offset[2] += self._speed * sin(self.h_angle)
        if self._move_dict["RIGHT"]:
            self._offset[0] += self._speed * cos(self.h_angle)
            self._offset[2] -= self._speed * sin(self.h_angle)
        if self._move_dict["UP"]:
            self._offset[1] += self._speed
        if self._move_dict["DOWN"]:
            self._offset[1] -= self._speed

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_moving:
            new_pos = self._current_mouse_pos
            difference = new_pos - self.mouse_position
            self.cursor().setPos(
                self.window().pos().x() + self.window().width() - self.width() / 2,
                self.window().pos().y() + self.window().height() - self.height() / 2,
            )
            self.h_angle -= difference.x() / 100
            if -pi / 2 < self.v_angle - difference.y() / 100 < pi / 2:
                self.v_angle -= difference.y() / 100

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._is_moving:
            self._is_moving = True
            self._update_timer.start(16)
            self.setFocus()
            QApplication.setOverrideCursor(Qt.CursorShape.BlankCursor)
            self.setMouseTracking(True)
            self.grabMouse()
            self.grabKeyboard()
            self.cursor().setPos(
                self.window().pos().x() + self.window().width() - self.width() / 2,
                self.window().pos().y() + self.window().height() - self.height() / 2,
            )
            self.mouse_position = self._current_mouse_pos

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._speed + event.angleDelta().y() / 100000 > 0:
            self._speed += event.angleDelta().y() / 100000

    def keyPressEvent(self, event: QKeyEvent) -> None:
        match (event.key()):
            case Qt.Key.Key_W:
                self._move_dict["FORWARD"] = True
            case Qt.Key.Key_S:
                self._move_dict["BACK"] = True
            case Qt.Key.Key_A:
                self._move_dict["LEFT"] = True
            case Qt.Key.Key_D:
                self._move_dict["RIGHT"] = True
            case Qt.Key.Key_Shift:
                self._move_dict["UP"] = True
            case Qt.Key.Key_Control:
                self._move_dict["DOWN"] = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if self._is_moving:
            match (event.key()):
                case Qt.Key.Key_W:
                    self._move_dict["FORWARD"] = False
                case Qt.Key.Key_S:
                    self._move_dict["BACK"] = False
                case Qt.Key.Key_A:
                    self._move_dict["LEFT"] = False
                case Qt.Key.Key_D:
                    self._move_dict["RIGHT"] = False
                case Qt.Key.Key_Shift:
                    self._move_dict["UP"] = False
                case Qt.Key.Key_Control:
                    self._move_dict["DOWN"] = False
                case Qt.Key.Key_Escape:
                    self.releaseKeyboard()
                    self._is_moving = False
                    self._update_timer.stop()

                    self.setMouseTracking(False)
                    self.releaseMouse()
                    QApplication.restoreOverrideCursor()
                    for key in self._move_dict.keys():
                        self._move_dict[key] = False

    def paintGL(self):
        self.do_move()

        self.makeCurrent()
        gl.glUseProgram(self._program)
        gl.glViewport(0, 0, *self._widget_size)

        location = lambda key: gl.glGetUniformLocation(self._program, key)

        gl.glUniform1i(location("MAX_ITER"), self.max_iter)
        gl.glUniform2f(location("RES"), *self._widget_size)
        gl.glUniform1f(location("PHI"), self.h_angle)
        gl.glUniform1f(location("THETA"), self.v_angle)
        gl.glUniform3f(location("OFFSET"), *self.offset)
        gl.glUniform4f(
            location("BG_COLOR"),
            self.bg_color.redF(),
            self.bg_color.greenF(),
            self.bg_color.blueF(),
            self.bg_color.alphaF(),
        )
        gl.glUniform4f(
            location("COLOR"),
            self.color.redF(),
            self.color.greenF(),
            self.color.blueF(),
            self.color.alphaF(),
        )
        gl.glUniform1i(location("MAX_STEPS"), self.depth)
        gl.glUniform1f(location("AO_COEF"), self.ao)
        gl.glUniform1i(location("SHADOWS"), int(self.shadows))
        gl.glUniform1f(location("FOLDING"), self.folding)
        gl.glUniform1f(location("SCALE"), self.scale)
        gl.glUniform1f(location("OUT_RAD"), self.out_rad)
        gl.glUniform1f(location("IN_RAD"), self.in_rad)
        gl.glUniform1i(location("AA"), 2 if self.antialiasing else 1)

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

    def fractal_controls(self) -> list[Any]:
        return (
            Fractal3D.fractal_controls(self)
            + ColorableFractal.fractal_controls(self)
            + BGColorableFractal.fractal_controls(self)
            + AAFractal.fractal_controls(self)
            + IterableFractal.fractal_controls(self)
            + [
                NamedCheckBox(
                    name="Shadows",
                    initial=self._shadows,
                    handlers=[lambda value: use_setter(self, "shadows", value)],
                ),
                NamedSlider(
                    name="Iterations",
                    scope=(0, 30),
                    initial=self.max_iter,
                    handlers=[lambda value: use_setter(self, "max_iter", value)],
                ),
                NamedSlider(
                    name="Depth",
                    scope=(1, 400),
                    initial=self._depth,
                    handlers=[lambda value: use_setter(self, "depth", value)],
                ),
                NamedSlider(
                    name="AO",
                    scope=(100, 500),
                    initial=600 - self._ao,
                    handlers=[lambda value: use_setter(self, "ao", 600 - value)],
                ),
                NamedSlider(
                    name="Folding",
                    scope=(1, 5000),
                    initial=self._folding * 1000,
                    handlers=[lambda value: use_setter(self, "folding", value / 1000)],
                ),
                NamedSlider(
                    name="Scale",
                    scope=(1, 5000),
                    initial=self._scale * 1000,
                    handlers=[lambda value: use_setter(self, "scale", value / 1000)],
                ),
                NamedSlider(
                    name="Out-Radius",
                    scope=(1, 5000),
                    initial=self._out_rad * 1000,
                    handlers=[lambda value: use_setter(self, "out_rad", value / 1000)],
                ),
                NamedSlider(
                    name="In-Radius",
                    scope=(1, 5000),
                    initial=self._in_rad * 1000,
                    handlers=[lambda value: use_setter(self, "in_rad", value / 1000)],
                ),
            ]
        )

    def motion_controls(self) -> list[Any]:
        return []
