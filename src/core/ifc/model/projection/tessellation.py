from ifcopenshell import entity_instance
from shapely import Point

from core.ifc.ifc_file import IfcFile


class Tessellation:

    def __init__(self, faces: list[tuple[Point, Point, Point]]):
        self.faces = faces

    def map_to_ifc(self, ifc_file: IfcFile) -> entity_instance:
        vertices_dict = {}
        vertices = []
        indices = []
        for triangle in self.faces:
            triangle_indices = []
            for vertex in triangle:
                if vertex not in vertices_dict:
                    vertices_dict[vertex] = len(vertices) + 1
                    vertices.append(vertex)
                triangle_indices.append(vertices_dict[vertex])
            indices.append(triangle_indices)
        ifc_face_set = ifc_file.create_ifc_triangulated_face_set(vertices, indices)
        return ifc_face_set