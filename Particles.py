import numpy as np
from Simulations import Simulation, Approximation
from Fields import ParticleEField


class Particle:

    def __init__(self,
                 sim: Simulation,
                 name = "",
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float),
                 mass = 0, charge = 0):
        self.r = position
        self.v = velocity
        self.a = acceleration
        self.m = mass
        self.q = charge
        self.__parentSim = sim
        self.name = name
        self.__partID = sim.addParticle(self)
        self.__fields = []
        self.__fieldIDs = []
        if charge != 0:
            self.__fields.append(ParticleEField(self))
        for f in self.__fields:
            self.__fieldIDs.append(f.getID())

    def __repr__(self):
        return self.name, self.r, self.v, self.a, self.m, self.q

    def __str__(self):
        return str(self.name + 'at r =' + self.x + 'with v =' + self.v + ', a = ')

    def __copy__(self):
        pass

    def getFieldIDs(self):
        return self.__fieldIDs

    def update(self):
        tStep = self.__parentSim.tStep
        approx = self.__parentSim.approx
        aNext = self.__parentSim.getAccel(self)
        if approx == Approximation.EULER:
            self.rNext += tStep * self.v
            self.vNext += tStep * self.a
        elif approx == Approximation.EULER_CROMER:
            self.vNext += tStep * self.a
            self.rNext += tStep * self.vNext
        elif approx == Approximation.VERLET:
            self.rNext += tStep * (self.v + 0.5*tStep * self.a)
            self.v += 0.5*tStep*(aNext + self.a)
        else:
            raise TypeError

        def tick(self):
            self.a = self.aNext
            self.v = self.vNext
            self.r = self.rNext


class Proton(Particle):

    mass = 938 # Temp value
    charge = 1

    def __init__(self,
                 sim : Simulation,
                 position = np.array([0, 0, 0]),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float)):
        super(Proton, self).__init__(sim, 'Proton', position, velocity, acceleration, Proton.mass, Proton.charge)

