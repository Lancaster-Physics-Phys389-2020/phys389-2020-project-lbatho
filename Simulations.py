from Fields import *
from Particles import *


class Simulation(Trackable, ABC):

    class Property(TrackableProperty):
        TIME = 'Time'
        ENERGY = 'Total Energy'
        MOMENTUM = 'Total Momentum'
        ANGMOMENTUM = 'Total Angular Momentum'

    def __init__(self, approx : Approximation, name : str, tStep: float, timeLength: float, logStep: float = None):
        log('Created new sim: ' + name)
        log.indent()
        log('Approximation ' + approx.value + ', timestep ' + str(tStep) + ', duration ' + str(timeLength))
        self.approx = approx
        self.name = name
        self.simlog = SimLog(self.__class__.__name__)
        self.tickLength = int(timeLength / tStep) + 1
        self.tStep = tStep
        if logStep is None:
            log('No logstep set. Defaulting to timestep.')
            self.tickLog = 1
        else:
            self.tickLog = int(timeLength / logStep)
        self.tickPrint = int(self.tickLength / 20)
        self.currentTick = 0
        self.particles: List[Particle] = []
        self.fields: List[Field] = []
        self.bunches: List[Bunch] = []
        log.unindent()
        self.running = False

    def start(self):
        self.running = True
        self.simlog.start()
        for i in range(self.tickLength):
            self.tick()
        self.post()

    @abstractmethod
    def post(self):
        pass

    def addParticle(self, p: Particle, quiet = False):
        j = len(self.particles)
        p.ID = j
        self.particles.append(p)
        if not quiet:
            log('Adding ' + p.name + ' with ID ' + str(j), ProgramLog.MsgType.ENV)
        return j

    def addBunch(self, b : Bunch):
        ids = []
        j = len(self.bunches)
        b.ID = j
        self.bunches.append(b)
        log('Adding bunch with ID ' + str(j) + ', ' + str(b.N) + ' ' + b.getTypeName() + 's:', ProgramLog.MsgType.ENV)
        log.indent()
        for p in b.particles:
            ids.append(self.addParticle(p, True))
        l = len(ids)
        log('Added ' + str(l) + ' particles with IDs in range: (' + str(ids[0]) + ', ' + str(ids[l-1]) + ')', ProgramLog.MsgType.ENV)
        log.unindent()
        return ids, j

    def addField(self, f : Field):
        j = len(self.fields)
        f.ID = j
        self.fields.append(f)
        log('Added ' + str(f) + ' with ID ' + str(j), ProgramLog.MsgType.ENV)
        return j

    def getCurrentTime(self):
        return self.currentTick * self.tStep

    def getForce(self, part : Particle):
        totalF = np.array([0, 0, 0], float)
#        ex = part.getFields()
        for f in self.fields:
 #          if f not in ex:
            totalF += f.getForce(part)
        return totalF

    def tick(self):
        prnt = (self.currentTick % self.tickPrint == 0)
        lg = (self.currentTick % self.tickLog == 0)
        if prnt:
            t = self.getCurrentTime()
            log(str(np.round(100*self.currentTick/self.tickLength)) + '% done')
        for p in self.particles:
            p.applyForce(self.getForce(p))
            p.update(self.tStep, self.approx)
        if lg:
            self.simlog()
        for p in self.particles:
            p.tick()
        for f in self.fields:
            f.update()
            f.tick()
        self.currentTick += 1

    def getTotalEnergy(self):
        e = float(0)
        for p in self.particles:
            e += p.getEnergy() #+ p.getPotentialEnergy()
        return e

    def getTotalMomentum(self):
        mv = np.array([0,0,0], float)
        for p in self.particles:
            mv += p.getMomentum()
        return mv

    def getTotalAngMomentum(self):
        tau = np.array([0,0,0], float)
        for p in self.particles:
            tau += p.getAngMomentum()
        return tau

    def getFullName(self):
        return 'System'

    def getProperty(self, p: Property):
        if p is Simulation.Property.TIME:
            return self.getCurrentTime()
        if p is Simulation.Property.ENERGY:
            return self.getTotalEnergy()
        if p is Simulation.Property.MOMENTUM:
            return self.getTotalMomentum()
        if p is Simulation.Property.ANGMOMENTUM:
            return self.getTotalAngMomentum()
        else:
            return None


class SingleProtonSimulation(Simulation):

    def __init__(self, approx : Approximation, tStep = float(1), timeLength = float(1)):
        super(SingleProtonSimulation, self).__init__(approx = approx, name = 'Single Proton in Constant Uniform B-Field',
                                                     tStep = tStep, timeLength =  timeLength)
        self.addField(ConstantUniformBField(fieldVector = np.array([0, 0, 1000], float)))
        pro = Proton()
        self.addParticle(pro)
        self.simlog.track(self, Simulation.Property.TIME, Simulation.Property.ENERGY, Simulation.Property.MOMENTUM, Simulation.Property.ANGMOMENTUM)
        self.simlog.track(pro, Particle.Property.POS)

    def post(self):
        print('Done')
        #print(self.xList)
        #plt.plot(self.xList[0], self.yList[0])
        #plt.show()