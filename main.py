# Author: bsrin
import glfw
from engine.window import Window
from engine.shader import Shader
from engine.camera import Camera
from engine.fbo import PingPongFBO
from physics.params import BlackHoleParams
from physics.entities import BinarySuns
from OpenGL.GL import *
import numpy as np

def main():
    WIDTH, HEIGHT = 1280, 720
    window = Window(WIDTH, HEIGHT, "Project EventHorizon - Kerr Black Hole")
    
    params = BlackHoleParams()
    suns = BinarySuns()
    camera = Camera([0.0, 4.0, 25.0])
    
    raytracer = Shader("shaders/quad.vert", "shaders/kerr_raytracer.frag")
    taa = Shader("shaders/quad.vert", "shaders/taa_resolve.frag")
    
    fbo = PingPongFBO(WIDTH, HEIGHT)
    read_idx, write_idx = 0, 1
    
    # fsq (fullscreen quad) setup
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    quad_vertices = np.array([-1,-1, 1,-1, -1,1, 1,1], dtype=np.float32)
    glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

    last_frame, fps_last_time, fps_frame_count = 0.0, 0.0, 0
    first_mouse = True
    last_x, last_y = WIDTH / 2.0, HEIGHT / 2.0

    glfw.set_input_mode(window.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def mouse_callback(win, xpos, ypos):
        nonlocal last_x, last_y, first_mouse
        if first_mouse:
            last_x = xpos; last_y = ypos; first_mouse = False
        xoffset = xpos - last_x
        yoffset = last_y - ypos 
        last_x = xpos; last_y = ypos
        camera.process_mouse(xoffset, yoffset)

    glfw.set_cursor_pos_callback(window.window, mouse_callback)

    while window.is_open():
        current_time = glfw.get_time()
        delta_time = current_time - last_frame
        last_frame = current_time

        fps_frame_count += 1
        if current_time - fps_last_time >= 1.0:
            glfw.set_window_title(window.window, f"Project EventHorizon | FPS: {fps_frame_count}")
            fps_frame_count = 0; fps_last_time = current_time

        # inputs
        camera.is_moving = False
        if glfw.get_key(window.window, glfw.KEY_ESCAPE) == glfw.PRESS: glfw.set_window_should_close(window.window, True)
        if glfw.get_key(window.window, glfw.KEY_W) == glfw.PRESS: camera.process_keyboard("FORWARD", delta_time)
        if glfw.get_key(window.window, glfw.KEY_S) == glfw.PRESS: camera.process_keyboard("BACKWARD", delta_time)
        if glfw.get_key(window.window, glfw.KEY_A) == glfw.PRESS: camera.process_keyboard("LEFT", delta_time)
        if glfw.get_key(window.window, glfw.KEY_D) == glfw.PRESS: camera.process_keyboard("RIGHT", delta_time)
        if getattr(camera, '_mouse_moved', False):
             camera.is_moving = True
             camera._mouse_moved = False

        if window.width != WIDTH or window.height != HEIGHT:
            WIDTH, HEIGHT = window.width, window.height
            fbo.resize(WIDTH, HEIGHT)

        jitter = camera.get_jitter(WIDTH, HEIGHT)

        # pass 1: relativistic raymarch & lighting
        glBindFramebuffer(GL_FRAMEBUFFER, fbo.fbos[write_idx])
        glViewport(0, 0, WIDTH, HEIGHT)
        glClear(GL_COLOR_BUFFER_BIT)
        
        raytracer.use()
        raytracer.set_vec2("u_resolution", WIDTH, HEIGHT)
        raytracer.set_vec2("u_jitter", *jitter)
        raytracer.set_vec3("u_camPos", *camera.position)
        raytracer.set_vec3("u_camForward", *camera.forward)
        raytracer.set_vec3("u_camRight", *camera.right)
        raytracer.set_vec3("u_camUp", *camera.up)
        
        raytracer.set_float("u_a", params.a)
        raytracer.set_float("u_M", params.M)
        
        sun1_p, sun2_p = suns.get_state(current_time)
        raytracer.set_vec3("u_sun1_pos", *sun1_p)
        raytracer.set_vec3("u_sun2_pos", *sun2_p)
        raytracer.set_vec3("u_sun1_color", *suns.color1)
        raytracer.set_vec3("u_sun2_color", *suns.color2)
        
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        # pass 2: temporal anti-aliasing resolve & bloom
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        taa.use()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, fbo.textures[write_idx])
        taa.set_int("u_CurrentFrame", 0)
        
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, fbo.textures[read_idx])
        taa.set_int("u_HistoryBuffer", 1)
        
        taa.set_int("u_is_moving", int(camera.is_moving))
        
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        
        # swap ping-pong history targets
        read_idx, write_idx = write_idx, read_idx
        window.swap_buffers()

    window.terminate()

if __name__ == "__main__":
    main()