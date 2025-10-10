from config.projection_entity import ProjectionEntity
from core.ifc.model.feature_element import FeatureElement
from core.ifc.model.tessellation import Tessellation


class Projection(FeatureElement):

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

    def map_to_ifc(self, ifc_file, entity, ifc_representation_sub_context, ifc_style):
        tessellation = Tessellation(self.triangles)
        ifc_face_set = tessellation.map_to_ifc(ifc_file)
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Tessellation", [ifc_face_set])
        ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        ifc_local_placement = ifc_file.create_ifc_local_placement((0.0, 0.0, 0.0))
        if entity == ProjectionEntity.IFC_GEOGRAPHIC_ELEMENT:
            ifc_element = ifc_file.create_ifc_geographic_element(ifc_local_placement, ifc_product_definition_shape)
        else:
            raise NotImplementedError(
                f"building step for feature type entity {entity.name} not implemented for clipped terrain feature types")
        return ifc_element
