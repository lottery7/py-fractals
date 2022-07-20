import numpy as np
# import copy

from FractalEngine import *
from OpenGL.GL import *
from math import pi, cos, sin
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QCursor


class BurningShip2D(Fractal2D):
    default_settings = {
        "MAX_ITER": 100,
        "OFFSET": [0, 0],
        "ZOOM": 1,
        "PHI": 0,
        "POWER": 2,
        "COLOR": (1.0, 1.0, 1.0, 1.0),
        "LINES": False,
        "AA": False,
        "ANIMATION": False,
        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_SCR_QUALITY": False,
        "HIGH_VIDEO_QUALITY": False,
        "SHADER_SRC": "src/shaders/burningship2d.frag",
    }

    animation_params = {
        "ZOOM": (lambda x, sp: x*(1.01**sp)),
        "PHI": (lambda x, sp: x + 0.001*sp),
    }

    def paintGL(self):
        self.makeCurrent()

        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())
        glUniform1d(location("ZOOM"), values["ZOOM"])
        glUniform1i(location("DRAW_LINES"), int(values["LINES"]))
        glUniform1f(location("PHI"), values["PHI"])
        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform1f(location("POWER"), values["POWER"])
        glUniform2d(location("OFFSET"), *values["OFFSET"])
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("OFFSET", "POSITION: {0:.16f}, {1:.16f}", unpack=True)
        self.add_status("ZOOM", "ZOOM: {0:.5e}")

    def setup_ui(self):
        super().setup_ui()

        # New items
        self.add_check_box("Lines", "LINES")
        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 10000),
                        self.settings["MAX_ITER"])

        self.add_slider("Rotation", Qt.Horizontal, lambda value: self.change_parameter("PHI", value / 5000),
                        (-5000, 5000), self.settings["PHI"])

        self.add_slider("Power", Qt.Horizontal, lambda value: self.change_parameter("POWER", value), (2, 10),
                        self.settings["POWER"])

        self._setup_status_bar()


class Mandelbrot2D(Fractal2D):
    default_settings = {
        "MAX_ITER": 100,
        "OFFSET": [0, 0],
        "ZOOM": 1,
        "PHI": 0,
        "POWER": 2,
        "COLOR": (1.0, 1.0, 1.0, 1.0),
        "LINES": False,
        "AA": False,
        "PERTURBATION": False,
        "ANIMATION": False,
        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_SCR_QUALITY": False,
        "HIGH_VIDEO_QUALITY": False,
        "SHADER_SRC": "src/shaders/mandelbrot2d.frag",
    }

    animation_params = {
        "ZOOM": (lambda x, sp: x*(1.01**sp)),
        "PHI": (lambda x, sp: x + 0.001*sp),
    }

    perturbation_array = np.array([0]*100000, np.float64)

    def initializeGL(self):
        super().initializeGL()

        SSBO = glGenBuffers(1)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 2, SSBO)
        glBufferData(GL_SHADER_STORAGE_BUFFER, self.perturbation_array.nbytes, self.perturbation_array, GL_DYNAMIC_DRAW)

    def paintGL(self):
        self.makeCurrent()

        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())
        glUniform1d(location("ZOOM"), values["ZOOM"])
        glUniform1i(location("DRAW_LINES"), int(values["LINES"]))
        glUniform1f(location("PHI"), values["PHI"])
        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform1f(location("POWER"), values["POWER"])
        glUniform1i(location("PERTURBATION"), int(values["PERTURBATION"]))
        glUniform2d(location("OFFSET"), *values["OFFSET"])
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        if self.settings["PERTURBATION"]:
            self.get_perturbation_values()
            glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.perturbation_array.nbytes, self.perturbation_array)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("OFFSET", "POSITION: {0:.16f}, {1:.16f}", unpack=True)
        self.add_status("ZOOM", "ZOOM: {0:.5e}")

    def setup_ui(self):
        super().setup_ui()

        # New items
        self.add_check_box("Lines", "LINES")
        self.add_check_box("Perturbation", "PERTURBATION")
        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 10000),
                        self.settings["MAX_ITER"])

        self.add_slider("Rotation", Qt.Horizontal, lambda value: self.change_parameter("PHI", value / 5000),
                        (-5000, 5000), self.settings["PHI"])

        self.add_slider("Power", Qt.Horizontal, lambda value: self.change_parameter("POWER", value), (2, 10),
                        self.settings["POWER"])

        self._setup_status_bar()

    def get_perturbation_values(self):
        n = self.settings["MAX_ITER"]
        self.perturbation_array.fill(5)

        def zsqr(clx) -> list:
            return [clx[0]*clx[0]-clx[1]*clx[1], 2*clx[0]*clx[1]]

        z = [0, 0]
        c = self.settings["OFFSET"]

        i = 0
        while i < n:
            z = zsqr(z)
            z[1] += c[1]
            z[0] += c[0]
            self.perturbation_array[2*i] = z[0]
            self.perturbation_array[2*i+1] = z[1]
            i += 1
            if z[0]*z[0] + z[1]*z[1] >= 512: break


