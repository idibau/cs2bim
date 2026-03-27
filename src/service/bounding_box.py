import shapely
from pyproj import Transformer
from shapely import wkt


class BoundingBox:
    """
    Represents a bounding box in the LV95 coordinate system

    Attributes:
        min_northing (float): Minimum northing value (Y coordinate in LV95).
        min_easting (float): Minimum easting value (X coordinate in LV95).
        max_northing (float): Maximum northing value (Y coordinate in LV95).
        max_easting (float): Maximum easting value (X coordinate in LV95).
    """

    def __init__(self, min_northing: float, min_easting: float, max_northing: float, max_easting: float):
        self.min_northing = min_northing
        self.min_easting = min_easting
        self.max_northing = max_northing
        self.max_easting = max_easting

    @classmethod
    def from_wkts(cls, wkts: list[str]) -> "BoundingBox":
        """
        Calculates and returns the minimal bounding box containing all given geometries.

        Args:
            wkts: A list of WKT strings representing geometries.

        Returns:
            A BoundingBox object describing the minimal bounding box around the given geometries.
        """
        geoms = [wkt.loads(x) for x in wkts]
        bbox = shapely.total_bounds(geoms)
        return BoundingBox(bbox[1], bbox[0], bbox[3], bbox[2])

    def get_wgs84_bounding_box_as_string(self) -> str:
        """
        Convert the LV95 bounding box to a WGS84 bounding box string.

        Returns:
            Comma-separated WGS84 bounding box string.
        """
        transformer = Transformer.from_crs("epsg:2056", "epsg:4326")
        p_1 = transformer.transform(self.min_easting, self.min_northing)
        p_2 = transformer.transform(self.max_easting, self.max_northing)
        return f"{p_1[1]},{p_1[0]},{p_2[1]},{p_2[0]}"
