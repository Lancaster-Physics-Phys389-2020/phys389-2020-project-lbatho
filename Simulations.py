from abc import ABC, abstractmethod
from enum import Enum

import scipy as sp
import numpy as np
from Particles import *
from Fields import *


class Approximation(Enum):

    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'


class Simulation(ABC):

    def __init__(self, approx : Approximation, name = "", tStep = 1, timeLength = 1):
        self.approx = approx
        self.name = name
        self.tickLength = int(timeLength / tStep)
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
        ident = self.nextID[0]
        self.particles[ident] = part
        self.nextID[0] += 1
        return ident

    def addField(self, f : Field):
        ident = self.nextID[1]
        self.fields[ident] = f
        self.nextID[1] += 1
        return ident

    def getCurrentTime(self):
        return self.tick * self.tStep

    def getAccel(self, part : Particle):
        return self.getForce(part) / part.m

    def getForce(self, part : Particle):
        totalF = np.array([0, 0, 0], float)
        ex = part.getFields()
        for f in self.fields:
            if f not in ex:
                totalF += f.getForce(part)
        return totalF


class SingleProtonSimulation(Simulation):

    def __init__(self, approx : Approximation, tStep = 1, timeLength = 1):
        super(SingleProtonSimulation, self).__init__(approx, 'Single Proton in Constant Uniform B-Field', tStep, timeLength)
        ConstantUniformBField(sim = self, fieldVector = np.array([1, 0, 0], float))
        self.pro = Proton(sim = self)

    def start(self):
        for i in range(self.tickLength):
            self.tick()

    def tick(self):
        print(self.getCurrentTime(), self.pro.r)
        for f in self.fields:
            f.update()
        for p in self.particles:
            p.update()
        for p in self.particles:
            p.tick()