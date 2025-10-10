from config.building_part_entity import BuildingPartEntity
from core.ifc.model.element import Element
from core.ifc.model.feature_element import FeatureElement
from core.ifc.model.gml.gml_geometry import GmlGeometry


class BuildingPart:

    def __init__(self, entity: BuildingPartEntity, gml_geometry: GmlGeometry, color):
        super().__init__()
        self.color = color
        self.gml_geometry = gml_geometry
        self.entity = entity

    def map_to_ifc(self, ifc_file, ifc_representation_sub_context):
        ifc_style = ifc_file.create_ifc_surface_style(self.color)
        ifc_representations = self.gml_geometry.map_to_ifc(ifc_file, ifc_style)
        ifc_product_definition_shape = self.gml_geometry.create_ifc_product_definition_shape(ifc_file,
                                                                                             ifc_representation_sub_context,
                                                                                             ifc_representations)
        return self.create_ifc_element(ifc_file, ifc_product_definition_shape)

    def create_ifc_element(self, ifc_file, product_definition_shape):
        ifc_local_placement = ifc_file.create_ifc_local_placement((0.0, 0.0, 0.0))
        if self.entity == BuildingPartEntity.IFC_ROOF:
            ifc_element = ifc_file.create_ifc_roof(ifc_local_placement, product_definition_shape)
        elif self.entity == BuildingPartEntity.IFC_SLAB:
            ifc_element = ifc_file.create_ifc_slab(ifc_local_placement, product_definition_shape)
        elif self.entity == BuildingPartEntity.IFC_WALL:
            ifc_element = ifc_file.create_ifc_wall(ifc_local_placement, product_definition_shape)
        elif self.entity == BuildingPartEntity.IFC_BUILDING_ELEMENT_PROXY:
            ifc_element = ifc_file.create_ifc_building_element_proxy(ifc_local_placement, product_definition_shape)
        else:
            raise NotImplementedError(
                f"building step for feature type entity {self.entity.name} not implemented for building feature types")
        return ifc_element


class Building(FeatureElement):

    def __init__(self) -> None:
        super().__init__()
        self.building_parts: list[BuildingPart] = []

    def add_building_part(self, building_part: BuildingPart):
        self.building_parts.append(building_part)

    def map_to_ifc(self, ifc_file, ifc_local_placement, ifc_representation_sub_context):
        ifc_building = ifc_file.create_ifc_building(ifc_local_placement)
        ifc_elements = [building_part.map_to_ifc(ifc_file, ifc_representation_sub_context) for building_part in
                        self.building_parts]
        ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_elements, ifc_building)
        return ifc_building
