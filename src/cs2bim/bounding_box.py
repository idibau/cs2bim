from __future__ import annotations
from pyproj import Transformer


class BoundingBox:
    """
    Information about a bounding box in a LV95

    Attributes
    ----------
    min_lon : float
        Minimum longitude
    min_lat : float
        Minimum latitude
    max_lon : float
        Maximum longitude
    max_lat : float
        Maximum latitude
    """

    def __init__(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> None:
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat

    def get_wgs84_bounding_box_as_string(self) -> str:
        transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
        p_1 = transformer.transform(self.min_lat, self.min_lon)
        p_2 = transformer.transform(self.max_lat, self.max_lon)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"
