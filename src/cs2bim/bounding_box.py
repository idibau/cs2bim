from __future__ import annotations
from pyproj import Transformer

from cs2bim.enum.epsg_code import EPSGCode


class BoundingBox:

    def __init__(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float, epsg_code: EPSGCode) -> None:
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat
        self.epsg_code = epsg_code

    @classmethod
    def from_wkt(cls, wkt: str, epsg_code: EPSGCode) -> BoundingBox:
        coordinates = []
        for points in wkt[9:-2].split(","):
            coordinates.append((float(points.split(" ")[0]), float(points.split(" ")[1])))
        return cls(coordinates[0][1], coordinates[0][0], coordinates[2][1], coordinates[2][0], epsg_code)

    def get_wgs84_bounding_box_as_string(self) -> str:
        transformer = Transformer.from_crs(self.epsg_code.value, EPSGCode.WGS84.value)
        p_1 = transformer.transform(self.min_lat, self.min_lon)
        p_2 = transformer.transform(self.max_lat, self.max_lon)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"

    def get_lv95_polygon_wkt(self) -> str:
        transformer = Transformer.from_crs(self.epsg_code.value, EPSGCode.LV95.value)
        p_1 = transformer.transform(self.min_lat, self.min_lon)
        p_2 = transformer.transform(self.min_lat, self.max_lon)
        p_3 = transformer.transform(self.max_lat, self.min_lon)
        p_4 = transformer.transform(self.max_lat, self.max_lon)
        return f"POLYGON (({p_1[0]} {p_1[1]},{p_2[0]} {p_2[1]},{p_3[0]} {p_3[1]},{p_4[0]} {p_4[1]},{p_1[0]} {p_1[1]}))"
