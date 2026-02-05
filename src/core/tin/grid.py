import logging

import numpy as np
from shapely import MultiLineString, LineString, Point

logger = logging.getLogger(__name__)


class Grid:
    """Grid structure for managing raster points and performing interpolation for areas"""

    def __init__(self, raster_points: np.ndarray):
        self.raster_points = raster_points
        self.x_coords = sorted(np.unique(raster_points[:, 0]))
        self.y_coords = sorted(np.unique(raster_points[:, 1]))

        x_to_idx = {x: i for i, x in enumerate(self.x_coords)}
        y_to_idx = {y: j for j, y in enumerate(self.y_coords)}

        self.grid = np.full((len(self.y_coords), len(self.x_coords)), -1, dtype=int)

        for pt_idx, pt in enumerate(raster_points):
            x, y = pt[0], pt[1]
            i = x_to_idx[x]
            j = y_to_idx[y]
            self.grid[j, i] = pt_idx

        min_x = np.min(self.x_coords)
        min_y = np.min(self.y_coords)
        max_x = np.max(self.x_coords)
        max_y = np.max(self.y_coords)

        self.x_grid_lines = MultiLineString([LineString([(x, min_y), (x, max_y)]) for x in self.x_coords])
        self.y_grid_lines = MultiLineString([LineString([(min_x, y), (max_x, y)]) for y in self.y_coords])

        diagonal_lines = []
        for i in range(len(self.x_coords) - 1):
            for j in range(len(self.y_coords) - 1):
                diag = LineString([(self.x_coords[i], self.y_coords[j + 1]), (self.x_coords[i + 1], self.y_coords[j])])
                diagonal_lines.append(diag)
        self.xy_grid_lines = MultiLineString(diagonal_lines)

    def get_intersection_points_with_line(self, start: Point, end: Point):
        """Returns intersection points between a line and grid lines, sorted by distance from start."""
        line = LineString([start, end])

        def get_intersection_gridlines(line: LineString, grid_lines: MultiLineString):
            inter = line.intersection(grid_lines)
            if inter.geom_type == 'Point':
                return [inter]
            elif inter.geom_type == "MultiPoint":
                return list(inter.geoms)
            else:
                return []

        intersection_points = get_intersection_gridlines(line, self.x_grid_lines)
        intersection_points.extend(get_intersection_gridlines(line, self.y_grid_lines))
        intersection_points.extend(get_intersection_gridlines(line, self.xy_grid_lines))
        return sorted(intersection_points, key=lambda p: p.distance(start))

    def get_height_for_vertex(self, vertex: np.ndarray):
        """Calculates interpolated height for a vertex anywhere on the grid."""
        i = np.searchsorted(self.x_coords, vertex[0], side='right') - 1
        j = np.searchsorted(self.y_coords, vertex[1], side='right') - 1

        i00 = self.grid[j, i]
        i10 = self.grid[j, i + 1]
        i01 = self.grid[j + 1, i]
        i11 = self.grid[j + 1, i + 1]

        if i00 == -1 or i10 == -1 or i01 == -1 or i11 == -1:
            raise Exception(f"raster points missing for vertex {vertex}")

        p00 = self.raster_points[i00]
        p10 = self.raster_points[i10]
        p01 = self.raster_points[i01]
        p11 = self.raster_points[i11]

        dx = self.x_coords[i + 1] - self.x_coords[i]
        dy = self.y_coords[j + 1] - self.y_coords[j]

        u = (vertex[0] - self.x_coords[i]) / dx
        v = (vertex[1] - self.y_coords[j]) / dy

        if u + v <= 1:
            return self.interpolate(vertex, np.array([p00, p10, p01]))
        else:
            return self.interpolate(vertex, np.array([p11, p10, p01]))

    def interpolate(self, v: np.ndarray, triangle: np.ndarray):
        """Performs barycentric interpolation for a 2D point within a 3D triangle."""
        (x, y) = v
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = triangle

        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        w1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
        w2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
        w3 = 1 - w1 - w2

        z = w1 * z1 + w2 * z2 + w3 * z3
        return z
