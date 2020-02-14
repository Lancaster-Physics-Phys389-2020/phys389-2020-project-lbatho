from Polynomial import Polynomial

class Parabola(Polynomial):

    def __init__(self, a,b,c):
        # Polynomial ax^2 + bx +c 
        # Note Polynomial maps constant as first item  
        super().__init__([c,b,a])
