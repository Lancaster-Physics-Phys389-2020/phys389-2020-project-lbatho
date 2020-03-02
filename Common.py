from enum import Enum
from abc import ABC, abstractmethod
import scipy.constants as const

E_proton = const.physical_constants['proton mass energy equivalent in MeV']

printEnv = False
printPart = False


class Approximation(Enum):
    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'


class MsgType(Enum):
    PRINT = 'Print'
    ENV = 'Environment'
    PART = 'Particle'


def log(s, type = MsgType.PRINT):
    if type == MsgType.PRINT:
        print(s)
    elif (type == MsgType.ENV) & printEnv:
        print(s)
    elif (type == MsgType.PART) & printPart:
        print(s)
