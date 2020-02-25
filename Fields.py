from abc import ABC, abstractmethod

import numpy as np
import scipy.constants as const
from Particles import Particle
from Simulations import Simulation


class Field(ABC):

    def __init__(self, sim : Simulation, name = ""):
        self.name = name
        self.id = sim.addField(self)

    @abstractmethod
    def getVector(self, point: np.array) -> np.array:
        pass

    @abstractmethod
    def getForce(self, p : Particle) -> np.array:
        pass

    @abstractmethod
    def getPotentialEnergy(self, p : Particle) -> float:
        pass

    @abstractmethod
    def update(self):
        pass


class UniformField(ABC, Field):

    def __init__(self, sim : Simulation, name = "", fieldVector = np.array([0, 0, 0], float)):
        super(UniformField, self).__init__(sim, name)
        self.fieldVector = fieldVector

    def getVector(self, point: np.array):
        return self.fieldVector


class ConstantField(ABC, Field):

    def update(self):
        return


class BField(ABC, Field):

    def getForce(self, p : Particle):
        return p.q * np.cross(p.v, self.getVector(p.x))

    def getPotentialEnergy(self, p : Particle):
        pass


class ConstantUniformBField(UniformField, ConstantField, BField):

    pass


class EField(ABC, Field):

    nor = 1 / (4*const.pi*const.epsilon_0)

    def getForce(self, p : Particle):
        return p.q * self.getVector(self, p.x)

    def getPotentialEnergy(self, p : Particle):
        return


class ParticleField(ABC, Field):

    def __init__(self, source : Particle, name = ""):
        super(ParticleField, self).__init__(source.getSim(), name)
        self.source = source


class ParticleEField(ParticleField, EField):

    def getVector(self, point: np.array):
        r = point - self.source.x
        r2 = np.vdot(r, r)
        rhat = r / np.sqrt(r2)
        return self.source.q * rhat / r2

    def update(self):
        return