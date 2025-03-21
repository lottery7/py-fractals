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
        Julia2D(name="Julia 2D", fragment_shader_path="res/shaders/julia2d.frag"),
        Mandelbrot2D(name="Mandelbrot 2D", fragment_shader_path="res/shaders/mandelbrot2d.frag"),
        BurningShip2D(name="Burning Ship", fragment_shader_path="res/shaders/burningship2d.frag"),
        Mandelbrot3D(name="Mandelbrot 3D Polar", fragment_shader_path="res/shaders/mandelbrot3d.frag"),
        Julia3D(name="Julia 3D Polar", fragment_shader_path="res/shaders/julia3d.frag"),
        Mandelbrot3D(name="Mandelbrot 3D Quaternion", fragment_shader_path="res/shaders/mandelbrot4d.frag"),
        Julia3D(name="Julia 3D Quaternion", fragment_shader_path="res/shaders/julia4d.frag"),
    ]

    window = MainWindow()

    for fractal in fractals:
        window.register_fractal(fractal)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
