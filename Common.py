from enum import Enum
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
import scipy.constants as const

PI = const.pi
EPSILON0 = const.epsilon_0
E_PROTON = const.physical_constants['proton mass energy equivalent in MeV']


class Approximation(Enum):
    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'


class MsgType(Enum):
    PRINT = 'Print'
    ENV = 'Environment'
    PART = 'Particle'


class Log:

    @classmethod
    def makeLog(cls):
        d = datetime.now()
        s = d.strftime('%Y-%m-%d_%H-%M-%S')
        return Log(s)

    def __init__(self, name = 'log', printEnv = False):
        self.printEnv = printEnv
        self.currentIndent = int(0)
        self.name = name
        Path('logs').mkdir(exist_ok = True)
        self.fname = 'logs/' + name + '.log'
        self.out = open(self.fname, 'w')

    def __call__(self, s, msgtype = MsgType.PRINT):
        self.log(s, msgtype)

    def log(self, s, msgtype = MsgType.PRINT):
        self.write(s)
        if msgtype == MsgType.PRINT:
            self.print(s)
        elif (msgtype == MsgType.ENV) & self.printEnv:
            self.print(s)
#        elif (msgtype == MsgType.PART) & self.printPart:
#            print(s)

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

    def indent(self, i = int(1)):
        self.currentIndent += 1

    def unindent(self):
        self.currentIndent = 0


log = Log.makeLog()

