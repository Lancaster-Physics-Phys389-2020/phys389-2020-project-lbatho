#import numpy 

class Polynomial:

    def __init__(self, coefficients=[-1,0,1]):
        self.coefficients = list(coefficients)

    def __call__(self,x):
        result = self.coefficients[-1]
        # reverse sum (computationally efficient)
        # run from second last coefficient to first (-1 so stops at 0)
        for i in range(len(self.coefficients)-2,-1,-1): 
            result = result*x + self.coefficients[i]
        return result 

    def __add__(self, other):
        """Return self + other as Polynomial object."""
        
        # Start with the longest list and add in the other
        if len(self.coefficients) > len(other.coefficients):
            result_coeff = self.coefficients[:]  # copy!
            for i in range(len(other.coefficients)):
                result_coeff[i] += other.coefficients[i]
        else:
            result_coeff = other.coefficients[:] # copy!
            for i in range(len(self.coefficients)):
                result_coeff[i] += self.coefficients[i]
        return Polynomial(result_coeff)


    def __mul__(self, other):
        c = self.coefficients
        d = other.coefficients
        M = len(c) - 1
        N = len(d) - 1
        result_coeff = (M+N+1)*[0,] #numpy.zeros(M+N+1)
        for i in range(0, M+1):
            for j in range(0, N+1):
                result_coeff[i+j] += c[i]*d[j]
        return Polynomial(result_coeff)

    def __str__(self):
        s = ''
        for i in range(0, len(self.coefficients)):
            if self.coefficients[i] != 0:
                s += ' + %g*x^%d' % (self.coefficients[i], i)
        # Fix layout
        s = s.replace('+ -', '- ')
        s = s.replace('x^0', '1')
        s = s.replace(' 1*', ' ')
        s = s.replace('x^1 ', 'x ')
        if s[0:3] == ' + ':  # remove initial +
            s = s[3:]
        if s[0:3] == ' - ':  # fix spaces for initial -
            s = '-' + s[3:]
        return s


    def __eq__(self,other):
        return self.coefficients == other.coefficients

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        # return the polynomial with highest order 
        # else with one with largest coefficient 
        if len(self.coefficients) == len(other.coefficients):
            return self.coefficients[-1]>other.coefficients[-1]
        else:
            return len(self.coefficients) > len(other.coefficients)


    def __lt__(self, other):
        # return the polynomial with highest order 
        # else with one with largest coefficient 
        if len(self.coefficients) == len(other.coefficients):
            return self.coefficients[-1]<other.coefficients[-1]
        else:
            return len(self.coefficients) < len(other.coefficients)