class Julia2D(Fractal2D):
    default_settings = {
        "MAX_ITER": 100,
        "OFFSET": [0, 0],
        "ZOOM": 1,
        "COLOR": (1.0, 1.0, 1.0, 1.0),
        "LINES": False,
        "AA": False,
        "ARG_C": pi,
        "ABS_C": 0.7,
        "PHI": 0,
        "POWER": 2,
        "ANIMATION": False,
        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_SCR_QUALITY": False,
        "HIGH_VIDEO_QUALITY": False,
        "SHADER_SRC": "src/shaders/julia2d.frag",
    }

    animation_params = {
        "ZOOM": (lambda x, sp: x**(1.01**sp)),
        "PHI": (lambda x, sp: x + 0.001*sp),
        "ARG_C": (lambda x, sp: x + 0.02 * sp),
        "ABS_C": (lambda x, sp: x + 0.02 * sp),
    }

    def paintGL(self):
        self.makeCurrent()
        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())

        glUniform1f(location("ZOOM"), values["ZOOM"])
        glUniform1i(location("DRAW_LINES"), int(values["LINES"]))
        glUniform1f(location("PHI"), values["PHI"])
        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform1f(location("POWER"), values["POWER"])
        glUniform2f(location("C"), *self.__get_c_value())
        glUniform2f(location("OFFSET"), *values["OFFSET"])
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("OFFSET", "POSITION: {0:.16f}, {1:.16f}", unpack=True)
        self.add_status("ZOOM", "ZOOM: {0:.5e}")
        self.add_status("ARG_C", "ARG: {0:.2f}")
        self.add_status("ABS_C", "ABS: {0:.4f}")
        self.add_status("POWER", "POWER: {0:.1f}")

    def setup_ui(self):
        super().setup_ui()

        # New items
        self.add_check_box("Lines", "LINES")

        self.add_slider("Abs(C)", Qt.Horizontal, lambda value: self.change_parameter("ABS_C", value / 5000),
                        (0, 10000), self.settings["ABS_C"] * 5000)

        self.add_slider("Arg(C)", Qt.Horizontal, lambda value: self.change_parameter("ARG_C", value / 1000),
                        (0, 2000 * pi), self.settings["ARG_C"] * 1000)
        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 1400),
                        self.settings["MAX_ITER"])

        self.add_slider("Power", Qt.Horizontal, lambda value: self.change_parameter("POWER", value), (2, 10),
                        self.settings["POWER"])

        self.add_slider("Rotation", Qt.Horizontal, lambda value: self.change_parameter("PHI", value / 5000),
                        (-5000, 5000), self.settings["PHI"])

        self._setup_status_bar()

    def __get_c_value(self):
        arg_c = self.settings["ARG_C"]
        abs_c = self.settings["ABS_C"]
        c = (abs_c * cos(arg_c), abs_c * sin(arg_c))
        return c


