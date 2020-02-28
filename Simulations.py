from Common import *
from Fields import *
from Particles import *


class Simulation(ABC):

    def __init__(self, approx : Approximation, name = "", tStep = 1, timeLength = 1):
        self.approx = approx
        self.name = name
        self.tickLength = int(timeLength / tStep) + 1
        self.tStep = tStep
        self.tick = 0
        self.nextID = (0, 0) # index 0 for particles, index 1 for fields
        self.particles = []
        self.fields = []
        self.running = False

    @abstractmethod
    def start(self):
        pass

    def addParticle(self, part : Particle):
        self.particles.append(part)
        return len(self.particles)

    def addField(self, f : Field):
        self.fields.append(f)
        return len(self.fields)

    def getCurrentTime(self):
        return self.tick * self.tStep

    def getAccel(self, part : Particle):
        return self.getForce(part) / part.m

    def getForce(self, part : Particle):
        totalF = np.array([0, 0, 0], float)
#        ex = part.getFields()
        for f in self.fields:
 #          if f not in ex:
            totalF += f.getForce(part)
        return totalF


class SingleProtonSimulation(Simulation):

    def __init__(self, approx : Approximation, tStep = float(1), timeLength = 1):
        super(SingleProtonSimulation, self).__init__(approx, 'Single Proton in Constant Uniform B-Field', tStep, timeLength)
        self.addField(ConstantUniformBField(fieldVector = np.array([0, 0, 1], float)))
        self.pro = Proton(velocity = np.array([1, 0, 0], float))
        self.addParticle(self.pro)

    def start(self):
        for i in range(self.tickLength):
            print(i)
            self.tock()

    def tock(self):
        print(self.getCurrentTime(), self.pro.r)
        for f in self.fields:
            f.update()
        for p in self.particles:
            p.applyForce(self.getForce(p))
            p.update(self.tStep, self.approx)
        for p in self.particles:
            p.tock()