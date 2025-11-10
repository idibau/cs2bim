from service.bounding_box import BoundingBox

class TestBoundingBox:

    def test_get_wgs84_bounding_box_as_string(self):
        bb = BoundingBox(
            min_northing=1200000.0,
            min_easting=2600000.0,
            max_northing=1200100.0,
            max_easting=2600100.0,
        )
        s = bb.get_wgs84_bounding_box_as_string()
        parts = s.split(",")
        assert len(parts) == 4
        lon1, lat1, lon2, lat2 = map(float, parts)
        for v in [lat1, lat2]:
            assert 40.0 < v < 55.0
        for v in [lon1, lon2]:
            assert 0.0 < v < 20.0