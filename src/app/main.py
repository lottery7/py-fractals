import sys

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from fractals import *
from frontend import MainWindow


def main():
    app = QApplication(sys.argv)

    format = QSurfaceFormat()
    format.setVersion(4, 3)
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    fractals = [
        Julia2D(fragment_shader_path="res/shaders/julia2d.frag"),
        Mandelbrot2D(fragment_shader_path="res/shaders/mandelbrot2d.frag"),
        BurningShip2D(fragment_shader_path="res/shaders/burningship2d.frag"),
        Mandelbrot3D(fragment_shader_path="res/shaders/mandelbrot3d.frag"),
    ]

    window = MainWindow()

    for fractal in fractals:
        window.register_fractal(fractal)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
