from copy import deepcopy

from Common import *


class Particle(TrackableObject, ABC):
    REST_MASS = 0
    CHARGE = 0
    PARTICLETYPE = ''

    @classmethod
    def getRestMass(cls):
        return cls.REST_MASS

    @classmethod
    def getCharge(cls):
        return cls.CHARGE

    @classmethod
    def calcGamma(cls, v: np.array):
        # g = 1 / np.sqrt(1 - np.vdot(v, v))
        return 1 / np.sqrt(1 - np.vdot(v, v))

    class Property(TrackableProperty):
        ENERGY = 'Energy', False
        MASS = 'Mass', False
        POS = 'Position', True
        VEL = 'Velocity', True
        ACCEL = 'Acceleration', True
        MOMENTUM = 'Momentum', True
        MOMENTUM_MAG = 'Momentum', False
        ANGMOMENTUM = 'Angular Momentum', True
        GAMMA = 'Gamma Factor', False

    def __init__(self,
                 name = "",
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float),
                 mass = float(0), charge = float(0)):
        self.r = position
        self.v = velocity
        self.a = acceleration
        self.rNext = np.copy(position)
        self.vNext = np.copy(velocity)
        self.aNext = np.copy(acceleration)
        self.m = mass
        self.mNext = mass
        self.gam = float(1)
        self.gamNext = float(1)
        self.q = charge
        self.name = name
        self.ID: int = None
        self.F = np.array([0, 0, 0], float)

    def __lt__(self, other):
        if isinstance(other, Particle):
            return self.name < other.name
        else:
            raise TypeError

    #    def __repr__(self):
    #        return self.name, self.r, self.v, self.a, self.m, self.q

    def __str__(self):
        return self.getFullName() + ' at r = ' + str(self.r) + ' with v = ' + str(self.v) + ', a = ' + str(self.a)

    def getFullName(self):
        return self.name + ' ' + str(self.ID)

    def getTypeName(self):
        return self.__class__.PARTICLETYPE

    def getType(self):
        return type(self)

    # def getFieldIDs(self):
    #    return self.__fieldIDs

    def applyForce(self, force: np.ndarray):
        # print("Force applied! ", force)
        self.F = force

    def update(self, tStep: float, approx: Approximation, relativistic = True):
        vnew = self.v + tStep * self.a
        if relativistic:
            self.gamNext = self.calcGamma(vnew)
            if self.gam > 1.4:
                self.aNext = (self.F - np.vdot(self.F, vnew) * vnew) / (self.m * self.gamNext)
            else:
                self.aNext = self.F / self.m
        else:
            self.aNext = self.F / self.m
        if approx == Approximation.EULER:
            self.rNext += tStep * self.v
            self.vNext += vnew
        elif approx == Approximation.EULER_CROMER:
            self.vNext += vnew
            self.rNext += tStep * self.vNext
        elif approx == Approximation.VERLET:
            self.rNext += tStep * (self.v + 0.5 * tStep * self.a)
            self.vNext += 0.5 * tStep * (self.aNext + self.a)
        else:
            raise TypeError

    def tick(self):
        self.a = self.aNext
        self.v = self.vNext
        self.r = self.rNext
        self.gam = self.gamNext

    def getMomentum(self):
        return self.gam * self.m * self.v

    def getAngMomentum(self):
        return np.cross(self.r, self.getMomentum())

    def getEnergy(self):
        # return 0.5 * self.m * np.vdot(self.v, self.v)  # Temp, non-relativistic
        p = self.getMomentum()
        return np.sqrt(np.vdot(p, p) + self.m ** 2)

    def getProperty(self, p: Property):
        if p is Particle.Property.ENERGY:
            return self.getEnergy()
        if p is Particle.Property.POS:
            return self.r
        if p is Particle.Property.VEL:
            return self.v
        if p is Particle.Property.GAMMA:
            return self.gam
        if p is Particle.Property.ACCEL:
            return self.a
        if p is Particle.Property.MASS:
            return self.m
        if p is Particle.Property.MOMENTUM:
            return self.getMomentum()
        if p is Particle.Property.MOMENTUM_MAG:
            return np.linalg.norm(self.getMomentum())
        if p is Particle.Property.ANGMOMENTUM:
            return self.getAngMomentum()

    def getPosition(self) -> np.ndarray:
        return self.r

    def getVelocity(self) -> np.ndarray:
        return self.v

    def getAcceleration(self) -> np.ndarray:
        return self.a

    def getGamma(self) -> np.ndarray:
        return self.gam

