import logging
import pyvista as pv
import pandas as pd
import numpy as np
import shapely
import itertools

from .polygon import Area

logger = logging.getLogger(__name__)


class Mesh(object):
    """
    Class representing a surface triangle mesh

    Parameters
    ----------
    data : np.ndarray | list | pv.PolyData
        Raster to be converted into a triangle mesh

    Attributes
    ----------
    mesh : pv.PolyData
        Mesh triangulated from input points
    min_values : np.ndarray
        Min values along each coordinate dimension (x, y, z)
    max_values : np.ndarray
        Max values along each coordinate dimension (x, y, z)
    """

    def __init__(self, data: np.ndarray | list | pv.PolyData | pd.DataFrame):
        if isinstance(data, pv.PolyData):
            self.mesh = data
        else:
            self.mesh = self._from_points(data)
        self.min_values = self.mesh.points.min(axis=0)
        self.max_values = self.mesh.points.max(axis=0)

    def _from_points(self, pts: np.ndarray | list) -> pv.PolyData:
        assert isinstance(pts, (np.ndarray, list))

        if isinstance(pts, list):
            pts = np.ndarray(pts)

        assert pts.ndim == 2
        assert pts.shape[1] == 3

        return pv.PolyData(pts).delaunay_2d()

    def decimate(self, max_height_error: float, grid_size: float, max_edge_len: float = 0) -> "Mesh":
        """
        Decimate number of triangle of this surface.

        Note:
        -----
        If angle between the normals of two neighboring triangles > max_normal_angle, then
        an edge exists.

        max_normal_angle = min(2 * np.rad2deg(np.arctan(max_height_error / grid_size)), 45)

        Parameters
        ----------
        max_height_error : float
            Maximum allowed height error in metres
            Is used to calculate the max allowed angle between neighboring triangles.
        grid_size : float
            Grid size of raster points.
            Is used to calculate the max allowed angle between neighboring triangles.
        max_edge_len : float; default = 0
            If specified, edges longer than this parameter are split in half.
        """
        # calcualte max normal angle between to neighbouring triangles.
        # if normal angle > max normal angle an edge exists
        max_normal_angle = min(2 * np.rad2deg(np.arctan(max_height_error / grid_size)), 45)

        mesh_deci = self.mesh.decimate_pro(
            reduction=0.99,
            feature_angle=max_normal_angle,
            splitting=False,
            preserve_topology=True,
            boundary_vertex_deletion=False,
        )

        if max_edge_len > 0:
            mesh_deci = mesh_deci.subdivide_adaptive(max_edge_len=max_edge_len)
        return Mesh(mesh_deci)

    def _sort_pts_2d(self, pts) -> np.ndarray:
        """Sorts points based on their 2D coordinates"""

        return pts[np.lexsort((pts[:, 0], pts[:, 1]))]

    def _resort_pts_2d(self, pts_sorted: np.ndarray, pts_unsorted: np.ndarray) -> np.ndarray:
        """Resorts points based on 2D coordinates to have the same order"""
        assert pts_sorted.ndim == 2 & pts_unsorted.ndim == 2 
        assert pts_sorted.shape[0] == pts_unsorted.shape[0] 

        # add index to sorted points
        pts_sorted_ind = np.hstack((pts_sorted, np.arange(pts_sorted.shape[0]).reshape(pts_sorted.shape[0], 1)))
        return self._sort_pts_2d(pts_unsorted)[np.argsort(self._sort_pts_2d(pts_sorted_ind)[:, -1].astype(int))]

    def project_points_on_surface(self, pts_2d: np.ndarray | list) -> np.ndarray:
        """
        Projects 2d points on to surface

        Parameters
        ----------
        pts_2d: np.ndarray | list
            2D points to be projected on surface

        Returns
        -------
        _ : np.ndarray
        """
        assert isinstance(pts_2d, (np.ndarray, list))

        if isinstance(pts_2d, list):
            pts_2d = np.ndarray(pts_2d)

        assert pts_2d.ndim == 2
        assert pts_2d.shape[1] == 2

        assert len(set(tuple(p) for p in pts_2d)) == pts_2d.shape[0], "Only unique coord tuples can be converted"
        pts_3d = self.mesh.multi_ray_trace(
            np.hstack((pts_2d, np.zeros((pts_2d.shape[0], 1)))),
            np.array([[0, 0, 1]] * pts_2d.shape[0]),
            first_point=True,
        )[0]

        offset = 0.00001
        while pts_3d.shape[0] != pts_2d.shape[0] and offset < 0.0001:
            pts_2d_approx = pts_2d + offset
            pts_3d = self.mesh.multi_ray_trace(
                np.hstack((pts_2d_approx, np.zeros((pts_2d_approx.shape[0], 1)))),
                np.array([[0, 0, 1]] * pts_2d_approx.shape[0]),
                first_point=True,
            )[0]
            pts_3d[:,:2] -= offset
            offset = offset + 0.00001

        return self._resort_pts_2d(pts_2d, pts_3d)

    def calculate_edge_segment(self, p_start: np.ndarray, p_end: np.ndarray, th_line_p: float = 1e-8) -> list:
        """Slice surface along axis and return all edge points in correct order"""
        assert p_start.ndim == 1 and p_end.ndim == 1

        vec = p_end - p_start
        n_vec = np.array([-vec[1], vec[0], 0], dtype=np.float64)
        n_vec = n_vec / np.linalg.norm(n_vec)

        plane_slice = self.mesh.slice(normal=n_vec.tolist(), origin=p_start[:2].tolist() + [0])

        # filter points within bb
        pts_on_edge = plane_slice.points[
            np.where(
                (plane_slice.points[:, 0] >= min(p_start[0], p_end[0]))
                & (plane_slice.points[:, 0] <= max(p_start[0], p_end[0]))
                & (plane_slice.points[:, 1] >= min(p_start[1], p_end[1]))
                & (plane_slice.points[:, 1] <= max(p_start[1], p_end[1]))
            )[0]
        ]

        return pts_on_edge[np.argsort(np.linalg.norm(pts_on_edge[:, :2] - p_start[:2], axis=1))].tolist()

    def slice_along_boundary(self, vertices_2d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Slices along boundary"""
        vertices_3d = self.project_points_on_surface(vertices_2d)

        edge_points = []
        for i in range(vertices_3d.shape[0]):
            p_start = vertices_3d[i, :]
            p_end = vertices_3d[(i + 1) % vertices_3d.shape[0], :]
            pts_on_edge = self.calculate_edge_segment(p_start, p_end)
            edge_points += [p_start.tolist()] + pts_on_edge

        edge_points = np.vstack(edge_points)
        line_definition = np.array(list(range(edge_points.shape[0])) + [0])

        return edge_points, line_definition

    def _filter_triangles(self, mesh: pv.PolyData, area: Area) -> np.ndarray:
        """
        Filters triangles based on geometry object.

        Parameters
        ----------
        mesh : pv.PolyData
            Mesh constructed by constrained 2d-Delaunay triangulatiion
            form points within area and 3D lines along boundaries.
        points_within_area :  np.ndarray
            Points within area of form [x, y, z] (N x 3).


        Returns
        -------
        _ :  np.ndarray
            Triangle definition as expected by pyvista.
            [num_vertices, ind1, ind2, ind3]

        """
        triangle_mask = []

        triangles = np.array(mesh.faces.reshape(mesh.n_faces_strict, 4)[:, 1:])
        vertices = mesh.points[:, :2]

        test_geom_area = area._geometry.buffer(0.0005)
        test_geom_boundary = shapely.LinearRing(area.get_exterior_points(exclude_last_point=False)).buffer(
            distance=0.0005
        )

        for triangle in triangles:
            points = vertices[triangle, :]
            tri = shapely.Polygon(points.tolist() + [points[0].tolist()])
            center_of_mass = shapely.Point(points.mean(axis=0).tolist())

            triangle_mask.append(
                1 if tri.within(test_geom_area) and not center_of_mass.within(test_geom_boundary) else 0
            )

        tri_filtered = triangles[np.array(triangle_mask, dtype=bool), :]
        tri_filtered = np.hstack((np.full((tri_filtered.shape[0], 1), 3), tri_filtered)).flatten()

        return tri_filtered

    def clip_mesh_by_area(self, area: Area, points_within_area: np.ndarray | pd.DataFrame) -> "Mesh":
        """
        Clips mesh by provided area.

        For each boundary (extrior and interior) the following calculations are performed:
        1. Vertices are projected on to 3d surface of the mesh
        2. For each line segment a vertical plane is defined and the surface is sliced along it
            2.1. Intersection points between vertices of the line segment are filtered and ordered
        3. Intersection points and line definition are added to the surface
        4. Surface is retriangulated
        5. Surface is clipped along boundaries of area by deleting triangles outside the boundary

        Parameters
        ----------
        area : Area
            Area to clip mesh with
        points_within_area :  np.ndarray
            Points within area of form [x, y, z] (N x 3).

        Returns
        -------
        _ : Mesh
            Clipped mesh
        """
        boundaries = [area.get_exterior_points(exclude_last_point=True)]

        if area.n_interiors > 0:
            boundaries += area.get_interior_points(exclude_last_point=True)

        # slice along boundary for all geometries included in area
        pts_boundaries = []
        lines = []
        for b_pts in boundaries:
            res = self.slice_along_boundary(b_pts)
            pts_boundaries.append(res[0])
            lines.append(res[1])

        # Move to same for loop as above
        mesh_pts = points_within_area
        line_definitions = []
        for i in range(len(pts_boundaries)):
            l = lines[i] + mesh_pts.shape[0]
            line_definitions.append([len(l), *l.tolist()])
            mesh_pts = np.vstack((mesh_pts, pts_boundaries[i]))

        # create PolyData object (merge line definitions to a single list)
        data_area = pv.PolyData(mesh_pts, lines=list(itertools.chain(*line_definitions)))

        # mesh it with preserving extracted 3D boundaries
        mesh = data_area.delaunay_2d(edge_source=data_area)

        # delete all triangles that lie outside of the boundary
        mesh.faces = self._filter_triangles(mesh, area)

        return Mesh(mesh)

    @property
    def n_triangles(self) -> int:
        """Returns number of triangles"""
        return self.mesh.n_faces_strict

    @property
    def _faces(self) -> np.ndarray:
        """Returns faces as array of form (N x 3)"""
        return self.mesh.faces.reshape(self.n_triangles, 4)[:, 1:]

    @property
    def _points(self) -> np.ndarray:
        """Returns points as array"""
        return self.mesh.points

    def _area_triangle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:

        return np.abs((p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2)

    @property
    def get_area_2d(self) -> float:
        """
        Calculates 2d area covered by this mesh

        The planar area of all triangles of this mesh is calculated and summed up.
        """
        points = self._points
        faces = self._faces

        area = 0
        for face in faces:
            area += self._area_triangle(*points[face])
        return area

    def check_area_consistency(self, area: float, treshold: float) -> bool:
        """
        Checks if 2d area covered by this mesh differs less than the provided treshhold from the area provided.
        """
        logger.debug(f"area consistency: {np.abs(self.get_area_2d - area)}")
        if np.abs(self.get_area_2d - area) < treshold:
            return True
        else:
            return False

    def get_data(self) -> tuple[list[list[float]], list[list[int]]]:
        """
        Returns points and triangle indices of surface represented by this object.

        Returns
        -------
        _ : tuple[list[list[float]], list[list[int]]]
            Point list of form [x, y, z] and triangle list of form [v1, v2, v3]
        """
        return self._points.tolist(), self._faces.tolist()
