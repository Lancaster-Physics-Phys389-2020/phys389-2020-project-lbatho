from Simulations import *

print('Hello.')
print('Logging to', log.fname)

sim = SingleProtonSimulation(approx = Approximation.VERLET, timeLength = 100, tStep = 0.001)
sim.start()
