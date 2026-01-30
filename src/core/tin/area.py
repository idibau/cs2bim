import logging
import numpy as np
import shapely
import triangle as tr
from shapely import Point, LineString, MultiLineString
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import LinearRing, Polygon

from config.configuration import config
from core.tin.grid import Grid
from core.tin.raster_points import RasterPoints

logger = logging.getLogger(__name__)


class Area:
    """Class representing a polygonal area including holes if present."""

    def __init__(self, polygon: BaseGeometry):
        if not isinstance(polygon, shapely.Polygon):
            raise ValueError(f"{type(polygon).__name__} not supported")
        self.polygon = polygon
        self.raster_points_within = []
        self.raster_points_buffer = []

    def add_raster_points(self, raster_points: RasterPoints):
        rpb = raster_points.within(self.polygon, 2 * config.tin.grid_size.value)
        if rpb is not None:
            self.raster_points_buffer.extend(rpb)
        rpw = raster_points.within(self.polygon, 0)
        if rpw is not None:
            self.raster_points_within.extend(rpw)

    def create_mesh(self):
        if not self.raster_points_buffer:
            raise Exception("No raster points found for area")

        self.raster_points_buffer = np.vstack(self.raster_points_buffer)
        if self.raster_points_within:
            self.raster_points_within = np.vstack(self.raster_points_within)

        grid = Grid(self.raster_points_buffer)

        exterior = self.densify_linearring_by_raster(self.polygon.exterior, grid)
        interiors = [self.densify_linearring_by_raster(interior, grid) for interior in
                     self.polygon.interiors]
        points_within_2d = [arr[:2] for arr in self.raster_points_within]

        vertices, faces = self.constrained_delaunay_2d(exterior, interiors, points_within_2d)

        vertices_z = []
        for vertex in vertices:
            z = grid.get_height_for_vertex(np.array(vertex))
            vertices_z.append([vertex[0], vertex[1], z])

        vertices_z = np.array(vertices_z)

        return vertices_z, faces

    def densify_linearring_by_raster(self, linear_ring, grid):
        coords = linear_ring.coords

        minx, miny, maxx, maxy = linear_ring.bounds

        x_grid_lines = [LineString([(x, miny), (x, maxy)]) for x in grid.unique_x]
        y_grid_lines = [LineString([(minx, y), (maxx, y)]) for y in grid.unique_y]
        grid_lines = MultiLineString([*x_grid_lines, *y_grid_lines])

        points = []
        for i in range(len(coords) - 1):
            start, end = Point(coords[i]), Point(coords[i + 1])
            segment = LineString([start, end])
            inter = segment.intersection(grid_lines)
            if inter.geom_type == 'Point':
                intersection_points = [inter]
            elif inter.geom_type == "MultiPoint":
                intersection_points = inter.geoms
            else:
                intersection_points = []
            intersection_points_sorted = sorted(intersection_points, key=lambda p: p.distance(start))
            points.append(start)
            points.extend(intersection_points_sorted)

        return LinearRing(points)

    def constrained_delaunay_2d(self, exterior, interiors, points_within):
        segments = []
        vertices = []

        offset = 0
        vertices.extend([list(pt) for pt in exterior.coords[:-1]])
        n_exterior = len(exterior.coords[:-1])
        exterior_segment = np.column_stack([
            np.arange(n_exterior),
            np.append(np.arange(1, n_exterior), offset)
        ]).tolist()
        segments.extend(exterior_segment)
        offset = offset + n_exterior
        for interior in interiors:
            vertices.extend([list(pt) for pt in interior.coords[:-1]])
            n_interior = len(interior.coords[:-1])
            interior_segment = np.column_stack([
                np.arange(offset, offset + n_interior),
                np.append(np.arange(offset + 1, offset + n_interior), offset)
            ]).tolist()
            segments.extend(interior_segment)
            offset = offset + n_interior

        vertices.extend(points_within)

        holes = []
        for interior in interiors:
            point = Polygon(interior).representative_point()
            holes.append(list(*point.coords))

        triangulation_input = {"vertices": vertices, "segments": segments}
        if holes:
            triangulation_input["holes"] = holes
        result = tr.triangulate(triangulation_input, "p")
        return result["vertices"], result["triangles"]
