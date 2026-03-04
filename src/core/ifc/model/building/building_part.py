from ifcopenshell import entity_instance
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.gml_geometry import GmlGeometry


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
        ifc_local_placement = ifc_file.create_relative_ifc_local_placement(placement_rel_to, Point(0, 0, 0))
        ifc_element = ifc_file.create_ifc_product(self.entity, ifc_local_placement, ifc_product_definition_shape)
        return ifc_element
