from Common import *
from Simulations import *

print('Hello.')
print('Logging to', log.fname)

#Common.printEnv = False
sim = SingleProtonSimulation(approx = Approximation.VERLET, timeLength = 100, tStep = 0.001, printStep = 10)
sim.start()
