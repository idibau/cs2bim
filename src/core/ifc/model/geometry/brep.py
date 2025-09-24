class Brep:

    def __init__(self, faces):
        self.faces = faces

    def map_to_ifc(self, ifc_file, ifc_representation_sub_context, ifc_style):
        vertex_dict = {}
        ifc_faces = []
        for polygon in self.faces:
            vertices = []
            for vertex in polygon:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = ifc_file.create_ifc_cartesian_point(vertex)
                vertices.append(vertex_dict[vertex])
            ifc_face = ifc_file.create_ifc_face(vertices)
            ifc_faces.append(ifc_face)
        ifc_face_set = ifc_file.create_ifc_faceted_brep(ifc_faces)
        ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context, "Brep",
                                                                                ifc_face_set)
        return product_definition_shape
