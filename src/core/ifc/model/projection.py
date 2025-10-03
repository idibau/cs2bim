from config.configuration import config
from config.projection_entity_type import ProjectionEntityType
from config.triangulation_representation_type import TriangulationRepresentationType
from core.ifc.model.element import Element
from core.ifc.model.brep import Brep
from core.ifc.model.tessellation import Tessellation


class Projection(Element):

    def __init__(self, data: tuple[list[list[float]], list[list[int]]]) -> None:
        super().__init__()
        self.triangles = []
        point_list = data[0]
        index_list = data[1]
        for triangle in index_list:
            p1 = self._create_tuple(point_list[triangle[0]])
            p2 = self._create_tuple(point_list[triangle[1]])
            p3 = self._create_tuple(point_list[triangle[2]])
            self.triangles.append((p1, p2, p3))

    @classmethod
    def _create_tuple(cls, l: list) -> tuple[float, float, float]:
        return float(l[0]), float(l[1]), float(l[2])

    def map_to_ifc(self, ifc_file, entity_type, ifc_representation_sub_context, ifc_style):
        representation_type = config.ifc.triangulation_representation_type
        if representation_type == TriangulationRepresentationType.TESSELLATION:
            tessellation = Tessellation(self.triangles)
            ifc_face_set = tessellation.map_to_ifc(ifc_file)
            ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Tessellation", [ifc_face_set])
        elif representation_type == TriangulationRepresentationType.BREP:
            brep = Brep(self.triangles)
            ifc_face_set = brep.map_to_ifc(ifc_file)
            ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Brep", [ifc_face_set])
        else:
            raise NotImplementedError(
                f"building step for representation type {representation_type.name} not implemented")
        ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        ifc_local_placement = ifc_file.create_ifc_local_placement((0.0, 0.0, 0.0))
        if entity_type == ProjectionEntityType.IFC_GEOGRAPHIC_ELEMENT:
            ifc_element = ifc_file.create_ifc_geographic_element(ifc_local_placement, ifc_product_definition_shape)
        else:
            raise NotImplementedError(
                f"building step for feature type entity type {entity_type.name} not implemented for clipped terrain feature typees")

        self.set_ifc_attributes(ifc_file, ifc_element)
        self.set_ifc_properties(ifc_file, ifc_element)

        return ifc_element
