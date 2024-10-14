from __future__ import annotations
from pyproj import Transformer


class BoundingBox:
    """
    Information about a bounding box in a LV95

    Attributes
    ----------
    min_nord : float
        Minimum longitude
    min_east : float
        Minimum latitude
    max_nord : float
        Maximum longitude
    max_east : float
        Maximum latitude
    """

    def __init__(self, min_nord: float, min_east: float, max_nord: float, max_east: float) -> None:
        self.min_nord = min_nord
        self.min_east = min_east
        self.max_nord = max_nord
        self.max_east = max_east

    def get_wgs84_bounding_box_as_string(self) -> str:
        transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
        p_1 = transformer.transform(self.min_east, self.min_nord)
        p_2 = transformer.transform(self.max_east, self.max_nord)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"
