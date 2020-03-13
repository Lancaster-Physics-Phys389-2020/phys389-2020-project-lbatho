from Common import *
from Particles import Particle


class Field(ABC):

    def __init__(self, name = ""):
        self.name = name
        self.ID = None

    @abstractmethod
    def getVector(self, point: np.array) -> np.array:
        pass

    def getMagnitude(self, point: np.array) -> float:
        return np.linalg.norm(self.getVector(point))

    @abstractmethod
    def getForce(self, p: Particle) -> np.array:
        pass

    @abstractmethod
    def getPotentialEnergy(self, p: Particle) -> float:
        pass

    @abstractmethod
    def update(self):
        pass

    def __str__(self):
        return self.name


class UniformField(Field, ABC):

    def __init__(self, fieldVector: np.array, region: Region = ALL_SPACE, name = ""):
        super(UniformField, self).__init__(name)
        self.fieldVector = fieldVector
        self.region = region

    def getVector(self, point: np.array):
        if self.region.contains(point):
            return self.fieldVector
        else:
            return np.array([0, 0, 0], float)

    def __str__(self):
        return self.name + ' with uniform field vector ' + str(self.fieldVector)


class ConstantField(Field, ABC):

    def update(self):
        return

    def tick(self):
        return


class BField(Field, ABC):

    def getForce(self, p: Particle):
        return p.q * np.cross(p.v, self.getVector(p.r))

    def getPotentialEnergy(self, p: Particle):
        pass


class ConstantUniformBField(UniformField, ConstantField, BField):

    def __init__(self, fieldVector: np.array, region: Region = ALL_SPACE):
        super(ConstantUniformBField, self).__init__(name = 'Constant Uniform B-Field', fieldVector = fieldVector, region = region)


class EField(Field, ABC):
    nor = 1 / (4 * PI * EPSILON0)

    def getForce(self, p: Particle):
        return p.q * self.getVector(p.r)

    @abstractmethod
    def getPotential(self, point: np.array) -> float:
        pass

    def getPotentialEnergy(self, p: Particle):
        return p.q * self.getPotential(p)


class OscillatingField(UniformField, ABC):

    def __init__(self, maxFieldVector: np.array, period: float, tStep: float, region: Region = ALL_SPACE, name = ""):
        super(OscillatingField, self).__init__(fieldVector = maxFieldVector, region = region, name = name)
        self.period = period
        self.tStep = tStep
        self.t = float(0)

    def tick(self):
        if self.t > self.period:
            self.t -= self.period
        else:
            self.t += self.tStep

    @abstractmethod
    def update(self):
        pass

    def __str__(self):
        return self.name + ' with uniform field vector ' + str(self.fieldVector) + ' and period ' + str(self.period)


class StepOscillatingField(OscillatingField, ABC):

    def __init__(self, maxFieldVector: np.array, period: float, tStep: float, region: Region = ALL_SPACE, name = ""):
        super(StepOscillatingField, self).__init__(maxFieldVector = maxFieldVector, period = period,
                                                   tStep = tStep, region = region, name = name)
        print(period)
        self.halfPeriod = period / 2

    def tick(self):
        if self.t > self.halfPeriod:
            self.t -= self.halfPeriod
        else:
            self.t += self.tStep

    def update(self):
        if self.t > self.halfPeriod:
            self.fieldVector = -self.fieldVector


class CyclotronEField(StepOscillatingField, EField):

    @classmethod
    def getResonanceT(cls, partType: Type[Particle], bField: ConstantUniformBField):
        return 2*PI*partType.getRestMass() / (partType.getCharge()*np.linalg.norm(bField.fieldVector))

    def __init__(self, fieldVector: np.array, partType: Type[Particle], bField: ConstantUniformBField,
                 tStep: float, region: Region = ALL_SPACE):
        period = self.getResonanceT(partType = partType, bField = bField)
        super(CyclotronEField, self).__init__(maxFieldVector = fieldVector, period = period,
                                              tStep = tStep, region = region, name = 'Cyclotronic E-Field')

    def getPotential(self, point: np.array):
        pass


class ParticleField(Field, ABC):

    def __init__(self, source: Particle, name = ""):
        super(ParticleField, self).__init__(source.getSim(), name)
        self.source = source


class ParticleEField(ParticleField, EField, ConstantField):

    def getVector(self, point: np.array):
        r = point - self.source.r
        r2 = np.vdot(r, r)
        rhat = r / np.sqrt(r2)
        return self.source.q * rhat / r2

    def getPotential(self, point: np.array):
        r = np.linalg.norm(point - self.source.x)
        return self.source.q / r


class FieldPoint(Trackable):
    class Property(TrackableProperty):
        VECTOR = 'Field vector', True
        # POTENTIAL = 'Potential'

    def __init__(self, f: Field, r: np.array, name: str):
        self.field = f
        self.point = r
        self.name = name

    def getProperty(self, p: Property):
        if p is Field.Property.VECTOR:
            return self.field.getVector(self.point)
        # elif p == Field.Property.POTENTIAL:
        #    return self.field.getPoten
        else:
            return None

    def getFullName(self):
        return self.field.getFullName() + ': ' + self.name
