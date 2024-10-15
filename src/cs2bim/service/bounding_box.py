from __future__ import annotations
from pyproj import Transformer


class BoundingBox:
    """
    Information about a bounding box in a LV95

    Attributes
    ----------
    min_north : float
        Minimum longitude
    min_east : float
        Minimum latitude
    max_north : float
        Maximum longitude
    max_east : float
        Maximum latitude
    """

    def __init__(self, min_north: float, min_east: float, max_north: float, max_east: float) -> None:
        self.min_north = min_north
        self.min_east = min_east
        self.max_north = max_north
        self.max_east = max_east

    def get_wgs84_bounding_box_as_string(self) -> str:
        transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
        p_1 = transformer.transform(self.min_east, self.min_north)
        p_2 = transformer.transform(self.max_east, self.max_north)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"
