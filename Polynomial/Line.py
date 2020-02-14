from Parabola import Parabola

class Line(Parabola):

    def __init__(self, m, b):
        # Line of form y = m*x + b
        super().__init__(0, b, m)