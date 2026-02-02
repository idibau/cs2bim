from ifcopenshell import entity_instance
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.gml_geometry import GmlGeometry
from core.ifc.model.feature_element import FeatureElement


class BuildingPart:

    def __init__(self, entity: str, gml_geometry: GmlGeometry, color):
        super().__init__()
        self.color = color
        self.gml_geometry = gml_geometry
        self.entity = entity

    def map_to_ifc(self, ifc_file: IfcFile, placement_rel_to: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        ifc_style = ifc_file.create_ifc_surface_style(self.color)
        ifc_product_definition_shape = self.gml_geometry.map_to_ifc(ifc_file, ifc_style, ifc_representation_sub_context)
        return self.create_ifc_element(ifc_file, placement_rel_to, ifc_product_definition_shape)

    def create_ifc_element(self, ifc_file: IfcFile, placement_rel_to: entity_instance,
                           product_definition_shape: entity_instance) -> entity_instance:
        ifc_local_placement = ifc_file.create_relative_ifc_local_placement(placement_rel_to, Point(0, 0, 0))
        ifc_element = ifc_file.create_ifc_product(self.entity, ifc_local_placement, product_definition_shape)
        return ifc_element


class Building(FeatureElement):

    def __init__(self):
        super().__init__()
        self.building_parts: list[BuildingPart] = []

    def add_building_part(self, building_part: BuildingPart):
        self.building_parts.append(building_part)

    def map_to_ifc(self, ifc_file: IfcFile, placement_rel_to: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        ifc_local_placement = ifc_file.create_relative_ifc_local_placement(placement_rel_to, Point(0, 0, 0))
        ifc_building = ifc_file.create_ifc_product("IfcBuilding", ifc_local_placement)
        ifc_elements = [building_part.map_to_ifc(ifc_file, ifc_local_placement, ifc_representation_sub_context) for
                        building_part in
                        self.building_parts]
        ifc_file.create_ifc_rel_contained_in_spatial_structure(ifc_elements, ifc_building)
        return ifc_building
