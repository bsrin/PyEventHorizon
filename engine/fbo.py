from OpenGL.GL import *

class PingPongFBO:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # 0: history, 1: current, 2: flare/post
        self.fbos = [glGenFramebuffers(1), glGenFramebuffers(1), glGenFramebuffers(1)]
        self.textures = [glGenTextures(1), glGenTextures(1), glGenTextures(1)]

        for i in range(3):
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[i])
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
            
            # strictly using 32-bit floats. 8-bit clamps the HDR sun math and ruins the bloom.
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.textures[i], 0)
            
            if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
                print(f"CRITICAL: FBO {i} is not complete!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def resize(self, width, height):
        self.width = width
        self.height = height
        for i in range(3):
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None)