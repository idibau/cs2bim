from ifcopenshell import entity_instance
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.feature_element import FeatureElement
from core.ifc.model.projection.tessellation import Tessellation


class Projection(FeatureElement):

    def __init__(self, data: tuple[list[list[float]], list[list[int]]]):
        super().__init__()
        self.triangles = []
        point_list = data[0]
        index_list = data[1]
        for triangle in index_list:
            p1 = Point(point_list[triangle[0]])
            p2 = Point(point_list[triangle[1]])
            p3 = Point(point_list[triangle[2]])
            self.triangles.append((p1, p2, p3))

    def map_to_ifc(self, ifc_file: IfcFile, entity: str, placement_rel_to: entity_instance, ifc_representation_sub_context: entity_instance,
                   ifc_style: entity_instance) -> entity_instance:
        tessellation = Tessellation(self.triangles)
        ifc_face_set = tessellation.map_to_ifc(ifc_file)
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Tessellation", [ifc_face_set])
        ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        ifc_local_placement = ifc_file.create_relative_ifc_local_placement(placement_rel_to, Point(0, 0, 0))
        ifc_element = ifc_file.create_ifc_product(entity, ifc_local_placement, ifc_product_definition_shape)
        return ifc_element
