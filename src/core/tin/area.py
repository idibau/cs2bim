import logging

import numpy as np
import pyvista as pv
import shapely
from shapely import Point, MultiPoint
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.ops import orient

from config.configuration import config
from core.tin.grid import Grid
from core.tin.raster_points import RasterPoints

logger = logging.getLogger(__name__)


class Area:
    """Class representing a polygonal area including holes if present."""

    def __init__(self, polygon: BaseGeometry):
        if not isinstance(polygon, shapely.Polygon):
            raise ValueError(f"{type(polygon).__name__} not supported")
        self.polygon = orient(polygon, sign=1.0)
        self.raster_points_within = []
        self.raster_points_buffer = []

    def add_raster_points(self, raster_points: RasterPoints):
        rpb = raster_points.within(self.polygon, 3 * config.tin.grid_size.value)
        if rpb is not None:
            self.raster_points_buffer.extend(rpb)
        rpw = raster_points.within(self.polygon, -0.001)
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
            z = grid.get_height_for_vertex(np.array(vertex[:-1]))
            vertices_z.append([vertex[0], vertex[1], z])
        vertices_z = np.array(vertices_z)

        return self.decimate(vertices_z, faces)

    def densify_linearring_by_raster(self, linear_ring, grid):
        coords = linear_ring.coords
        points = []
        for i in range(len(coords) - 1):
            start, end = Point(coords[i]), Point(coords[i + 1])
            intersection_points_sorted = grid.get_intersection_points_with_line(start, end)
            points.append(start)
            points.extend(intersection_points_sorted)

        deduplicated_list = list({p.coords[0]: p for p in MultiPoint(points).geoms}.values())
        return LinearRing(deduplicated_list)

    def constrained_delaunay_2d(self, exterior, interiors, points_within):
        def to_3d(pts):
            return np.hstack([pts, np.zeros((pts.shape[0], 1))])

        exterior_points_3d = to_3d(np.array(exterior.coords))
        interiors_points_3d = [to_3d(np.array(interior.coords)) for interior in interiors]
        points_within_3d = to_3d(np.array(points_within)) if len(points_within) > 0 else np.empty((0, 3))

        all_points = np.vstack([exterior_points_3d] + interiors_points_3d + [points_within_3d])

        lines = []
        offset = 0
        for loop in [exterior_points_3d] + interiors_points_3d:
            n = len(loop)
            for i in range(n):
                lines.append([2, offset + i, offset + ((i + 1) % n)])
            offset += n

        edge_src = pv.PolyData(all_points[:offset])
        edge_src.lines = np.hstack(lines)

        mesh = pv.PolyData(all_points).delaunay_2d(edge_source=edge_src, tol=0)

        faces_raw = mesh.faces.reshape(-1, 4)[:, 1:]
        keep_indices = []

        for i, face_idx in enumerate(faces_raw):
            tri_coords = mesh.points[face_idx][:, :2]
            tri_poly = Polygon(tri_coords)
            if tri_poly.within(self.polygon.buffer(0.01)):
                keep_indices.append(i)

        final_mesh = mesh.extract_cells(keep_indices).extract_surface()
        return final_mesh.points, final_mesh.faces.reshape(-1, 4)[:, 1:]

    def decimate(self, vertices, faces):
        pv_faces = np.insert(faces, 0, 3, axis=1)
        polydata = pv.PolyData(vertices, pv_faces)
        max_normal_angle = min(2 * np.rad2deg(np.arctan(config.tin.max_height_error / config.tin.grid_size)), 45)
        polydata.decimate_pro(
            reduction=0.99,
            feature_angle=max_normal_angle,
            splitting=False,
            preserve_topology=True,
            boundary_vertex_deletion=False,
            inplace=True
        )
        faces_flat = polydata.faces
        faces_2d = faces_flat.reshape(-1, 4)
        original_faces = faces_2d[:, 1:]
        return polydata.points, original_faces
