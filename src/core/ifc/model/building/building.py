from ifcopenshell import entity_instance
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.building_part import BuildingPart
from core.ifc.model.feature_element import FeatureElement


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
