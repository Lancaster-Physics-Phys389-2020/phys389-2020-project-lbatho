import numpy as np
from Simulations import Simulation


class Particle:

    def __init__(self,
                 sim: Simulation,
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float),
                 mass = 0, charge = 0):
        self.x = position
        self.v = velocity
        self.a = acceleration
        self.m = mass
        self.q = charge
        self.__id = sim.addParticle(self)
        self.__parentSim = sim

    def __repr__(self):
        return "Particle"


class Proton(Particle):

    mass = 938 # Temp value
    charge = 1

    def __init__(self,
                 sim : Simulation,
                 position = np.array([0, 0, 0]),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float)):
        super(Proton, self).__init__(sim, position, velocity, acceleration, Proton.mass, Proton.charge)
