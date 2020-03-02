import Common
from Simulations import *

print("Hello.")
Common.printEnv = False
sim = SingleProtonSimulation(approx = Approximation.VERLET, timeLength = 100, tStep = 0.001, printStep = 10)
sim.start()
