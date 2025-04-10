import numpy as np
import pandas as pd
import geopandas as gpd
import shapely


class RasterPoints(object):
    """
    Class for handling raster points

    Attributes
    ----------
    data : geopandas.GeoDataFrame
        Raster points as GeoDataFrame
    """

    def __init__(self, data: np.ndarray, origin: np.ndarray = np.zeros((3,))) -> None:
        if not np.allclose(origin, np.zeros((3,))):
            data = self._reduce(data, origin)
        self.data = self._to_gpd(data)

    def _reduce(self, data: np.ndarray, origin: np.ndarray):
        """Reduces raster points by origin"""
        return data - origin

    def _to_gpd(self, data: np.ndarray):
        """Converts points to GeoDataFrame"""
        p = pd.DataFrame(data, columns=["x", "y", "z"])
        return gpd.GeoDataFrame(p, geometry=gpd.points_from_xy(p.x, p.y))

    def get_all_points(self):
        """Returns all points stored in this object"""
        return pd.DataFrame(self.data.drop(columns=["geometry"])).to_numpy()

    def within(self, polygon: shapely.geometry.Polygon, buffer_dist: float | int = 0) -> np.ndarray:
        """
        Filters points data by geometry with option to add buffer.
        Returns all points which lie within this polygon.

        Parameters
        ----------
        polygon : shapely.geometry.Polygon
            Geometry to filter points with.

        Returns
        -------
        _ : np.ndarray
            Array with all points within polygon.
        """
        if buffer_dist > 0:
            filter_geom = polygon.buffer(distance=buffer_dist)
        else:
            filter_geom = polygon
        gdf_points_within = gpd.sjoin(
            self.data,
            gpd.GeoDataFrame(index=[0], geometry=[filter_geom]),
            how="inner",
            predicate="within",
        )
        return pd.DataFrame(gdf_points_within.drop(columns=["geometry", "index_right"])).to_numpy()
