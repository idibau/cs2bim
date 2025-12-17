from shapely import Point


class TestCoordinates:

    def test_coordinates_equality_and_hash(self):
        a = Point(1, 2, 3)
        b = Point(1.0, 2.0, 3.0)
        c = Point(1, 2, 4)
        assert a == b
        assert a != c
        s = {a, b}
        assert len(s) == 1