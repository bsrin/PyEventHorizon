import numpy as np

class BlackHoleParams:
    def __init__(self):
        # Natural units
        self.M = 1.0
        self.a = 0.9  # Spin parameter (0 <= a < M)
        
        # Derived parameters
        self.r_plus = self.M + np.sqrt(max(self.M**2 - self.a**2, 0.0))
        
        # Approximate ISCO for a=0.9 (prograde)
        self.r_isco = 2.32 * self.M 
        self.r_outer = 20.0 * self.M

        # Accretion Disk Thermodynamics
        self.t_max = 10000.0 # Peak temperature mapping