class Proton(Particle):
    REST_MASS = 938  # Temp value
    CHARGE = 1
    PARTICLETYPE = 'Proton'

    def __init__(self,
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float)):
        super(Proton, self).__init__(position = position, velocity = velocity, acceleration = acceleration,
                                     mass = Proton.REST_MASS, charge = Proton.CHARGE)

class Bunch(TrackableObject):
    class Property(TrackableProperty):
        ENERGY = 'Total Energy', False
        MASS = 'Mass', False
        POS = 'Central Position', True
        VEL = 'Average Velocity', True
        GAMMA = 'Average Gamma', False
        ACCEL = 'Average Acceleration', True
        MOMENTUM = 'Total Momentum', True
        # MOMENTUM_MAG = 'Total Momentum (mag)'
        ANGMOMENTUM = 'Total Angular Momentum', True
        AVGENERGY = 'Average Energy', False
        AVGMOMENTUM = 'Average Momentum', True
        AVGANGMOMENTUM = 'Average Angular Momentum', True

    def __init__(self, partType: Type[Particle], N: int,
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float),
                 R = float(0)):
        self.N = N
        self.partType = partType
        part = partType(position = position, velocity = velocity, acceleration = acceleration)
        self.particles: List[Particle] = [part]
        self.ID = None
        for i in range(N - 1):
            self.particles.append(deepcopy(part))

    def getTypeName(self):
        return self.particles[0].getTypeName()

    def getType(self):
        return type(self.particles[0])

    def getMomentum(self):
        mv = np.array([0, 0, 0], float)
        for i in self.particles:
            mv += i.getMomentum()
        return mv

    def getAvgMomentum(self):
        return self.getMomentum() / self.N

    def getAngMomentum(self):
        tau = np.array([0, 0, 0], float)
        for i in self.particles:
            tau += i.getAngMomentum()
        return tau

    def getAvgAngMomentum(self):
        return self.getAngMomentum() / self.N

    def getPosition(self):
        r = np.array([0, 0, 0], float)
        for i in self.particles:
            r += i.r
        return r / self.N

    def getVelocity(self):
        v = np.array([0, 0, 0], float)
        for i in self.particles:
            v += i.v
        return v / self.N

    def getGamma(self):
        g = float(0)
        for i in self.particles:
            g += i.gam
        return g / self.N

    def getAcceleration(self):
        a = np.array([0, 0, 0], float)
        for i in self.particles:
            a += i.a
        return a / self.N

    def getEnergy(self):
        e = 0
        for i in self.particles:
            e += i.getEnergy()
        return e

    def getMass(self):
        m = 0
        for i in self.particles:
            m += i.m
        return m

    def getAvgEnergy(self):
        return self.getEnergy() / self.N

    def __str__(self):
        return self.getFullName() + ' centred at r = ' + str(self.getPosition()) + ' with mv = ' + str(
            self.getMomentum()) + ', E = ' + str(self.getEnergy())

    def getFullName(self):
        return 'Bunch ' + str(self.ID)

    def getProperty(self, p: Property):
        if p is Bunch.Property.ENERGY:
            return self.getEnergy()
        if p is Bunch.Property.POS:
            return self.getPosition()
        if p is Bunch.Property.VEL:
            return self.getVelocity()
        if p is Bunch.Property.GAMMA:
            return self.getGamma()
        if p is Bunch.Property.ACCEL:
            return self.getAcceleration()
        if p is Bunch.Property.MASS:
            return self.getMass()
        if p is Bunch.Property.MOMENTUM:
            return self.getMomentum()
        if p is Bunch.Property.ANGMOMENTUM:
            return self.getAngMomentum()
        if p is Bunch.Property.AVGENERGY:
            return self.getAvgEnergy()
        if p is Bunch.Property.AVGMOMENTUM:
            return self.getAngMomentum()
        if p is Bunch.Property.AVGANGMOMENTUM:
            return self.getAvgAngMomentum()
        else:
            return None
