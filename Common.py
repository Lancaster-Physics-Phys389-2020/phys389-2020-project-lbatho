import csv
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

import scipy.constants as const

PI = const.pi
EPSILON0 = const.epsilon_0
E_PROTON = const.physical_constants['proton mass energy equivalent in MeV']


class Approximation(Enum):
    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'


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
        self.file = open(name + ".csv", 'w', newline = '')
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

    @classmethod
    def makeLog(cls):
        d = datetime.now()
        s = d.strftime('%Y-%m-%d_%H-%M-%S')
        return ProgramLog(s)

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


log = ProgramLog.makeLog()

