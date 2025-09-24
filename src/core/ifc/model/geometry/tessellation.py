class Tessellation:

    def __init__(self, faces):
        self.faces = faces

    def map_to_ifc(self, ifc_file, ifc_representation_sub_context, ifc_style):
        vertices_dict = {}
        vertices = []
        for triangle in self.faces:
            for vertex in triangle:
                if not vertex in vertices_dict:
                    vertices_dict[vertex] = len(vertices) + 1
                    vertices.append(vertex)
        point_index_list = [tuple(vertices_dict[v] for v in triangle) for triangle in self.faces]
        ifc_face_set = ifc_file.create_ifc_triangulated_face_set(vertices, point_index_list)
        ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                "Tesselation", ifc_face_set)
        return product_definition_shape