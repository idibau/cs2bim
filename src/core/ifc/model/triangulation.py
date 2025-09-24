from config.configuration import config
from config.element_entity_type import ElementEntityType
from config.triangulation_representation_type import TriangulationRepresentationType
from core.ifc.model.element import Element
from core.ifc.model.geometry.brep import Brep
from core.ifc.model.geometry.tessellation import Tessellation


class Triangulation(Element):

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
            product_definition_shape = tessellation.map_to_ifc(ifc_file, ifc_representation_sub_context, ifc_style)
        elif representation_type == TriangulationRepresentationType.BREP:
            brep = Brep(self.triangles)
            product_definition_shape = brep.map_to_ifc(ifc_file, ifc_representation_sub_context, ifc_style)
        else:
            raise NotImplementedError(f"building step for representation type {representation_type.name} not implemented")

        ifc_local_placement = ifc_file.create_ifc_local_placement((0.0, 0.0, 0.0))
        if entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
            ifc_element = ifc_file.create_ifc_geographic_element(ifc_local_placement, product_definition_shape)
        else:
            raise NotImplementedError(
                f"building step for featuretype entity type {entity_type.name} not implemented for 2d featuretypes")

        self.set_ifc_attributes(ifc_file, ifc_element)
        self.set_ifc_properties(ifc_file, ifc_element)

        return ifc_element
