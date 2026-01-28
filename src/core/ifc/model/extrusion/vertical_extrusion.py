import logging
from ifcopenshell import entity_instance
from shapely import Point
from shapely.geometry.base import BaseGeometry
from shapely.affinity import translate

from core.ifc.ifc_file import IfcFile
from core.ifc.model.extrusion.circle import Circle
from core.ifc.model.extrusion.cross_section import CrossSection
from core.ifc.model.extrusion.egg import Egg
from core.ifc.model.extrusion.extrusion import Extrusion
from core.ifc.model.extrusion.polygon import Polygon
from core.ifc.model.extrusion.rectangle import Rectangle

logger = logging.getLogger(__name__)


class VerticalExtrusion(Extrusion):

    def __init__(self, area: CrossSection, start_point: BaseGeometry, end_point: BaseGeometry, orientation: float):
        super().__init__()
        self.area = area
        self.start_point = start_point
        self.end_point = end_point
        self.orientation = orientation

    def map_to_ifc(self, ifc_file: IfcFile, entity: str, placement_rel_to: entity_instance,
                   ifc_representation_sub_context: entity_instance, ifc_style: entity_instance) -> entity_instance:
        if isinstance(self.area, Polygon) and not self.area.local:
            ifc_profile_def = ifc_file.create_ifc_arbitrary_closed_profile_def(self.area.points)
            self.start_point = translate(self.start_point, xoff=-self.start_point.x, yoff=-self.start_point.y, zoff=0)
        elif isinstance(self.area, Egg) or isinstance(self.area, Polygon):
            ifc_profile_def = ifc_file.create_ifc_arbitrary_closed_profile_def(self.area.points)
        elif isinstance(self.area, Rectangle):
            ifc_profile_def = ifc_file.create_ifc_rectangle_profile_def(self.area.width, self.area.height)
        elif isinstance(self.area, Circle):
            ifc_profile_def = ifc_file.create_ifc_circle_profile_def(self.area.radius)
        else:
            raise Exception(
                f"simple extrusion building step for area class {type(self.area)} not implemented")

        ifc_geometry = ifc_file.create_ifc_extruded_area_solid(ifc_profile_def, self.start_point,
                                                               self.end_point.z - self.start_point.z, self.orientation)

        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "AdvancedSweptSolid",
                                                                                    [ifc_geometry])

        ifc_local_placement = ifc_file.create_relative_ifc_local_placement(placement_rel_to, Point(0.0, 0.0, 0.0))
        ifc_file.create_ifc_styled_item(ifc_geometry, ifc_style)
        ifc_element = ifc_file.create_ifc_product(entity, ifc_local_placement, ifc_product_definition_shape)
        return ifc_element
