import pickle
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Type

import numpy as np
import scipy.constants as const
import matplotlib.pyplot as plt
from pandas import DataFrame

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
        if (point[0] >= self.x1) and (point[0] <= self.x2) and (point[1] >= self.y1) and (point[1] <= self.y2) and (
                point[2] >= self.z1) and (point[2] <= self.z2):
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
        self.axis: Axis = axis

    def contains(self, point: np.array):
        if (point[self.axis.value] >= self.b1) and (point[self.axis.value] <= self.b2):
            return True
        else:
            return False


class TrackableProperty(Enum):

    def isVector(self):
        return self.value[1]

    def __str__(self):
        return self.value[0]


class Trackable(ABC):

    @abstractmethod
    def getProperty(self, p: TrackableProperty):
        pass

    @abstractmethod
    def getFullName(self) -> str:
        pass

    @abstractmethod
    def getTypeName(self) -> str:
        pass


class SimLog:

    @classmethod
    def splitArray(cls, column):
        x = []
        y = []
        z = []
        for i in column:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])
        return x, y, z

    @classmethod
    def summariseTrackables(cls, lis: List[Trackable]) -> dict:
        dic = {}
        for i in lis:
            t = i.getTypeName()
            if dic.get(t) is None:
                dic.update({t: 1})
            else:
                dic.update({t: dic.get(t) + 1})
        return dic

    def __init__(self, name: str):
        self.name = name
        self.columns = []
        self.logging = False
        self.tracked: List[Trackable] = []
        self.rows: List[dict] = []
        self.miscdata = {}
        self.envdata = {}

    def start(self):
        self.logging = True
        # self.out = csv.DictWriter(self.file, fieldnames = self.columns)
        # self.out.writeheader()

    def track(self, t: Trackable, *trackedProperties: TrackableProperty):
        self.tracked.append((t, trackedProperties))
        for i in trackedProperties:
            self.columns.append(t.getFullName() + ': ' + str(i))

    def log(self):
        dic = {}
        for t in self.tracked:
            for i in t[1]:
                dic.update({(t[0].getFullName() + ': ' + str(i)): t[0].getProperty(i)})
        # self.out.writerow(dic)
        # self.file.flush()
        self.rows.append(dic)

    def getTrackedData(self) -> DataFrame:
        df: DataFrame = self.getRawTrackedData()
        vec = False
        for k, v in self.rows[0].items():
            if isinstance(v, np.ndarray):
                vec = True
                break
        if not vec:
            return df
        else:
            dic = {}
            for d in list(df):
                if isinstance(df[d][0], np.ndarray):
                    x, y, z = self.splitArray(df[d])
                    dic.update({(d + ' - x'): x, (d + ' - y'): y, (d + ' - z'): z})
                else:
                    dic.update({d: df[d]})
            return DataFrame(dic)

    def getRawTrackedData(self) -> DataFrame:
        return DataFrame(self.rows)

    def appendMiscData(self, data: dict):
        self.miscdata.update(data)

    def getMiscData(self) -> dict:
        return self.miscdata

    def appendEnvData(self, data: dict):
        self.envdata.update(data)

    def getEnvData(self) -> dict:
        return self.envdata

    def save(self, filename: str = None):
        if filename is None:
            file = self.name + '_' + START_TIME_STR + '.pickle'
        else:
            file = filename
        log('Pickling simulation data to ' + file + '... ', endLine = False)
        with open(file, 'wb') as f:
            pickle.dump(self, f)
        print('done')

    def saveToCSV(self, filename: str = None):
        if filename is None:
            file = self.name + '_' + START_TIME_STR + '.csv'
        else:
            file = filename
        log('Dumping simulation data as CSV to ' + file + '... ', endLine = False)
        self.getTrackedData().to_csv(path_or_buf = file)
        log('done')

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

    def __call__(self, s = None, msgtype = MsgType.PRINT, endLine = True):
        if s is None:
            s = ''
        self.log(s, msgtype, endLine)

    def log(self, s, msgtype = MsgType.PRINT, endLine = True):
        if self.dicLog.get(msgtype):
            self.print(s, endLine)
            self.write(s, endLine)

    def print(self, s, endLine = True):
        i = ''
        for j in range(self.currentIndent):
            i += '\t'
        if endLine:
            print(i + str(s))
        else:
            print(i + str(s), end = '')

    def write(self, s, endLine = True):
        i = ''
        for j in range(self.currentIndent):
            i += '\t'
        if endLine:
            self.out.write(i + str(s) + '\n')
        else:
            self.out.write(i + str(s))
        self.out.flush()

    def indent(self, i: int = 1):
        self.currentIndent += i

    def unindent(self):
        self.currentIndent = 0


log = ProgramLog(START_TIME_STR)
