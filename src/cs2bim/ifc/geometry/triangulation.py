import logging
from stl import mesh

from cs2bim.ifc.geometry.geometry import Geometry

logger = logging.getLogger(__name__)


class Triangulation(Geometry):
    """
    Holds a list of triangles that define a mesh

    Attributes
    ----------
    triangles : list[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
            ]
        ]
        List of triangle coordinate tuples

    """

    def __init__(self) -> None:
        self.triangles = []

    def load_from_stl(self, file_name: str) -> None:
        """Loads trianglualtion from an stl file"""
        logger.debug(f"read triangulation from file '{file_name}'")
        self.triangles = []
        self.mesh = mesh.Mesh.from_file(file_name)
        v0 = list(map(Triangulation._create_tuple, self.mesh.v0))
        v1 = list(map(Triangulation._create_tuple, self.mesh.v1))
        v2 = list(map(Triangulation._create_tuple, self.mesh.v2))
        self.triangles = list(zip(v0, v1, v2))
        logger.debug("completed read triangulation")

    def load_from_points_and_faces(self, data: tuple[list[list[float]], list[list[int]]]):
        """Takes a list of points and a list of indexes to build the triangulation"""
        self.triangles = []
        point_list = data[0]
        index_list = data[1]
        for triangle in index_list:
            p1 = Triangulation._create_tuple(point_list[triangle[0]])
            p2 = Triangulation._create_tuple(point_list[triangle[1]])
            p3 = Triangulation._create_tuple(point_list[triangle[2]])
            self.triangles.append((p1, p2, p3))

    @classmethod
    def _create_tuple(cls, l: list) -> tuple[float, float, float]:
        return (float(l[0]), float(l[1]), float(l[2]))
