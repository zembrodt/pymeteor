# test_point.py
from pymeteor.pymeteor import Point

# See http://www.wolframalpha.com/input/?i=cross+product+of+(1,2)+and+(3,4)
# and http://www.wolframalpha.com/input/?i=cross+product+of+(3,4)+and+(1,2)
def test_cross_product():
    a = Point(1,2)
    b = Point(3,4)

    assert a.cross_product(b) == -2
    assert b.cross_product(a) == 2
    

def test_equals_true():
    a = Point(1,2)
    b = Point(1,2)

    assert a.equals(b) == True
    assert b.equals(a) == True

def test_equals_false():
    a = Point(1,2)
    b = Point(2,1)

    assert a.equals(b) == False
    assert b.equals(a) == False

def test_subtract_true():
    a = Point(1,2)
    b = Point(3,4)
    
    c = Point(2,2)
    d = Point(-2,-2)

    assert b.subtract(a).equals(c) == True
    assert a.subtract(b).equals(d) == True

def test_subtract_false():
    a = Point(1,2)
    b = Point(3,4)

    assert a.subtract(b).equals(b) == False

def test_subtract_zero():
    a = Point(1,2)
    b = Point(0,0)

    assert a.subtract(a).equals(b) == True
