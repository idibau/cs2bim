from pyproj import Transformer


class BoundingBox:
    """
    Information about a bounding box in a LV95

    Attributes
    ----------
    min_northing : float
        Minimum longitude
    min_easting : float
        Minimum latitude
    max_northing : float
        Maximum longitude
    max_easting : float
        Maximum latitude
    """

    def __init__(self, min_northing: float, min_easting: float, max_northing: float, max_easting: float) -> None:
        self.min_northing = min_northing
        self.min_easting = min_easting
        self.max_northing = max_northing
        self.max_easting = max_easting

    def get_wgs84_bounding_box_as_string(self) -> str:
        transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
        p_1 = transformer.transform(self.min_easting, self.min_northing)
        p_2 = transformer.transform(self.max_easting, self.max_northing)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"
