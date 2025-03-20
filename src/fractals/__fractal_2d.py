import copy
import glob
import os
from datetime import datetime
from math import cos, sin

import ffmpeg
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import *


class Fractal2D(QOpenGLWidget):
    def __init__(
        self,
        window: QMainWindow,
        opengl_layout: QLayout,
        buttons_layout: QLayout,
        object_name: str = "Fractal_Object",
        settings: dict = None,
        *args,
    ):
        super().__init__(parent=window)

        # Установка непереданных в момент создания объекта настроек.
        # default_settings должены быть определены в наследующем класс.
        if settings is None:
            settings = copy.deepcopy(self.default_settings)
        else:
            for key, value in self.default_settings.items():
                if key not in settings:
                    settings[key] = copy.deepcopy(value)

        # Словарь с настройкми.
        self.settings = settings

        # Код вершинного шейдера (устанавливает прямоугольную область).
        self.vertex_shader_code = """
        #version 120
        attribute vec2 vertex_position;
        void main() {
            gl_Position = vec4(vertex_position, 0, 1);
        }"""

        # Код фрагментного шейдера.
        with open(self.settings["SHADER_SRC"], encoding="utf8") as file:
            self.fragment_shader_code = file.readlines()

        self.program = None
        self.setObjectName(object_name)
        self.installEventFilter(self)
        self.window = window
        opengl_layout.addWidget(self)

        self._interface_widget = QWidget()
        self._interface_widget.setLayout(QGridLayout())
        buttons_layout.addWidget(self._interface_widget)
        self.interface = self._interface_widget.layout()

        # Виджет панели управления анимацией.
        self._anim_panel_widget = QWidget()
        self._anim_panel_widget.setLayout(QGridLayout())
        self.window.lay_anim.addWidget(self._anim_panel_widget)
        self.anim_panel = self._anim_panel_widget.layout()

        self._anim_param_end_value = QLabel()
        self._anim_progress_bar = QProgressBar()
        self._anim_progress_bar.setMaximum(100)
        self._anim_progress_bar.setVisible(False)

        self.animation_length = 0

        self._status_dict = {}
        self.status = ""

        self.mouse_position = QPoint(0, 0)

        # Добавление кнопок.
        self.setup_ui()

        # Добавляем текущий объект в указанное окно.
        self.window.add_object(self)

        self.draw = False

    def add_button(self, title, func, color="black", pos=None):
        """Добавляет кнопку в интерфейс текущего объекта. \n
        :param title: название кнопки.
        :param func: функция, выполняемая при нажатии.
        :param pos: позиция (по умолчанию добавляется в конец).
        :param color: цвет.
        """
        Button(self, self.interface, title, func, color, pos)

    def add_check_box(self, title, arg_name, pos=None):
        """Добавляет кнопку вкл/выкл в интерфейс текущего объекта. \n
        :param title: название кнопки.
        :param arg_name: название изменяемого аргумента (должен быть в self.settings).
        :param pos: позиция (по умолчанию добавляется в конец).
        """
        CheckBox(self, self.interface, title, arg_name, pos)

    def add_slider(self, title, slider_type, func, scope, start_value, pos=None):
        """Добавляет слайдер в интерфейс текущего объекта.
        :param title: название слайдера (текст над слайдером).
        :param slider_type: тип слайдера (вертикальный / горизонтальный)
        :param func: фукнция, в которую передаётся значение со слайдера.
        :param scope: отрезок значений.
        :param start_value: начальное значение.
        :param pos: позиция (по умолчанию добавляется в конец).
        :return: None
        """
        if pos is None:  # Позиция не указана, добавляет в конец.
            self.interface.addWidget(QLabel(title))
            Slider(self, slider_type, func, self.interface, scope, start_value)
        else:  # Добавляет в указанное место.
            self.interface.addWidget(QLabel(title), *pos)
            Slider(
                self,
                slider_type,
                func,
                self.interface,
                scope,
                start_value,
                (pos[0] + 1, pos[1]),
            )

    def add_status(self, title, text_form="{0}", unpack=False):
        """Добавляет переменную в статус. \n
        :param title: имя переменной из настроек.
        :param text_form: формат записи переменной в строке.
        :param unpack: аспаковывать или нет (массив или нет) (по умолчанию нет).
        :return: None
        """
        self._status_dict[title] = (text_form, unpack)

    def paintEvent(self, QPaintEvent):
        if self.draw:
            self.paintGL()
        self.draw = False
        pass

    def resizeGL(self, w, h):
        self.draw = True
        glViewport(0, 0, w, h)

    def state_changed(self):
        self.draw = True

    def eventFilter(self, source, event):
        """Обрабатывает нажатия."""
        # Движение мыши.
        if event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.LeftButton:
                self.draw = True
                oldPos = self.mouse_position
                newPos = self._rotate_point(self._get_mouse_position())
                difference = newPos - oldPos
                self._change_offset(-difference.x(), -difference.y(), True, True)
                self.mouse_position = newPos

        # Нажатие кнопки мыши.
        elif event.type() == QEvent.MouseButtonPress:
            if event.buttons() == Qt.LeftButton:
                self.mouse_position = self._rotate_point(self._get_mouse_position())
                self.setCursor(QCursor(Qt.ClosedHandCursor))

            elif event.buttons() == Qt.RightButton:
                # Меняем местоположение на то, куда нажали.
                p = self._get_mouse_position()
                self._change_offset(p.x(), p.y(), True, True, True, True)
                self.draw = True

        # Отпускание кнопки мыши.
        elif event.type() == QEvent.MouseButtonRelease:
            self.unsetCursor()

        # Прокрутка колёсика мыши.
        elif event.type() == QEvent.Wheel:
            self.draw = True
            self.change_parameter("ZOOM", self.settings["ZOOM"] * 1.1 ** (event.angleDelta().y() / 100))

        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Escape:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Info")
                dlg.setIcon(QMessageBox.Question)
                yes_btn = dlg.addButton(QMessageBox.Yes)
                dlg.addButton(QMessageBox.Cancel)
                dlg.setText(f"Are you sure you want to exit?")
                dlg.setStyleSheet(
                    """QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                                            width: 300px; min-width:300px; max-width:300px;}"""
                )
                dlg.exec()
                if dlg.clickedButton() == yes_btn:
                    quit(-1)

        else:
            return False

        return True

    def initializeGL(self):
        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0], dtype=np.float32)
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        # VERTEX BUFFER OBJECT
        # Буффер, в котором лежат координаты вершин.
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # ELEMENT BUFFER OBJECT
        # Буффер, в котором записан порядок вершин.
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # Компиляция вершинного и фрагментного шейдеров.
        vertex_shader = compileShader(self.vertex_shader_code, GL_VERTEX_SHADER)
        fragment_shader = compileShader(self.fragment_shader_code, GL_FRAGMENT_SHADER)

        # Инициализация шейдерной программы.
        self.program = compileProgram(vertex_shader, fragment_shader)
        glUseProgram(self.program)

        # Передача вершин.
        in_shader_pos = glGetAttribLocation(self.program, "vertex_position")
        glEnableVertexAttribArray(in_shader_pos)
        glVertexAttribPointer(
            in_shader_pos,
            2,
            GL_FLOAT,
            GL_FALSE,
            vertices.itemsize * 2,
            ctypes.c_void_p(0),
        )

    def set_visible(self, choice: bool):
        """Включение/выключение объекта."""
        super().setVisible(choice)
        if choice:
            self.setFocus()
            self.update_status_bar()
        else:
            self.window.statusBar.clearMessage()

        self._interface_widget.setVisible(choice)
        self._anim_panel_widget.setVisible(choice)

    def update_frame(self):
        """Обновляет кадр."""
        if self.settings["ANIMATION"]:
            self.animate()
        current = self.settings["ANIMATION_PARAM"]
        value = self.settings[current]
        for i in range(self.animation_length * 60):
            value = self.animation_params[current](value, self.settings["ANIMATION_SPEED"])
        self._anim_param_end_value.setText(f"End value: {value:.3e}")
        self.update_status_bar()
        self.update()

    def animate(self):
        """Изменяет параметры для отображения анимации."""
        self.draw = True
        current = self.settings["ANIMATION_PARAM"]
        self.settings[current] = self.animation_params[current](
            self.settings[current], self.settings["ANIMATION_SPEED"]
        )

    def _change_offset(self, x, y, difference=False, scale=True, centerize=False, rotate=False):
        """Изменяет текущее местоположение на изображении.
        :param x: новая абсцисса.
        :param y: новая ордината.
        :param difference: абсолютное или относительное изменение местоположения.
        :param scale: масштабировать или нет.
        :param centerize: центрировать или нет.
        :param rotate: поворачивать или нет.
        """
        if scale:
            x, y = self._get_scaled_points(x, y, centerize, rotate)

        if difference:
            self.settings["OFFSET"][0] += x
            self.settings["OFFSET"][1] += y
        else:
            self.settings["OFFSET"] = [x, y]

    def change_parameter(self, param: str, value, difference: bool = False):
        if difference:
            if len(value) > 1:
                for ind, val in enumerate(value):
                    self.settings[param][ind] += value[ind]
            else:
                self.settings[param] += value
        else:
            self.settings[param] = value

    def _color_picker(self, key):
        def __change_color(self, key, color: QColor):
            self.settings[key] = color.getRgbF()
            self.draw = True

        picker = QColorDialog(self)
        picker.setStyleSheet("QSpinBox { min-width: 50px; max-width: 50px; }")
        r, g, b, a = self.settings[key]
        current_color = QColor(r * 255, g * 255, b * 255, a * 255)
        picker.setCurrentColor(current_color)
        picker.currentColorChanged.connect(lambda: __change_color(self, key, picker.currentColor()))
        if not picker.exec():
            self.settings[key] = current_color.getRgbF()

    def _get_mouse_position(self):
        xy = self.mapFromGlobal(QCursor().pos())
        return xy

    def _get_scaled_points(self, x, y, centerize=True, rotate=True):
        if centerize:
            x -= self.width() / 2
            y -= self.height() / 2
        if rotate:
            xy = self._rotate_point(QPoint(x, y))
            x, y = xy.x(), xy.y()

        x *= 2 / min(self.width(), self.height()) / self.settings["ZOOM"]
        y *= -2 / min(self.width(), self.height()) / self.settings["ZOOM"]

        return x, y

    def _rotate_point(self, p: QPoint, clock_wise=True):
        x1, y1 = p.x(), p.y()
        pi = 3.141592654
        x0, y0 = self.settings["OFFSET"]
        c = cos(pi * self.settings["PHI"])
        s = sin(pi * self.settings["PHI"])
        if clock_wise:
            x = (x1 - x0) * c - (y1 - y0) * s
            y = (x1 - x0) * s + (y1 - y0) * c
        else:
            x = (x1 - x0) * c - (y1 - y0) * s
            y = (x1 - x0) * s + (y1 - y0) * c
        try:
            return QPoint(x, y)
        except Exception as e:
            print(e)
            return p

    def save_position(self):
        with open("res/doc/positions.txt", "a") as file:
            text = "; ".join(
                [
                    f'{self.settings["OFFSET"][0]}',
                    f'{self.settings["OFFSET"][1]}',
                    f'{self.settings["ZOOM"]}',
                ]
            )
            file.write(text + "\n")

    def save_video(self):
        self._anim_progress_bar.setVisible(True)
        old_size = self.size()
        if self.settings["HIGH_VIDEO_QUALITY"]:
            self.resize(2560, 1440)

        for i in range(round(self.animation_length * 60 + 60)):
            if self.animation_length * 60 + 30 >= i >= 30:
                self.animate()
            scr = self.grabFramebuffer()
            scr.save(f"res/tmp/image{i:08d}.jpg", "jpg")
            self._anim_progress_bar.setValue(round(i / (self.animation_length + 1) / 60 * 100))

        self.resize(old_size)

        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        try:
            stream = ffmpeg.input("res/tmp/image%08d.jpg", framerate=60)
            stream = ffmpeg.output(stream, f"res/video/animation_{date}.mp4", video_bitrate="20000k")
            ffmpeg.run(stream)
        except Exception:
            error_dialog = QErrorMessage()
            error_dialog.showMessage("ffmpeg error. Try to reinstall ffmpeg.")

        for file in glob.glob("res/tmp/*"):
            os.remove(file)

        self._anim_progress_bar.setValue(0)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Info")
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(f"Animation is saved.")
        dlg.setDetailedText("PATH: res/video/animation_" + date + ".mp4")
        dlg.setStyleSheet(
            """QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                            width: 300px; min-width:300px; max-width:300px;}"""
        )
        dlg.exec()

        self._anim_progress_bar.setVisible(False)

    def input_position(self):
        text, ok = QInputDialog.getText(self, "Position", "Enter x; y; z:")
        if ok:
            text = text.split(";")
            for i in range(3):
                if not text[i]:
                    continue
                val = float(text[i])
                if i == 0:
                    self.settings["OFFSET"][0] = val
                elif i == 1:
                    self.settings["OFFSET"][1] = val
                else:
                    self.settings["ZOOM"] = val

    def setup_ui(self):
        self.add_button("Object color", lambda: self._color_picker("COLOR"), color="black")
        self.add_button("Screenshot", self.take_screenshot, color="black")
        self.add_button("Save position", self.save_position)
        self.add_button("Input position", self.input_position)
        self.add_check_box("Anti-aliasing", "AA")
        self.add_check_box("High screenshot quality", "HIGH_SCR_QUALITY")

        CheckBox(self, self.anim_panel, "High video quality", "HIGH_VIDEO_QUALITY", None)
        CheckBox(self, self.anim_panel, "Real-time", "ANIMATION", None)
        Button(self, self.anim_panel, "Save animation", self.save_video, "black")

        self._anim_param_end_value.setText("DIE")
        self.anim_panel.addWidget(self._anim_param_end_value)
        self.anim_panel.addWidget(self._anim_progress_bar)

    def take_screenshot(self):
        date = datetime.now().strftime("%Y-%m2d-%d_%H-%M-%S.jpg")
        path = f"res/screenshots/screenshot_{date}"
        self.resize(self.width() + self.width() % 2, self.height() + self.height() % 2)

        old_size = self.size()
        if self.settings["HIGH_SCR_QUALITY"]:
            self.resize(2560, 1440)

        scr = self.grabFramebuffer()
        scr.save(path, "jpg")

        self.resize(old_size)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Info")
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(f"Screenshot is saved.")
        dlg.setDetailedText("PATH:\n" + path + "\n")
        dlg.setStyleSheet(
            """QLabel{height: 30px; min-height: 30px; max-height: 30px;
                                    width: 300px; min-width:300px; max-width:300px;}"""
        )
        dlg.exec()

    def update_status_bar(self):
        status_list = []
        for key, value in self._status_dict.items():
            form, unpack = value
            val = self.settings[key]
            if unpack:
                status_list.append(form.format(*val))
            else:
                status_list.append(form.format(val))
        self.status = " ".join(status_list)
        self.window.statusBar.showMessage(self.status)
