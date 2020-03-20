print('Particle Simulator')
print('Loading modules...')

from Common import *
from Simulations import *

print('Logging to', log.fname)
sim = IsoCyclotronSimulation(approx = Approximation.VERLET, tStep = 0.001, timeLength = 30, logStep = 0.1)
sim.start()

from Analysis import *

a = AnalysisHandler('out.pickle')
a.plot('Bunch 0: Central Position - x', 'Bunch 0: Central Position - y')
