import pytest
from Polynomial import Polynomial

def test_create():
    a = Polynomial([1,1,1])
    assert a(5) == 31

def test_poynoial_add():
    a = Polynomial([1,-1,1])
    b = Polynomial([-1,1,1])
    c = a+b 
    assert c.coefficients == [0, 0, 2]

def test_broken_test():
    a = Polynomial([1,-1,1])
    assert a(5) == 3