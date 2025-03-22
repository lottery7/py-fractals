from abc import ABC, ABCMeta, abstractmethod
from math import ceil
from typing import Any

from PySide6.QtCore import QPoint
from PySide6.QtGui import QCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSizePolicy

__all__ = ["FractalABC"]


class _ABCQOpenGLWidgetMeta(type(QOpenGLWidget), ABCMeta):
    pass


class FractalABC(ABC, QOpenGLWidget, metaclass=_ABCQOpenGLWidgetMeta):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._name = name

    @abstractmethod
    def fractal_controls(self) -> list[Any]:
        pass

    @abstractmethod
    def animation_controls(self) -> list[Any]:
        pass

    @abstractmethod
    def paintGL(self) -> None:
        pass

    @abstractmethod
    def initializeGL(self) -> None:
        pass

    def resizeGL(self, w, h) -> None:
        self.update()

    @property
    def _current_mouse_pos(self) -> QPoint:
        return self.mapFromGlobal(QCursor().pos())

    @property
    def _widget_size(self) -> tuple[int, int]:
        pixel_ratio = self.window().devicePixelRatio()
        width = ceil(self.width() * pixel_ratio)
        height = ceil(self.height() * pixel_ratio)
        return (width, height)

    @property
    def name(self) -> str:
        return self._name
