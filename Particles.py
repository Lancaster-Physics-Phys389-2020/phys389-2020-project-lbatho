from copy import deepcopy

from Common import *


class Particle(Trackable, ABC):

    REST_MASS = 0
    CHARGE = 0
    PARTICLETYPE = ''

    @classmethod
    def getRestMass(cls):
        return cls.REST_MASS

    @classmethod
    def getCharge(cls):
        return cls.CHARGE

    class Property(TrackableProperty):
        ENERGY = 'Energy', False
        MASS = 'Mass', False
        POS = 'Position', True
        VEL = 'Velocity', True
        ACCEL = 'Acceleration', True
        MOMENTUM = 'Momentum', True
        ANGMOMENTUM = 'Angular Momentum', True

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
        self.q = charge
        self.name = name
        self.ID: int = None

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

    def getAngMomentum(self):
        return np.cross(self.r, self.getMomentum())

    def getEnergy(self):
        return 0.5*self.m*np.vdot(self.v, self.v) # Temp, non-relativistic

    def getProperty(self, p: Property):
        if p is Particle.Property.ENERGY:
            return self.getEnergy()
        if p is Particle.Property.POS:
            return self.r
        if p is Particle.Property.VEL:
            return self.v
        if p is Particle.Property.ACCEL:
            return self.a
        if p is Particle.Property.MASS:
            return self.m
        if p is Particle.Property.MOMENTUM:
            return self.getMomentum()
        if p is Particle.Property.ANGMOMENTUM:
            return self.getAngMomentum()


class Proton(Particle):

    REST_MASS = 938 # Temp value
    CHARGE = 1
    PARTICLETYPE = 'Proton'

    def __init__(self,
                 position = np.array([0, 0, 0], float),
                 velocity = np.array([0, 0, 0], float),
                 acceleration = np.array([0, 0, 0], float)):
        super(Proton, self).__init__(position = position, velocity = velocity, acceleration = acceleration,
                                     mass = Proton.REST_MASS, charge = Proton.CHARGE)


class Bunch(Trackable):

    class Property(TrackableProperty):
        ENERGY = 'Total Energy', False
        MASS = 'Mass', False
        POS = 'Central Position', True
        VEL = 'Average Velocity', True
        ACCEL = 'Average Acceleration', True
        MOMENTUM = 'Total Momentum', True
       # MOMENTUM_MAG = 'Total Momentum (mag)'
        ANGMOMENTUM = 'Total Angular Momentum', True
        AVGENERGY = 'Average Energy', False
        AVGMOMENTUM = 'Average Momentum', True
        AVGANGMOMENTUM = 'Average Angular Momentum', True

    def __init__(self, partType: Type[Particle], N: int,
                 position = np.array([0,0,0], float),
                 velocity = np.array([0,0,0], float),
                 acceleration = np.array([0,0,0], float),
                 R = float(0)):
        self.N = N
        self.partType = partType
        part = partType(position = position, velocity = velocity, acceleration = acceleration)
        self.particles: List[Particle] = [part]
        self.ID = None
        for i in range(N-1):
            self.particles.append(deepcopy(part))

    def getTypeName(self):
        return self.particles[0].getTypeName()

    def getMomentum(self):
        mv = np.array([0, 0, 0], float)
        for i in self.particles:
            mv += i.getMomentum()
        return mv

    def getAvgMomentum(self):
        return self.getMomentum()/self.N

    def getAngMomentum(self):
        tau = np.array([0, 0, 0], float)
        for i in self.particles:
            tau += i.getAngMomentum()
        return tau

    def getAvgAngMomentum(self):
        return self.getAngMomentum()/self.N

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

    def getMass(self):
        m = 0
        for i in self.particles:
            m += i.getMass()
        return m

    def getAvgEnergy(self):
        return self.getEnergy()/self.N

    def __str__(self):
        return self.getFullName() + ' centred at r = ' + str(self.getAvgPosition()) + ' with mv = ' + str(self.getMomentum()) + ', E = ' + str(self.getEnergy())

    def getFullName(self):
        return 'Bunch ' + str(self.ID)

    def getProperty(self, p: Property):
        if p is Bunch.Property.ENERGY:
            return self.getEnergy()
        if p is Bunch.Property.POS:
            return self.getAvgPosition()
        if p is Bunch.Property.VEL:
            return self.getAvgVelocity()
        if p is Bunch.Property.ACCEL:
            return self.getAvgAcceleration()
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
