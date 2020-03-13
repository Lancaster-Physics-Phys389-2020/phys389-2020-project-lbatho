from Common import *
from Fields import *
from Particles import *


class Simulation(Trackable, ABC):

    class Property(TrackableProperty):
        TIME = 'Time', False
        ENERGY = 'Total Energy', False
        MOMENTUM = 'Total Momentum', False
        ANGMOMENTUM = 'Total Angular Momentum', False

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
            self.tickLog = int(logStep / tStep)
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
        log('Done in ' + str((datetime.now() - START_TIME).total_seconds()) + 's')
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
            print(str(np.round(100*self.currentTick/self.tickLength)) + '% done')
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

    def __init__(self, approx : Approximation, tStep: float, timeLength: float, logStep: float = None):
        super(SingleProtonSimulation, self).__init__(approx = approx, name = 'Single Proton in Constant Uniform B-Field',
                                                     tStep = tStep, timeLength =  timeLength, logStep = logStep)
        #self.addField(ConstantUniformBField(fieldVector = np.array([0, 0, 1000], float)))
        pro = Proton(velocity = np.array([1,0,0], float))
        self.addParticle(pro)
        self.simlog.track(self, Simulation.Property.TIME, Simulation.Property.ENERGY, Simulation.Property.MOMENTUM, Simulation.Property.ANGMOMENTUM)
        self.simlog.track(pro, Particle.Property.POS)

    def post(self):
        print('Done')
        self.simlog.save()
        df = self.simlog.getData()
        x, y, z = SimLog.splitArray(df['Proton 0: Position'])
        plt.plot(x, y)
        plt.show()


class CyclotronSimulation(Simulation):

    def __init__(self, approx: Approximation, tStep: float, timeLength: float, logStep: float = None,
                 part: Type[Particle] = Proton, nBunch: int = 1, nPerBunch: int = 10):
        super(CyclotronSimulation, self).__init__(approx = approx, tStep = tStep, timeLength = timeLength,
                                                  logStep = logStep, name = part.__name__ + ' Cyclotron')
        self.simlog.track(self, Simulation.Property.TIME)
        for i in range(nBunch):
            b = Bunch(partType = part, N = nPerBunch, velocity = np.array([1,0,0], float))
            self.addBunch(b)
            self.simlog.track(b, Bunch.Property.POS)
        bf = ConstantUniformBField(np.array([0,0,1000]))
        self.addField(bf)
        r = AxisRegion(-5, 5, Axis.X)
        c = CyclotronEField(fieldVector = np.array([1000,0,0], float), partType = part, bField = bf, tStep = tStep, region = r)
        self.addField(c)

    def post(self):
        self.simlog.save()
        df = self.simlog.getData()
        x, y, z = SimLog.splitArray(df['Bunch 0: Central Position'])
        plt.plot(x, y)
        plt.show()