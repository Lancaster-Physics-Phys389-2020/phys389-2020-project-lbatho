import numpy as np


class Field:

    def __init__(self, name = ""):
        self.name = name

    def getVal(self, point: np.array) -> np.array:
        pass


class UniformField(Field):

    __fieldVal: np.array

    def __init__(self, name = "", fieldValue = np.array([0, 0, 0], float)):
        self.name = name
        self.__fieldVal = fieldValue

    def getVal(self, point: np.array):
        return self.__fieldVal


