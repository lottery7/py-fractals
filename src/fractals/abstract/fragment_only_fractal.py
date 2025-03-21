from abc import abstractmethod

import numpy as np
import OpenGL.GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader

from .fractal_abc import FractalABC


class FragmentOnlyFractal(FractalABC):
    def __init__(self, fragment_shader_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fragment_shader_path = fragment_shader_path

    def _fragment_shader_code(self) -> str:
        with open(self._fragment_shader_path) as fragment_shader_file:
            return fragment_shader_file.read()

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
