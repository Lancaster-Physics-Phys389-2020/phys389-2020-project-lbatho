from copy import copy
import textwrap
import matplotlib.pyplot as plt

from Common import *
from Fields import *
from Particles import *


class Simulation(ABC):

    def __init__(self, approx : Approximation, name : str, tStep = 1, printStep = 1, timeLength = 1):
        self.approx = approx
        self.name = name
        #self.log = Log(type(self).__name__)
        self.tickLength = int(timeLength / tStep) + 1
        self.tStep = tStep
        self.tickPrint = int(printStep / tStep)
        self.currentTick = 0
        self.nextID = (0, 0) # index 0 for particles, index 1 for fields
        self.particles = []
        self.fields = []
        self.xList = []
        self.yList = []
        self.zList = []
        self.running = False

    @abstractmethod
    def start(self):
        pass

#    def addParticles(self, part : Particle, n = 1):
#        ids = []
#        for i in range(n):
#            p = copy(part)
#            j = len(self.particles)
#            p.ID = j
#            self.particles.append(p)
#            log('Adding ' + p.name + ' with ID ' + str(j), MsgType.ENV)
#            ids.append(j)
#        return ids

    def addParticle(self, p : Particle):
        j = len(self.particles)
        p.ID = j
        self.particles.append(p)
        log('Adding ' + p.name + ' with ID ' + str(j), MsgType.ENV)
        return j

    def addBunch(self, b : Bunch):
        ids = []
        log('Adding bunch of ' + str(b.N) + ' particles:', MsgType.ENV)
        log.indent()
        for p in b.particles:
            ids.append(self.addParticle(p))
        log.unindent()
        return ids

    def addField(self, f : Field):
        j = len(self.fields)
        f.ID = j
        self.fields.append(f)
        return j

    def getCurrentTime(self):
        return self.currentTick * self.tStep

    def getAccel(self, part : Particle):
        return self.getForce(part) / part.m

    def getForce(self, part : Particle):
        totalF = np.array([0, 0, 0], float)
#        ex = part.getFields()
        for f in self.fields:
 #          if f not in ex:
            totalF += f.getForce(part)
        return totalF

    def tick(self):
        for f in self.fields:
            f.update()
        for p in self.particles:
            p.applyForce(self.getForce(p))
            p.update(self.tStep, self.approx)
            if self.currentTick % self.tickPrint == 0:
                log('Time:', self.getCurrentTime())
                log(p)
            self.xList[p.ID].append(p.r[0])
            self.yList[p.ID].append(p.r[1])
        for p in self.particles:
            p.tick()
        self.currentTick += 1


class SingleProtonSimulation(Simulation):

    def __init__(self, approx : Approximation, tStep = float(1), printStep = float(1), timeLength = 1):
        super(SingleProtonSimulation, self).__init__(approx, 'Single Proton in Constant Uniform B-Field', tStep, printStep, timeLength)
        self.addField(ConstantUniformBField(fieldVector = np.array([0, 0, 1000], float)))
        self.pro = Proton(velocity = np.array([1, 0, 0], float))
        b = Bunch(self.pro, N = 10)
        self.addBunch(b)
        for p in self.particles:
            self.xList.append([])
            self.yList.append([])

    def start(self):
        for i in range(self.tickLength):
            self.tick()
        print(self.xList)
        plt.plot(self.xList[0], self.yList[0])
        plt.show()