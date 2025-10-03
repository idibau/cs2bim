class Brep:

    def __init__(self, faces):
        self.faces = faces

    def map_to_ifc(self, ifc_file):
        vertex_dict = {}
        ifc_faces = []
        for polygon in self.faces:
            vertices = []
            for vertex in polygon:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = ifc_file.create_ifc_cartesian_point(vertex)
                vertices.append(vertex_dict[vertex])
            ifc_poly_loop = ifc_file.create_ifc_poly_loop(vertices)
            ifc_face = ifc_file.create_ifc_face(ifc_poly_loop, [])
            ifc_faces.append(ifc_face)
        ifc_face_set = ifc_file.create_ifc_faceted_brep(ifc_faces)
        return ifc_face_set