class Mandelbrot3D(Fractal3D):
    default_settings = {
        "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
        "COLOR": (0.439, 0.1765, 0.1765, 1.0),

        "ZOOM": 2.8,
        "PHI": 4.4,
        "THETA": -0.5,

        "AA": False,
        "HIGH_SCR_QUALITY": False,
        "CUT": False,
        "SHADOWS": True,
        "MAX_ITER": 10,
        "DEPTH": 400,
        "AO": 150,
        "POWER": 9,

        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_VIDEO_QUALITY": False,
        "ANIMATION": False,

        "SHADER_SRC": "src/shaders/mandelbrot3d.frag",

        "ROTATE_Y": 0,
    }

    animation_params = {
        "PHI": (lambda x, sp: x+0.05*sp),
        "THETA": (lambda x, sp: x+0.05*sp),
    }

    def paintGL(self):
        self.makeCurrent()
        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())

        glUniform1f(location("PHI"), values["PHI"])
        glUniform1f(location("THETA"), values["THETA"])

        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform4f(location("BG_COLOR"), *values["BG_COLOR"])
        glUniform1f(location("ZOOM"), values["ZOOM"])
        glUniform1f(location("POWER"), values["POWER"])
        glUniform1i(location("CUT"), values["CUT"])
        glUniform1i(location("MAX_STEPS"), values["DEPTH"])
        glUniform1f(location("ROTATE_Y"), values["ROTATE_Y"])
        glUniform1f(location("AO_COEF"), values["AO"])
        glUniform1i(location("SHADOWS"), int(values["SHADOWS"]))
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("POWER", "POWER: {:}")

    def setup_ui(self):
        self.add_button("BG color", lambda: self._color_picker("BG_COLOR"), color="black")
        super().setup_ui()

        # New items
        self.add_check_box("Cut", "CUT")
        self.add_check_box("Shadows", "SHADOWS")

        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 30),
                        self.settings["MAX_ITER"])

        self.add_slider("Depth", Qt.Horizontal, lambda value: self.change_parameter("DEPTH", value), (1, 400),
                        self.settings["DEPTH"])

        self.add_slider("AO", Qt.Horizontal, lambda value: self.change_parameter("AO", 600 - value), (100, 500),
                        600 - self.settings["AO"])

        self.add_slider("Power", Qt.Horizontal, lambda value: self.change_parameter("POWER", value), (2, 10),
                        self.settings["POWER"])

        self._setup_status_bar()


