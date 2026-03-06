import glfw
import sys
from OpenGL.GL import *

class Window:
    def __init__(self, width: int, height: int, title: str):
        if not glfw.init():
            print("CRITICAL: Failed to initialize GLFW.")
            sys.exit(1)

        # need modern gl 4.3 core for the heavy compute shaders. no legacy pipeline.
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        self.width = width
        self.height = height
        self.window = glfw.create_window(width, height, title, None, None)

        if not self.window:
            glfw.terminate()
            print("CRITICAL: Failed to create GLFW window.")
            sys.exit(1)

        glfw.make_context_current(self.window)
        
        # lock to monitor refresh rate (usually 60fps) to prevent screen tearing
        glfw.swap_interval(1) 
        glfw.set_framebuffer_size_callback(self.window, self.on_resize)

    def on_resize(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    def is_open(self) -> bool:
        return not glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def terminate(self):
        glfw.terminate()