from enum import Enum
from abc import ABC, abstractmethod

class Approximation(Enum):

    EULER = 'Euler'
    EULER_CROMER = 'Euler-Cromer'
    VERLET = 'Verlet'