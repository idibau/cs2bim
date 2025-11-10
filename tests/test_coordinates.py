from core.ifc.model.coordinates import Coordinates


class TestCoordinates:

    def test_coordinates_equality_and_hash(self):
        a = Coordinates(1, 2, 3)
        b = Coordinates(1.0, 2.0, 3.0)
        c = Coordinates(1, 2, 4)
        assert a == b
        assert a != c
        s = {a, b}
        assert len(s) == 1