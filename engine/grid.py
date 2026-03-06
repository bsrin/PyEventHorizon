from OpenGL.GL import *
import numpy as np

class Grid:
    def __init__(self):
        # Create a large ground plane grid
        size = 100
        vertices = []
        for i in range(-size, size + 1):
            vertices.extend([-size, -8.0, i, size, -8.0, i]) # Lines along X
            vertices.extend([i, -8.0, -size, i, -8.0, size]) # Lines along Z
        
        self.vertices = np.array(vertices, dtype=np.float32)
        self.count = len(self.vertices) // 3
        
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindVertexArray(0)

    def draw(self, shader, cam_pos, forward, right, up, proj_view):
        shader.use()
        # Pass a simple projection matrix or just use a standard view setup
        # For simplicity, pass the camera vectors so the grid feels anchored
        shader.set_vec3("u_camPos", *cam_pos)
        shader.set_vec3("u_camForward", *forward)
        shader.set_vec3("u_camRight", *right)
        shader.set_vec3("u_camUp", *up)
        
        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINES, 0, self.count)