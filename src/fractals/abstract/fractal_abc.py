from abc import ABC, ABCMeta, abstractmethod
from math import ceil
from typing import Any

import numpy as np
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader
from PySide6.QtCore import QPoint
from PySide6.QtGui import QCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QSizePolicy

__all__ = ["FractalABC"]


class _ABCQOpenGLWidgetMeta(type(QOpenGLWidget), ABCMeta):
    pass


class FractalABC(ABC, QOpenGLWidget, metaclass=_ABCQOpenGLWidgetMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    @abstractmethod
    def paintGL(self) -> None:
        pass

    def resizeGL(self, w, h) -> None:
        self.update()

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fractal_controls(self) -> list[Any]:
        pass

    @abstractmethod
    def motion_controls(self) -> list[Any]:
        pass

    @abstractmethod
    def _fragment_shader_code(self) -> str:
        pass

    def initializeGL(self) -> None:
        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0], dtype=np.float32)
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(vao)

        # VERTEX BUFFER OBJECT
        # Buffer with vertex coordinates
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # ELEMENT BUFFER OBJECT
        # Buffer with vertex order
        ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

        # Initialize shaders
        with open("res/shaders/vertex_shader.glsl") as vertex_shader_file:
            vertex_shader = compileShader(vertex_shader_file.read(), gl.GL_VERTEX_SHADER)
        fragment_shader = compileShader(self._fragment_shader_code(), gl.GL_FRAGMENT_SHADER)

        self._program = compileProgram(vertex_shader, fragment_shader)
        gl.glUseProgram(self._program)

        # Data binding
        in_shader_pos = gl.glGetAttribLocation(self._program, "vertex_position")
        gl.glEnableVertexAttribArray(in_shader_pos)
        gl.glVertexAttribPointer(
            in_shader_pos,
            2,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            vertices.itemsize * 2,
            gl.ctypes.c_void_p(0),
        )

    @property
    def _current_mouse_pos(self) -> QPoint:
        return self.mapFromGlobal(QCursor().pos())

    @property
    def _widget_size(self) -> tuple[int, int]:
        width = ceil(self.width() * self.devicePixelRatio())
        height = ceil(self.height() * self.devicePixelRatio())
        return (width, height)
