import numpy as np
from Common import *
from Particles import Particle


class Field(ABC):

    def __init__(self, name = ""):
        self.name = name
        self.ID = None

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


class UniformField(Field):

    def __init__(self, name = "", fieldVector = np.array([0, 0, 0], float)):
        super(UniformField, self).__init__(name)
        self.fieldVector = fieldVector

    def getVector(self, point: np.array):
        return self.fieldVector


class ConstantField(Field):

    def update(self):
        return


class BField(Field):

    def getForce(self, p : Particle):
        return p.q * np.cross(p.v, self.getVector(p.r))

    def getPotentialEnergy(self, p : Particle):
        pass


class ConstantUniformBField(UniformField, ConstantField, BField):

    def __init__(self, fieldVector : np.array):
        super(ConstantUniformBField, self).__init__('Constant Uniform B-Field', fieldVector)

class EField(Field):

    nor = 1 / (4*const.pi*const.epsilon_0)

    def getForce(self, p : Particle):
        return p.q * self.getVector(self, p.r)

    @abstractmethod
    def getPotential(self, point : np.array) -> float:
        pass

    def getPotentialEnergy(self, p : Particle):
        return p.q * self.getPotential(p)


class ParticleField(Field):

    def __init__(self, source : Particle, name = ""):
        super(ParticleField, self).__init__(source.getSim(), name)
        self.source = source


class ParticleEField(ParticleField, EField):

    def getVector(self, point: np.array):
        r = point - self.source.r
        r2 = np.vdot(r, r)
        rhat = r / np.sqrt(r2)
        return self.source.q * rhat / r2

    def getPotential(self, point : np.array):
        r = np.linalg.norm(point - self.source.x)
        return self.source.q / r

    def update(self):
        return
