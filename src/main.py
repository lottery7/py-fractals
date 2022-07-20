import sys

from Fractals import *
from PyQt5.QtWidgets import QApplication
from Window import Window

def main():
    """ Главная функция.
        Что делает:
         1. Запускает программу.
         2. Инициализирует стандартные объекты.
         3. Указывает начальные параметры.
    """

    # Инициализация программы.
    # Должна производиться ДО инициализации объектов.
    app = QApplication(sys.argv)
    GUI = Window()

    # Кортеж, хранящий все переменные интерфейса, необходимые для
    # инициализации объектов.
    window_set = (GUI, GUI.lay_canvas, GUI.lay_settings)

    # Инициализация объектов.
    # Передаваемые параметры указаны внутри соответствующего класса.
    Mandelbrot2D(*window_set, object_name="Mandelbrot2D")
    Julia2D(*window_set, object_name="Julia2D")
    BurningShip2D(*window_set, object_name="BurningShip2D")
    Mandelbrot3D(*window_set, object_name="Mandelbrot3D")
    Julia3D(*window_set, object_name="Julia3D")
    Mandelbrot4D(*window_set, object_name="Mandelbrot4D")
    Julia4D(*window_set, object_name="Julia4D")
    Mandelbox(*window_set, object_name="Explorer3D")

    # Запуск окна программы.
    GUI.show()

    # Запуск программы.
    app.exec()


if __name__ == "__main__":
    main()
