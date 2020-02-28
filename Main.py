import numpy as np
import scipy.constants as const

from Simulations import *

print("Hello.")
print(const.physical_constants['proton mass energy equivalent in MeV'])
sim = SingleProtonSimulation(approx = Approximation.EULER, timeLength = 10, tStep = 0.1)
sim.start()