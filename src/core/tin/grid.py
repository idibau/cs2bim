import logging

import numpy as np

logger = logging.getLogger(__name__)


class Grid:

    def __init__(self, raster_points):
        self.raster_points = raster_points
        self.unique_x = np.unique(raster_points[:, 0])
        self.unique_y = np.unique(raster_points[:, 1])

        n_x = len(self.unique_x)
        n_y = len(self.unique_y)

        x_to_idx = {x: i for i, x in enumerate(self.unique_x)}
        y_to_idx = {y: j for j, y in enumerate(self.unique_y)}

        self.grid = np.full((n_y, n_x), -1, dtype=int)

        for pt_idx, pt in enumerate(raster_points):
            x, y = pt[0], pt[1]
            i = x_to_idx[x]
            j = y_to_idx[y]
            self.grid[j, i] = pt_idx

    def get_height_for_vertex(self, vertex):
        i = np.searchsorted(self.unique_x, vertex[0], side='right') - 1
        j = np.searchsorted(self.unique_y, vertex[1], side='right') - 1

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

        dx = self.unique_x[i + 1] - self.unique_x[i]
        dy = self.unique_y[j + 1] - self.unique_y[j]

        u = (vertex[0] - self.unique_x[i]) / dx
        v = (vertex[1] - self.unique_y[j]) / dy

        if u + v <= 1:
            return self.interpolate(vertex, [p00, p10, p01])
        else:
            return self.interpolate(vertex, [p11, p10, p01])

    def interpolate(self, v, triangle):
        (x, y) = v
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = triangle

        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        w1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
        w2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
        w3 = 1 - w1 - w2

        z = w1 * z1 + w2 * z2 + w3 * z3
        return z
