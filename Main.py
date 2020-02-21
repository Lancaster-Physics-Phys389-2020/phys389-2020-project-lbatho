from Simulation import Sim
from Particle import *
from Fields import *

print("Hello.")
f = UniformField(name = "test", fieldValue = np.array([1,0,0], float))
print(f.name, f.getVal(np.array([0, 0, 0])))
f2 = Field()
print(f2.getVal(np.array([0,0,0])))