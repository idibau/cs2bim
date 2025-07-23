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

    def __init__(self, xyz_filepaths: list[str], origin: np.ndarray = np.zeros((3,))) -> None:
        self.xyz_filepaths = xyz_filepaths
        self.origin = origin

    def within(
            self,
            polygon: shapely.geometry.Polygon,
            buffer_dist: float = 0,
    ) -> np.ndarray:
        """
        Efficiently load and filter points within a (possibly buffered) polygon from multiple xyz files.
        Assumes xyz files have at least three columns: x, y, z (plus any others you want to retain).
        """
        geom = polygon.buffer(buffer_dist) if buffer_dist > 0 else polygon
        results = []
        for xyz_filepath in self.xyz_filepaths:
            try:
                data = np.loadtxt(xyz_filepath, delimiter=" ", skiprows=1)
                if not np.allclose(self.origin, np.zeros((3,))):
                    data = self._reduce(data, self.origin)
                data = data - self.origin
            except Exception:
                continue  # Skip corrupted/bad file
            if data.ndim == 1:
                data = data.reshape((1, -1))
            x = data[:, 0]
            y = data[:, 1]
            # Create array of shapely Points
            points = shapely.points(np.column_stack([x, y]))
            mask = geom.contains(points)
            if np.any(mask):
                results.append(data[mask])
        if results:
            return np.vstack(results)
        else:
            return np.empty((0, 3))  # Adjust column count as needed
