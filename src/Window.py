import time
from PyQt5 import uic, QtCore, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtGui import QIcon


class Window(QMainWindow):
    """" Класс окна программы. """
    def __init__(self, *args):
        super().__init__(*args)
        self.ui = uic.loadUi("res/ui/main_window.ui", self)
        self.current_object = None
        self.previous_object = None
        self.current_object = None
        self.previous_object = None
        self.setWindowIcon(QIcon("res/icon.ico"))

        # Таймер для обновления процесса.
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_window)
        self.timer.start()

        # # Переменные для вычисления количества FPS.
        # self.fps = fps
        # self.start_time = time.time()
        # self.frame_counter = 1

    def add_object(self, object_: QOpenGLWidget):
        """ Добавляет объект. """
        self.cobox_objects.addItem(object_.objectName(), object_)
        if self.current_object is not None:
            self.current_object.setVisible(False)
            self.previous_object = self.current_object
            self.current_object = object_
        else:  # ещё не было добавлено ни одного объекта.
            self.current_object = self.previous_object = object_
        self.__make_object_current()

    @pyqtSlot()
    def update_window(self):
        """ Обновляет изображение в окне. """

        # Выбранный объект делается текущим объектом.
        self.current_object = self.cobox_objects.currentData()
        if self.current_object != self.previous_object:
            self.__make_object_current()

        self.current_object.settings["ANIMATION_PARAM"] = self.cobox_animParam.currentText()
        self.current_object.settings["ANIMATION_SPEED"] = self.spbox_animSpeed.value()
        self.current_object.animation_length = self.spbox_length.value()

        # Обновляется состояние текущего объекта.
        if self.current_object is not None:
            self.current_object.update_frame()

        # # Вычисляется FPS.
        # endTime = time.time()  # Время конца кадра.
        # if endTime - self.start_time > 0.5:
        #     # Обновление значения FPS каждые полсекунды.
        #     self.fps = int(self.frame_counter / (endTime - self.start_time))
        #     self.start_time = endTime
        #     self.frame_counter = 0
        # self.frame_counter += 1

    def __make_object_current(self):
        """ Делает объект в self.current_object текующим объектом. """
        if self.previous_object is not None:
            # Надо выключить предыдущий объект
            self.previous_object.set_visible(False)
        # Включаем текущий объект
        self.current_object.set_visible(True)

        # Меняем доступные виды анимации
        self.cobox_animParam.clear()
        self.cobox_animParam.addItems(self.current_object.animation_params.keys())

        # Предыдущий объект это теперь текущий объект
        self.previous_object = self.current_object
        self.setWindowTitle(self.current_object.objectName())
