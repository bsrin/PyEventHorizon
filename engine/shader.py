from OpenGL.GL import *
import OpenGL.GL.shaders
import sys

class Shader:
    def __init__(self, vertex_path: str, fragment_path: str):
        self.ID = self._compile_program(vertex_path, fragment_path)
        
        # cache uniform locations. querying the gpu every frame is a massive cpu bottleneck.
        self.uniform_cache = {}

    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"CRITICAL: Failed to read shader file {path}.\nError: {e}")
            sys.exit(1)

    def _compile_program(self, vertex_path: str, fragment_path: str):
        vertex_src = self._read_file(vertex_path)
        fragment_src = self._read_file(fragment_path)

        try:
            vertex_shader = OpenGL.GL.shaders.compileShader(vertex_src, GL_VERTEX_SHADER)
            fragment_shader = OpenGL.GL.shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER)
            program = OpenGL.GL.shaders.compileProgram(vertex_shader, fragment_shader)
            return program
        except OpenGL.GL.shaders.ShaderCompilationError as e:
            print(f"CRITICAL: Shader Compilation Failed in {vertex_path} or {fragment_path}!")
            print(e)
            sys.exit(1)

    def use(self):
        glUseProgram(self.ID)

    def _get_location(self, name: str) -> int:
        if name not in self.uniform_cache:
            loc = glGetUniformLocation(self.ID, name)
            self.uniform_cache[name] = loc
        return self.uniform_cache[name]

    # pushing python math to glsl
    def set_int(self, name: str, value: int):
        glUniform1i(self._get_location(name), value)

    def set_float(self, name: str, value: float):
        glUniform1f(self._get_location(name), value)

    def set_vec2(self, name: str, x: float, y: float):
        glUniform2f(self._get_location(name), x, y)

    def set_vec3(self, name: str, x: float, y: float, z: float):
        glUniform3f(self._get_location(name), x, y, z)