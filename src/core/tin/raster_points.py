import numpy as np
import shapely
from shapely import Polygon, Point


class RasterPoints(object):
    """Class for handling raster points"""

    def __init__(self, xyz_filepath: str):
        self.data = np.loadtxt(xyz_filepath, delimiter=" ", skiprows=1)
        if self.data.ndim == 1:
            self.data = self.data.reshape((1, -1))
        self.xy = self.data[:, :2]

    def within(self, polygon: Polygon, buffer_dist: float = 0) -> np.ndarray | None:
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
