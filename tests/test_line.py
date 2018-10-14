# test_line.py
from pymeteor.pymeteor import Line
from pymeteor.pymeteor import Point

# Assert two lines intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,0)+and+(2,0),+line+segment+through+(1,1)+and+(1,0)
def test_intersection():
    line1 = Line(Point(0,0), Point(2,0))
    line2 = Line(Point(1,1), Point(1,0))

    assert line1.intersects(line2) == True
    assert line2.intersects(line1) == True

# Assert two lines that are parallel do not intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,1)+and+(2,1),+line+segment+through+(0,2)+and+(2,2)
def test_parallel():
    line1 = Line(Point(0,1), Point(2,1))
    line2 = Line(Point(0,2), Point(2,2))

    assert line1.intersects(line2) == False
    assert line2.intersects(line1) == False

# Assert two line segments that would intersect without endpoints, do not intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,1)+and+(2,1),+line+segment+through+(3,0)+and+(3,2)
def test_non_intersection():
    line1 = Line(Point(0,1), Point(2,1))
    line2 = Line(Point(3,0), Point(3,2))

    assert line1.intersects(line2) == False
    assert line2.intersects(line1) == False

# Assert two line segments that intersect perpindicularly on one endpoint, do intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,1)+and+(2,1),+line+segment+through+(2,0)+and+(2,2)
def test_perpendicular_intersection_one():
    line1 = Line(Point(0,1), Point(2,1))
    line2 = Line(Point(2,0), Point(2,2))

    assert line1.intersects(line2) == True
    assert line2.intersects(line1) == True

# Assert two line segments that intersect perpindicularly on both endpoints, do intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,2)+and+(2,2),+line+segment+through+(2,0)+and+(2,2)
def test_perpendicular_intersection_two():
    line1 = Line(Point(0,2), Point(2,2))
    line2 = Line(Point(2,0), Point(2,2))

    assert line1.intersects(line2) == True
    assert line2.intersects(line1) == True

# Assert two line segments that are collinear and intersect on their end points, do intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,1)+and+(2,1),+line+segment+through+(2,1)+and+(3,1)
def test_collinear_intersection():
    line1 = Line(Point(0,1), Point(2,1))
    line2 = Line(Point(2,1), Point(3,1))

    assert line1.intersects(line2) == True
    assert line2.intersects(line1) == True

# Assert two line segments that are collinear and do not intersect on their end points, do not intersect
# See http://www.wolframalpha.com/input/?i=line+segment+through+(0,1)+and+(2,1),+line+segment+through+(3,1)+and+(4,1)
def test_collinear_non_intersection():
    line1 = Line(Point(0,1), Point(2,1))
    line2 = Line(Point(3,1), Point(4,1))

    assert line1.intersects(line2) == False
    assert line2.intersects(line1) == False
