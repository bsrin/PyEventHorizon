import numpy as np
import math

class Camera:
    def __init__(self, position):
        self.position = np.array(position, dtype=np.float32)
        self.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        self.yaw = -90.0  
        self.pitch = 0.0

        self.speed = 15.0
        self.sensitivity = 0.1
        self.is_moving = False
        
        self.update_camera_vectors()

        # precompute halton sequences for taa sub-pixel jitter. 
        # distributes samples way better than standard random noise over time.
        self.frame_index = 0
        self.halton_base2 = [self._halton(i, 2) for i in range(1, 17)]
        self.halton_base3 = [self._halton(i, 3) for i in range(1, 17)]

    def update_camera_vectors(self):
        front = np.zeros(3, dtype=np.float32)
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.forward = front / np.linalg.norm(front)

        self.right = np.cross(self.forward, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.forward)
        self.up = self.up / np.linalg.norm(self.up)

    def process_keyboard(self, direction, delta_time):
        velocity = self.speed * delta_time
        if direction == "FORWARD": self.position += self.forward * velocity
        if direction == "BACKWARD": self.position -= self.forward * velocity
        if direction == "LEFT": self.position -= self.right * velocity
        if direction == "RIGHT": self.position += self.right * velocity
        self.is_moving = True

    def process_mouse(self, xoffset, yoffset):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        # clamp pitch so the camera doesn't flip over the pole
        if self.pitch > 89.0: self.pitch = 89.0
        if self.pitch < -89.0: self.pitch = -89.0

        self.update_camera_vectors()
        self.is_moving = True

    def _halton(self, index, base):
        f, r = 1.0, 0.0
        while index > 0:
            f = f / base
            r = r + f * (index % base)
            index = int(index / base)
        return r

    def get_jitter(self, width, height):
        # kill jitter instantly when moving, otherwise the taa history smears the screen
        if self.is_moving:
            self.frame_index = 0
            return np.array([0.0, 0.0], dtype=np.float32)
            
        idx = self.frame_index % 16
        jitter_x = (self.halton_base2[idx] - 0.5) / width
        jitter_y = (self.halton_base3[idx] - 0.5) / height
        self.frame_index += 1
        return np.array([jitter_x, jitter_y], dtype=np.float32)