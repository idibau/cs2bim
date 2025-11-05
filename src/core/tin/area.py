import logging

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import Polygon

from config.configuration import config
from core.ifc.model.coordinates import Coordinates
from core.tin.mesh import Mesh
from core.tin.raster_points import RasterPoints

logger = logging.getLogger(__name__)


class Area:
    """
    Class representing a polygonal area including holes if present.

    NOTE
    ----
    Circular arcs are not supported. Therefore they must be segmented in advance.

    ``ST_CurveToLine`` https://postgis.net/docs/ST_CurveToLine.html provides such
    functionality. However, make sure to use ``flag 1`` to create symmetric output.
    Otherwise the adjacent areas might overlap.

    Parameters
    ----------
    polygon
    origin :
        Origin to reduce coordinate values
    """

    def __init__(self, polygon: BaseGeometry, project_origin: Coordinates):
        if not isinstance(polygon, shapely.Polygon):
            raise ValueError(f"{type(polygon).__name__} not supported")

        self._geometry = self._check_polygon_definition(polygon)

        project_origin = np.array(project_origin.to_tuple()[:2])
        assert project_origin.shape == (2,)
        if not np.allclose(project_origin, np.zeros((2,))):
            self._reduce(project_origin)

        self.raster_points_within = []
        self.raster_points_buffer = []

    def add_raster_points(self, raster_points: RasterPoints):
        rpb = raster_points.within(self.get_geometry, 3 * config.tin.grid_size.value)
        if rpb is not None:
            self.raster_points_buffer.append(rpb)
        rpw = raster_points.within(self.get_geometry, 0)
        if rpw is not None:
            self.raster_points_within.append(rpw)

    def create_mesh(self) -> Mesh:
        if self.raster_points_buffer:
            mesh = Mesh(np.vstack(self.raster_points_buffer))
        else:
            mesh = Mesh(np.empty((0, 3)))
        if self.raster_points_within:
            mesh_clipped = mesh.clip_mesh_by_area(self, np.vstack(self.raster_points_within))
        else:
            mesh_clipped = mesh.clip_mesh_by_area(self, np.empty((0, 3)))
        mesh_clipped_decimated = mesh_clipped.decimate(config.tin.max_height_error, config.tin.grid_size.value)
        logger.debug(
            f"area consistency: {mesh_clipped_decimated.check_area_consistency(self.get_area, 0.1)}"
        )
        return mesh_clipped_decimated

    def _check_polygon_definition(self, poly: Polygon) -> Polygon:
        """
        Checks polygon definition and creates a geometry object.

        According to WKT-Standard the exterior of a polygon (hull / shell)
        has to be defined counter-clockwise (ccw) while present interiors (holes)
        have to defined clockwise.

        Parameters
        ----------
        poly :
            Polygon to be checked

        Returns
        -------
        _ :
            Checked and possibly corrected polygon
        """

        # check exterior
        shell = poly.exterior
        if not shapely.is_ccw(shell):
            shell = shapely.reverse(shell)

        # check interiors if present
        holes = []
        if len(poly.interiors) > 0:
            mask = [True if shapely.is_ccw(h) else False for h in poly.interiors]
            if sum(mask) > 0:
                # reverse linearring it is ccw defined
                for i, m in enumerate(mask):
                    if not m:
                        holes.append(poly.interiors[i])
                    else:
                        holes.append(shapely.reverse(poly.interiors[i]))
            else:
                holes = poly.interiors

        return shapely.Polygon(shell=shell, holes=holes)

    def _reduce(self, origin: np.ndarray):
        """Reduces coordinates by origin"""

        shell = (np.stack(self._geometry.exterior.coords.xy).T - origin).tolist()

        holes = []
        for hole in [np.stack(geom.coords.xy).T for geom in self._geometry.interiors]:
            holes.append((hole - origin).tolist())

        self._geometry = shapely.geometry.Polygon(shell=shell, holes=holes)

    @property
    def get_geometry(self) -> shapely.geometry.Polygon:
        return self._geometry

    def get_exterior_points(self, exclude_last_point: bool = True) -> np.ndarray:
        """
        Returns vertices of exterior boundary

        Parameters
        ----------
        exclude_last_point :
            Whether to exclude last point (which is identical with first point)

        Returns
        -------
        _ :
        """
        points = np.stack(self._geometry.exterior.coords.xy).T
        if exclude_last_point:
            points = points[:-1]

        return points

    @property
    def n_interiors(self) -> int:
        """Returns number boundaries (holes)"""
        return len(self._geometry.interiors)

    def get_interior_points(self, exclude_last_point: bool = True) -> list[np.ndarray]:
        """
        Returns vertices of all interior boundaries

        Parameters
        ----------
        exclude_last_point :
            Whether to exclude last point (which is identical with first point)

        Returns
        -------
        _ :
        """
        points = [np.stack(geom.coords.xy).T for geom in self._geometry.interiors]

        if exclude_last_point:
            points = [p[:-1] for p in points]

        return points

    @property
    def get_area(self) -> float:
        """Returns area"""
        return self._geometry.area
