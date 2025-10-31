from core.ifc.model.gml.namespace import namespace
from core.ifc.model.gml.pos_list import PosList


class Polygon:
    def __init__(self):
        super().__init__()
        self.exterior = PosList()
        self.interior = []

    def from_gml(self, gml, project_origin: tuple[float, float, float]):
        pos_list_exterior = gml.xpath("./gml:exterior//gml:posList", namespaces=namespace)
        if len(pos_list_exterior) != 1:
            raise ValueError("Polygon expects exactly one exterior posList")
        self.exterior.from_gml(pos_list_exterior[0], project_origin)
        for pos_list_gml in gml.xpath("./gml:interior//gml:posList", namespaces=namespace):
            pos_list = PosList()
            pos_list.from_gml(pos_list_gml, project_origin)
            self.interior.append(pos_list)

    def create_ifc_indexed_polygonal_face(self, ifc_file, coordinates):
        exterior_indices = []
        for vertex in self.exterior.coordinates:
            if not vertex in coordinates:
                coordinates[vertex] = len(coordinates) + 1
            exterior_indices.append(coordinates[vertex])

        interior_indices_list = []
        for interior in self.interior:
            polygon_indices = []
            for vertex in interior.coordinates:
                if not vertex in coordinates:
                    coordinates[vertex] = len(coordinates) + 1
                polygon_indices.append(coordinates[vertex])
            interior_indices_list.append(polygon_indices)

        if interior_indices_list:
            return ifc_file.create_ifc_indexed_polygonal_face_with_voids(exterior_indices, interior_indices_list)
        else:
            return ifc_file.create_ifc_indexed_polygonal_face(exterior_indices)

    def create_ifc_face(self, ifc_file):
        vertex_dict = {}
        vertices = []
        for vertex in self.exterior.coordinates:
            if vertex not in vertex_dict:
                vertex_dict[vertex] = ifc_file.create_ifc_cartesian_point(vertex)
            vertices.append(vertex_dict[vertex])
        exterior_ifc_poly_loop = ifc_file.create_ifc_poly_loop(vertices)
        interior_ifc_poly_loops = []
        for interior in self.interior:
            vertices = []
            for vertex in interior:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = ifc_file.create_ifc_cartesian_point(vertex)
                vertices.append(vertex_dict[vertex])
            interior_ifc_poly_loops.append(ifc_file.create_ifc_poly_loop(vertices))
        ifc_face = ifc_file.create_ifc_face(exterior_ifc_poly_loop, interior_ifc_poly_loops)
        return ifc_face