class Julia3D(Fractal3D):
    default_settings = {
        "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
        "COLOR": (0.439, 0.1765, 0.1765, 1.0),

        "ZOOM": 2.8,
        "PHI": 4,
        "THETA": -0.5,

        "AA": False,
        "HIGH_SCR_QUALITY": False,
        "CUT": False,
        "SHADOWS": True,

        "ABS_C": 0.8776,
        "ARGX_C": 2,
        "ARGY_C": 2.67,

        "MAX_ITER": 7,
        "DEPTH": 400,
        "AO": 120,
        "POWER": 7,
        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_VIDEO_QUALITY": False,
        "ANIMATION": False,

        "SHADER_SRC": "src/shaders/julia3d.frag",

        "ROTATE_Y": 0,
    }

    animation_params = {
        "PHI": (lambda x, sp: x+0.05*sp),
        "THETA": (lambda x, sp: x+0.05*sp),
        "ABS_C": (lambda x, sp: x+0.1*sp),
        "ARGX_C": (lambda x, sp: x+0.1*sp),
        "ARGY_C": (lambda x, sp: x+0.1*sp),
    }

    def paintGL(self):
        self.makeCurrent()
        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())
        glUniform1f(location("PHI"), values["PHI"])
        glUniform1f(location("THETA"), values["THETA"])
        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform4f(location("BG_COLOR"), *values["BG_COLOR"])
        glUniform1f(location("ZOOM"), values["ZOOM"])
        glUniform1f(location("POWER"), values["POWER"])
        glUniform1i(location("CUT"), values["CUT"])
        glUniform3f(location("C"), *self.__getC())
        glUniform1i(location("MAX_STEPS"), values["DEPTH"])
        glUniform1f(location("ROTATE_Y"), values["ROTATE_Y"])
        glUniform1f(location("AO_COEF"), values["AO"])
        glUniform1i(location("SHADOWS"), int(values["SHADOWS"]))
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("POWER", "POWER: {:}")
        self.add_status("ARGX_C", "ARG_X: {:.2f}")
        self.add_status("ARGY_C", "ARG_Y: {:.2f}")
        self.add_status("ABS_C", "ABS: {:.4f}")

    def setup_ui(self):
        self.add_button("BG color", lambda: self._color_picker("BG_COLOR"), color="black")
        super().setup_ui()

        # New items
        self.add_check_box("Cut", "CUT")
        self.add_check_box("Shadows", "SHADOWS")

        self.add_slider("Abs(C)", Qt.Horizontal, lambda value: self.change_parameter("ABS_C", value / 5000),
                        (0, 10000), self.settings["ABS_C"] * 5000)

        self.add_slider("ArgX(C)", Qt.Horizontal, lambda value: self.change_parameter("ARGX_C", value / 1000),
                        (0, 2000 * pi), self.settings["ARGX_C"] * 1000)

        self.add_slider("ArgY(C)", Qt.Horizontal, lambda value: self.change_parameter("ARGY_C", value / 1000),
                        (0, 2000 * pi), self.settings["ARGY_C"] * 1000)

        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 30),
                        self.settings["MAX_ITER"])

        self.add_slider("Depth", Qt.Horizontal, lambda value: self.change_parameter("DEPTH", value), (1, 400),
                        self.settings["DEPTH"])

        self.add_slider("AO", Qt.Horizontal, lambda value: self.change_parameter("AO", 600 - value), (100, 500),
                        600 - self.settings["AO"])

        self.add_slider("Power", Qt.Horizontal, lambda value: self.change_parameter("POWER", value), (2, 10),
                        self.settings["POWER"])

        self._setup_status_bar()

    def __getC(self):
        a, b, r = self.settings["ARGX_C"], self.settings["ARGY_C"], self.settings["ABS_C"]
        return r * cos(a)*cos(b), r * sin(a)*cos(b), r * sin(b)


class Mandelbrot4D(Mandelbrot3D):
    default_settings = {
        "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
        "COLOR": (0.439, 0.1765, 0.1765, 1.0),

        "ZOOM": 3,
        "PHI": -0.8,
        "THETA": -0.2,

        "AA": False,
        "HIGH_SCR_QUALITY": False,
        "CUT": False,
        "SHADOWS": True,
        "MAX_ITER": 21,
        "DEPTH": 400,
        "AO": 250,
        "POWER": 2,

        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_VIDEO_QUALITY": False,
        "ANIMATION": False,

        "SHADER_SRC": "src/shaders/mandelbrot4d.frag",

        "ROTATE_Y": 0,
    }

    animation_params = {
        "PHI": (lambda x, sp: x + 0.05 * sp),
        "THETA": (lambda x, sp: x + 0.05 * sp),
    }


