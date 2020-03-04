from copy import copy

import numpy as np

from Common import *


class Particle:

    def __init__(self,
                 name = "",
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float),
                 mass = 0, charge = 0):
        self.r = position
        self.v = velocity
        self.a = acceleration
        self.rNext = np.copy(position)
        self.vNext = np.copy(velocity)
        self.aNext = np.copy(acceleration)
        self.m = mass
        self.q = charge
        self.name = name
        self.ID = None
        #self.__partID = sim.addParticle(self)
        #self.__fields = []
        #self.__fieldIDs = []
        #if charge != 0:
        #    self.__fields.append(ParticleEField(self))
        #for f in self.__fields:
        #    self.__fieldIDs.append(f.getID())

    def __repr__(self):
        return self.name, self.r, self.v, self.a, self.m, self.q

    def __str__(self):
        return self.name + ' ' + str(self.ID) + ' at r = ' + str(self.r) + ' with v = ' + str(self.v) + ', a = ' + str(self.a)

    #def getFieldIDs(self):
    #    return self.__fieldIDs

    def applyForce(self, force : np.array):
        #print("Force applied! ", force)
        self.aNext = force / self.m

    def update(self, tStep, approx):
        if approx == Approximation.EULER:
            self.rNext += tStep * self.v
            self.vNext += tStep * self.a
        elif approx == Approximation.EULER_CROMER:
            self.vNext += tStep * self.a
            self.rNext += tStep * self.vNext
        elif approx == Approximation.VERLET:
            self.rNext += tStep * (self.v + 0.5*tStep * self.a)
            self.vNext += 0.5*tStep*(self.aNext + self.a)
        else:
            raise TypeError

    def tick(self):
        self.a = self.aNext
        self.v = self.vNext
        self.r = self.rNext

    def getMomentum(self):
        return self.m*self.v


class Proton(Particle):

    mass = 938 # Temp value
    charge = 1

    def __init__(self,
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float)):
        super(Proton, self).__init__('Proton', position, velocity, acceleration, Proton.mass, Proton.charge)


class Bunch:

    def __init__(self,
                 part: Particle,
                 N : int,
                 R = float(0)):
        self.N = N
#        n = N**(1/3)
#        spacing = 2*R/n
#        if spacing == 0:
        self.particles = []
        for i in range(N):
            self.particles.append(copy(part))

    def getMomentum(self):
        mv = np.array([0, 0, 0], float)
        for i in self.particles:
            mv += i.getMomentum()
        return mv

    def getAvgMomentum(self):
        return self.getMomentum()/self.N

    def getAvgPosition(self):
        r = np.array([0, 0, 0], float)
        for i in self.particles:
            r += i.r
        return r/self.N

    def getAvgVelocity(self):
        v = np.array([0, 0, 0], float)
        for i in self.particles:
            v += i.v
        return v/self.N

    def getAvgAcceleration(self):
        a = np.array([0, 0, 0], float)
        for i in self.particles:
            a += i.a
        return a/self.N

    def getEnergy(self):
        e = 0
        for i in self.particles:
            e += i.getEnergy()
        return e

    def getAvgEnergy(self):
        return self.getEnergy()/self.N