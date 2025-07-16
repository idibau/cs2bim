import numpy as np
import shapely


class Area(object):
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
    wkt_str : str
        WKT string defining the polygon
    origin : np.ndarray of form [x, y]
        Origin to reduce coordinate values
    """

    def __init__(self, wkt_str: str, origin: np.ndarray = np.zeros((2,))) -> None:
        assert isinstance(wkt_str, str)

        self._geometry = self._check_polygon_definition(shapely.from_wkt(wkt_str))

        assert origin.shape == (2,)
        if not np.allclose(origin, np.zeros((2,))):
            self._reduce(origin)

    def _check_polygon_definition(self, poly: shapely.Polygon):
        """
        Checks polygon definition and creates a geometry object.

        According to WKT-Standard the exterior of a polygon (hull / shell)
        has to be defined counter-clockwise (ccw) while present interiors (holes)
        have to defined clockwise.

        Parameters
        ----------
        poly : shapely.Polygon
            Polygon to be checked

        Returns
        -------
        _ : shapely.Polygon
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

    def _reduce(self, origin):
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
        exclude_last_point : bool; default = True
            Whether to exclude last point (which is identical with first point)

        Returns
        -------
        _ : np.ndarray
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
        exclude_last_point : bool; default = True
            Whether to exclude last point (which is identical with first point)

        Returns
        -------
        _ : list[np.ndarray]
        """
        points = [np.stack(geom.coords.xy).T for geom in self._geometry.interiors]

        if exclude_last_point:
            points = [p[:-1] for p in points]

        return points

    @property
    def get_area(self) -> float:
        """Returns area"""
        return self._geometry.area