class Julia4D(Julia3D):
    default_settings = {
        "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
        "COLOR": (0.439, 0.1765, 0.1765, 1.0),

        "ZOOM": 2.8,
        "PHI": -0.3,
        "THETA": -0.3,

        "AA": False,
        "HIGH_SCR_QUALITY": False,
        "CUT": False,
        "SHADOWS": True,

        "ABS_C": 0.7626,
        "ARGX_C": 3.3,
        "ARGY_C": 6.28,

        "MAX_ITER": 14,
        "DEPTH": 400,
        "AO": 250,
        "POWER": 2,
        "ANIMATION_PARAM": "ZOOM",
        "ANIMATION_SPEED": 1,
        "HIGH_VIDEO_QUALITY": False,
        "ANIMATION": False,

        "SHADER_SRC": "src/shaders/julia4d.frag",

        "ROTATE_Y": 0,
    }

    animation_params = {
        "PHI": (lambda x, sp: x + 0.05 * sp),
        "THETA": (lambda x, sp: x + 0.05 * sp),
        "ABS_C": (lambda x, sp: x + 0.1 * sp),
        "ARGX_C": (lambda x, sp: x + 0.1 * sp),
        "ARGY_C": (lambda x, sp: x + 0.1 * sp),
    }


class Mandelbox(Fractal3D):
    default_settings = {
        "BG_COLOR": (0.1765, 0.1765, 0.1765, 1.0),
        "COLOR": (1.0, 1.0, 1.0, 1.0),

        "AA": False,
        "HIGH_SCR_QUALITY": False,
        "SHADOWS": False,

        "SPEED": 0.1,
        "PHI": 0,
        "THETA": 0,
        "OFFSET": [0, 0, 50],

        "MAX_ITER": 20,
        "DEPTH": 300,
        "AO": 250,
        "FOLDING": 4.245,
        "SCALE": 2.051,
        "OUT_RAD": 5,
        "IN_RAD": 3.238,

        "ANIMATION_PARAM": "OUT_RAD",
        "ANIMATION_SPEED": 0,
        "HIGH_VIDEO_QUALITY": False,
        "ANIMATION": False,

        "SHADER_SRC": "src/shaders/mandelbox.frag",
    }

    animation_params = {
        "OUT_RAD": (lambda x, sp: x + 0.02*sp),
        "IN_RAD": (lambda x, sp: x + 0.02*sp),
        "FOLDING": (lambda x, sp: x + 0.02*sp),
        "SCALE": (lambda x, sp: x + 0.02*sp),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_dict = {
            "FORWARD": False,
            "BACK": False,
            "LEFT": False,
            "RIGHT": False,
            "UP": False,
            "DOWN": False,
        }
        self.is_moving = False

    def check_move(self):
        if self.move_dict["FORWARD"]:
            self.draw = True
            self.settings["OFFSET"][0] -= self.settings["SPEED"] * sin(self.settings["PHI"]) \
                                          * cos(self.settings["THETA"])
            self.settings["OFFSET"][1] -= self.settings["SPEED"] * -sin(self.settings["THETA"])
            self.settings["OFFSET"][2] -= self.settings["SPEED"] * cos(self.settings["PHI"]) \
                                          * cos(self.settings["THETA"])
        if self.move_dict["BACK"]:
            self.draw = True
            self.settings["OFFSET"][0] += self.settings["SPEED"] * sin(self.settings["PHI"]) \
                                          * cos(self.settings["THETA"])
            self.settings["OFFSET"][1] += self.settings["SPEED"] * -sin(self.settings["THETA"])
            self.settings["OFFSET"][2] += self.settings["SPEED"] * cos(self.settings["PHI"]) \
                                          * cos(self.settings["THETA"])
        if self.move_dict["LEFT"]:
            self.draw = True
            self.settings["OFFSET"][0] -= self.settings["SPEED"] * cos(self.settings["PHI"])
            self.settings["OFFSET"][2] += self.settings["SPEED"] * sin(self.settings["PHI"])

        if self.move_dict["RIGHT"]:
            self.draw = True
            self.settings["OFFSET"][0] += self.settings["SPEED"] * cos(self.settings["PHI"])
            self.settings["OFFSET"][2] -= self.settings["SPEED"] * sin(self.settings["PHI"])

        if self.move_dict["UP"]:
            self.draw = True
            self.settings["OFFSET"][1] += self.settings["SPEED"]

        if self.move_dict["DOWN"]:
            self.draw = True
            self.settings["OFFSET"][1] -= self.settings["SPEED"]

    def update_frame(self):
        self.check_move()
        super().update_frame()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove:
            if self.is_moving:
                self.draw = True
                new_pos = self._get_mouse_position()
                difference = new_pos - self.mouse_position
                self.cursor().setPos(self.window.pos().x() + self.window.width() - self.width() / 2,
                                     self.window.pos().y() + self.window.height() - self.height() / 2)
                self.settings["PHI"] -= difference.x() / 100
                if -pi / 2 < self.settings["THETA"] - difference.y() / 100 < pi / 2:
                    self.settings["THETA"] -= difference.y() / 100

        elif event.type() == QEvent.MouseButtonPress:
            if not self.is_moving:
                self.draw = True
                self.is_moving = True
                self.setFocus()
                self.setCursor(QCursor(Qt.BlankCursor))
                self.setMouseTracking(True)
                self.grabMouse()
                self.cursor().setPos(self.window.pos().x() + self.window.width() - self.width() / 2,
                                     self.window.pos().y() + self.window.height() - self.height() / 2)

            self.mouse_position = self._get_mouse_position()

        elif event.type() == QEvent.Wheel:
            if self.settings["SPEED"] + event.angleDelta().y() / 100000 > 0:
                self.settings["SPEED"] += event.angleDelta().y() / 100000

        elif event.type() == QEvent.KeyPress:
            self.draw = True
            if event.key() == Qt.Key_W and not self.move_dict["FORWARD"]:
                self.move_dict["FORWARD"] = True
            if event.key() == Qt.Key_S and not self.move_dict["BACK"]:
                self.move_dict["BACK"] = True
            if event.key() == Qt.Key_A and not self.move_dict["LEFT"]:
                self.move_dict["LEFT"] = True
            if event.key() == Qt.Key_D and not self.move_dict["RIGHT"]:
                self.move_dict["RIGHT"] = True
            if event.key() == Qt.Key_Space and not self.move_dict["UP"]:
                self.move_dict["UP"] = True
            if event.key() == Qt.Key_Control and not self.move_dict["DOWN"]:
                self.move_dict["DOWN"] = True

        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_W and self.move_dict["FORWARD"]:
                self.move_dict["FORWARD"] = False
            if event.key() == Qt.Key_S and self.move_dict["BACK"]:
                self.move_dict["BACK"] = False
            if event.key() == Qt.Key_A and self.move_dict["LEFT"]:
                self.move_dict["LEFT"] = False
            if event.key() == Qt.Key_D and self.move_dict["RIGHT"]:
                self.move_dict["RIGHT"] = False
            if event.key() == Qt.Key_Space and self.move_dict["UP"]:
                self.move_dict["UP"] = False
            if event.key() == Qt.Key_Control and self.move_dict["DOWN"]:
                self.move_dict["DOWN"] = False
            if event.key() == Qt.Key_Escape:
                if self.is_moving:
                    self.is_moving = False
                    self.setMouseTracking(False)
                    self.releaseMouse()
                    self.unsetCursor()
                    for key in self.move_dict.keys():
                        self.move_dict[key] = False
                else:
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("Info")
                    dlg.setIcon(QMessageBox.Question)
                    yes_btn = dlg.addButton(QMessageBox.Yes)
                    dlg.addButton(QMessageBox.Cancel)
                    dlg.setText(f"Are you sure you want to exit?")
                    dlg.setStyleSheet("""QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                                                width: 300px; min-width:300px; max-width:300px;}""")
                    dlg.exec_()
                    if dlg.clickedButton() == yes_btn:
                        quit(-1)
        else:
            return False
        return True

    def paintGL(self):
        self.makeCurrent()
        values = self.settings
        location = lambda key: glGetUniformLocation(self.program, key)

        glUniform1i(location("MAX_ITER"), values["MAX_ITER"])
        glUniform2f(location("RES"), self.width(), self.height())
        glUniform1f(location("PHI"), values["PHI"])
        glUniform1f(location("THETA"), values["THETA"])
        glUniform3f(location("OFFSET"), *values["OFFSET"])
        glUniform4f(location("BG_COLOR"), *values["BG_COLOR"])
        glUniform4f(location("COLOR"), *values["COLOR"])
        glUniform1i(location("MAX_STEPS"), values["DEPTH"])
        glUniform1f(location("AO_COEF"), values["AO"])
        glUniform1i(location("SHADOWS"), int(values["SHADOWS"]))
        glUniform1f(location("FOLDING"), values["FOLDING"])
        glUniform1f(location("SCALE"), values["SCALE"])
        glUniform1f(location("OUT_RAD"), values["OUT_RAD"])
        glUniform1f(location("IN_RAD"), values["IN_RAD"])
        glUniform1i(location("AA"), int(values["AA"]) + 1)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def save_position(self):
        with open("src/doc/positions.txt", "a") as file:
            text = "; ".join([f'{self.settings["OFFSET"][0]}', f'{self.settings["OFFSET"][1]}',
                              f'{self.settings["OFFSET"][2]}'])
            file.write(text + "\n")

    def input_position(self):
        text, ok = QInputDialog.getText(self, 'Position', 'Enter x; y; z:')
        if ok:
            text = text.split(";")
            for i in range(3):
                if not text[i]: continue
                val = float(text[i])
                if i == 0:
                    self.settings["OFFSET"][0] = val
                elif i == 1:
                    self.settings["OFFSET"][1] = val
                else:
                    self.settings["OFFSET"][2] = val

    def _setup_status_bar(self):
        self.add_status("MAX_ITER", "ITER: {}")
        self.add_status("OFFSET", "POS: {:.2f}; {:.2f}; {:.2f}", unpack=True)
        self.add_status("SPEED", "SPEED: {:.4f}")
        self.add_status("SCALE", "SCALE: {:}")
        self.add_status("FOLDING", "FOLDING: {:}")
        self.add_status("OUT_RAD", "OUT-RAD: {:}")
        self.add_status("IN_RAD", "IN-RAD: {:}")

    def setup_ui(self):
        self.add_button("BG color", lambda: self._color_picker("BG_COLOR"), color="black")
        super().setup_ui()

        # New items
        self.add_check_box("Shadows", "SHADOWS")

        self.add_slider("Iterations", Qt.Horizontal, lambda value: self.change_parameter("MAX_ITER", value), (0, 30),
                        self.settings["MAX_ITER"])

        self.add_slider("Depth", Qt.Horizontal, lambda value: self.change_parameter("DEPTH", value), (1, 400),
                        self.settings["DEPTH"])

        self.add_slider("AO", Qt.Horizontal, lambda value: self.change_parameter("AO", 600 - value), (100, 500),
                        600 - self.settings["AO"])

        self.add_slider("Folding", Qt.Horizontal, lambda value: self.change_parameter("FOLDING", value / 1000),
                        (1, 5000), self.settings["FOLDING"] * 1000)

        self.add_slider("Scale", Qt.Horizontal, lambda value: self.change_parameter("SCALE", value / 1000), (1, 5000),
                        self.settings["SCALE"] * 1000)

        self.add_slider("Out-radius", Qt.Horizontal, lambda value: self.change_parameter("OUT_RAD", value / 1000),
                        (1, 5000), self.settings["OUT_RAD"] * 1000)

        self.add_slider("In-radius", Qt.Horizontal, lambda value: self.change_parameter("IN_RAD", value / 1000),
                        (1, 5000), self.settings["IN_RAD"] * 1000)

        self.add_button("Save position", self.save_position)

        self._setup_status_bar()
