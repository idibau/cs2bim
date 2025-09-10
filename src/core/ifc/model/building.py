from config.element_entity_type import ElementEntityType
from core.ifc.model.element import Element
from core.ifc.model.geometry.brep import Brep


class BuildingPart(Element):

    def __init__(self, entity_type: ElementEntityType, faces, color):
        super().__init__()
        self.color = color
        self.faces = faces
        self.entity_type = entity_type

    def map_to_ifc(self, ifc_file, ifc_representation_sub_context):
        ifc_style = ifc_file.create_ifc_surface_style(self.color)
        brep = Brep(self.faces)
        product_definition_shape = brep.map_to_ifc(ifc_file, ifc_representation_sub_context, ifc_style)

        ifc_local_placement = ifc_file.create_ifc_local_placement((0.0, 0.0, 0.0))
        if self.entity_type == ElementEntityType.IFC_GEOGRAPHIC_ELEMENT:
            ifc_element = ifc_file.create_ifc_geographic_element(ifc_local_placement,
                                                                 product_definition_shape)
        elif self.entity_type == ElementEntityType.IFC_ROOF:
            ifc_element = ifc_file.create_ifc_roof(ifc_local_placement, product_definition_shape)
        elif self.entity_type == ElementEntityType.IFC_SLAB:
            ifc_element = ifc_file.create_ifc_slab(ifc_local_placement, product_definition_shape)
        elif self.entity_type == ElementEntityType.IFC_WALL:
            ifc_element = ifc_file.create_ifc_wall(ifc_local_placement, product_definition_shape)
        elif self.entity_type == ElementEntityType.IFC_SPACE:
            ifc_element = ifc_file.create_ifc_space(ifc_local_placement, product_definition_shape)
        else:
            raise Exception(
                f"building step for feature class entity type {self.entity_type.name} not implemented for building feature classes")
        self.set_ifc_attributes(ifc_element)
        self.set_ifc_properties(ifc_file, ifc_element)
        return ifc_element


class Building(Element):

    def __init__(self) -> None:
        super().__init__()
        self.building_parts: list[BuildingPart] = []

    def add_building_part(self, building_part: BuildingPart):
        self.building_parts.append(building_part)

    def map_to_ifc(self, ifc_file, ifc_local_placement, ifc_representation_sub_context):
        ifc_building_parts = []
        for building_part in self.building_parts:
            ifc_element = building_part.map_to_ifc(ifc_file, ifc_representation_sub_context)
            ifc_building_parts.append(ifc_element)

        ifc_building = ifc_file.create_ifc_building(ifc_local_placement)
        self.set_ifc_attributes(ifc_building)
        self.set_ifc_properties(ifc_file, ifc_building)

        ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_building_parts, ifc_building)
        return ifc_building