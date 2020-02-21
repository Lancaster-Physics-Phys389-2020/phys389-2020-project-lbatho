import numpy as np


class Particle:

    x : np.array
    v : np.array
    a : np.array
    m : float
    q : float

    def __init__(self,
                 position = np.array([0,0,0], float),
                 velocity = np.array([0,0,0], float),
                 acceleration = np.array([0,0,0], float),
                 mass = 0, charge = 0):
        self.x = position
        self.v = velocity
        self.a = acceleration
        self.m = mass
        self.q = charge

