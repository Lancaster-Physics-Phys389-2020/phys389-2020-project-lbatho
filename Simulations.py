from abc import ABC, abstractmethod

import scipy as sp
import numpy as np
from Particles import Particle
from Fields import Field


class Simulation(ABC):

    def __init__(self, name = "", tStep = 1, timeLength = 1):
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
        self.particles[self.nextID[0]] = part
        self.nextID[0] += 1
        return self.nextID[0] - 1

    def addField(self, f : Field):
        self.fields[self.nextID[1]] = f
        self.nextID[1] += 1
        return self.nextID[1] - 1


class ProtonSimulation(Simulation):

    def start(self):
        pass
