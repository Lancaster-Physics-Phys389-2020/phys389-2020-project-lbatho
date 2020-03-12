import csv
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

import numpy as np
import scipy.constants as const

START_TIME = datetime.now()
START_TIME_STR = START_TIME.strftime('%Y-%m-%d_%H-%M-%S')

PI = const.pi
EPSILON0 = const.epsilon_0
E_PROTON = const.physical_constants['proton mass energy equivalent in MeV']


class Approximation(Enum):
    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'


class Axis(Enum):
    X = 0
    Y = 1
    Z = 2


class Region(ABC):

    @abstractmethod
    def contains(self, point: np.array) -> bool:
        pass


class AllRegion(Region):

    def contains(self, point: np.array):
        return True


ALL_SPACE: Region = AllRegion()


class CubeRegion(Region):

    def __init__(self, boundA: np.array, boundB: np.array):
        if boundA[0] < boundB[0]:
            self.x1 = boundA[0]
            self.x2 = boundB[0]
        else:
            self.x1 = boundB[0]
            self.x2 = boundA[0]
        if boundA[1] < boundB[1]:
            self.y1 = boundA[1]
            self.y2 = boundB[1]
        else:
            self.y1 = boundB[1]
            self.y2 = boundA[1]
        if boundA[2] < boundB[2]:
            self.z1 = boundA[2]
            self.z2 = boundB[2]
        else:
            self.z1 = boundB[2]
            self.z2 = boundA[2]

    def contains(self, point: np.array):
        x = point[0]
        y = point[1]
        z = point[2]
        if (point[0] >= self.x1) and (point[0] <= self.x2) and (point[1] >= self.y1) and (point[1] <= self.y2) and (point[2] >= self.z1) and (point[2] <= self.z2):
            return True
        else:
            return False


class AxisRegion(Region):

    def __init__(self, boundA: float, boundB: float, axis: Axis):
        if boundA < boundB:
            self.b1 = boundA
            self.b2 = boundB
        else:
            self.b1 = boundB
            self.b2 = boundA
        self.axis:Axis = axis

    def contains(self, point: np.array):
        if (point[self.axis.value] >= self.b1) and (point[self.axis.value] <= self.b2):
            return True
        else:
            return False

class TrackableProperty(Enum):
    pass


class Trackable(ABC):

    @abstractmethod
    def getProperty(self, p: TrackableProperty):
        pass

    @abstractmethod
    def getFullName(self) -> str:
        pass


class SimLog:

    def __init__(self, name: str):
        self.name = name
        self.file = open(name + '_' + START_TIME_STR + '.csv', 'w', newline = '')
        self.columns = []
        self.out: csv.DictWriter = None
        self.logging = False
        self.tracked: List[Trackable] = []

    def start(self):
        self.logging = True
        self.out = csv.DictWriter(self.file, fieldnames = self.columns)
        self.out.writeheader()

    def track(self, t: Trackable, *trackedProperties: TrackableProperty):
        self.tracked.append((t, trackedProperties))
        for i in trackedProperties:
            self.columns.append(t.getFullName() + ': ' + i.value)

    def log(self):
        dic = {}
        for t in self.tracked:
            for i in t[1]:
                dic.update({(t[0].getFullName() + ': ' + i.value): t[0].getProperty(i)})
        self.out.writerow(dic)

    def __call__(self):
        self.log()


class ProgramLog:

    class MsgType(Enum):
        PRINT = 'Print'
        ENV = 'Environment'
        PART = 'Particle'
        FIELD = 'Field'
        BUNCH = 'Bunch'

    def __init__(self, name = 'log', logPrint = True, logEnv = True, logPart = True,
                 logField = False, logBunch = True):
        self.dicLog = {ProgramLog.MsgType.PRINT: logPrint, ProgramLog.MsgType.ENV: logEnv}
        self.currentIndent = int(0)
        self.name = name
        Path('logs').mkdir(exist_ok = True)
        self.fname = 'logs/' + name + '.log'
        self.out = open(self.fname, 'w')

    def __call__(self, s, msgtype = MsgType.PRINT):
        self.log(s, msgtype)

    def log(self, s, msgtype = MsgType.PRINT):
        if self.dicLog.get(msgtype):
            self.print(s)
            self.write(s)

    def print(self, s):
        i = ''
        for j in range(self.currentIndent):
            i += '\t'
        print(i + str(s))

    def write(self, s):
        i = ''
        for j in range(self.currentIndent):
            i += '\t'
        self.out.write(i + str(s) + '\n')
        self.out.flush()

    def indent(self, i: int = 1):
        self.currentIndent += i

    def unindent(self):
        self.currentIndent = 0


log = ProgramLog(START_TIME_STR)

