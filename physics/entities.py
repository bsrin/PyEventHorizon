import numpy as np

class BinarySuns:
    def __init__(self):
        # Moved much farther away
        self.pos1 = np.array([60.0, 10.0, -50.0], dtype=np.float32)
        self.pos2 = np.array([-60.0, -10.0, 50.0], dtype=np.float32)
        
        # Colors: Orange and Yellow
        self.color1 = np.array([1.0, 0.4, 0.0], dtype=np.float32)
        self.color2 = np.array([1.0, 0.9, 0.2], dtype=np.float32)

    def get_state(self, time):
        return self.pos1, self.pos2