import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import Point


class RasterPoints(object):
    """
    Class for handling raster points

    Attributes
    ----------
    data : geopandas.GeoDataFrame
        Raster points as geopandas.GeoDataFrame
    """

    def __init__(self, xyz_filepath: str, origin: np.ndarray = np.zeros((3,))) -> None:
        self.data = np.loadtxt(xyz_filepath, delimiter=" ", skiprows=1)
        if not np.allclose(origin, np.zeros((3,))):
            self.data = self.data - origin
        if self.data.ndim == 1:
            self.data = self.data.reshape((1, -1))
        self.xy = self.data[:, :2]

    def within(
            self,
            polygon: shapely.geometry.Polygon,
            buffer_dist: float = 0,
    ) -> np.ndarray:
        """
        Return points within (or within buffer of) polygon.
        First filters by polygon bounding box for speed.
        """
        geom = polygon.buffer(buffer_dist) if buffer_dist > 0 else polygon

        minx, miny, maxx, maxy = geom.bounds
        in_bbox = (
                (self.xy[:, 0] >= minx) &
                (self.xy[:, 0] <= maxx) &
                (self.xy[:, 1] >= miny) &
                (self.xy[:, 1] <= maxy)
        )

        if not np.any(in_bbox):
            return None

        candidate_points = shapely.points(self.xy[in_bbox])
        mask = geom.contains(candidate_points)

        if np.any(mask):
            return self.data[in_bbox][mask]
        else:
            return None

