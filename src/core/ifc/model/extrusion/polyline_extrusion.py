import logging
from ifcopenshell import entity_instance
from shapely import Point
from shapely.geometry.base import BaseGeometry

from config.extrusion_entity import ExtrusionEntity
from core.ifc.ifc_file import IfcFile
from core.ifc.model.extrusion.circle import Circle
from core.ifc.model.extrusion.cross_section import CrossSection
from core.ifc.model.extrusion.egg import Egg
from core.ifc.model.extrusion.extrusion import Extrusion
from core.ifc.model.extrusion.polygon import Polygon
from core.ifc.model.extrusion.rectangle import Rectangle

logger = logging.getLogger(__name__)


class PolylineExtrusion(Extrusion):

    def __init__(self, area: CrossSection, polyline: BaseGeometry):
        super().__init__()
        self.area = area
        self.points = []
        for x, y, z in list(polyline.coords):
            self.points.append(Point(x, y, z))

    def map_to_ifc(self, ifc_file: IfcFile, entity: ExtrusionEntity, ifc_representation_sub_context: entity_instance,
                   ifc_style: entity_instance) -> entity_instance:
        ifc_polyline = ifc_file.create_ifc_polyline(self.points)

        if isinstance(self.area, Circle):
            ifc_geometry = ifc_file.create_ifc_swept_disk_solid(ifc_polyline, self.area.radius)
        else:
            if isinstance(self.area, Egg) or isinstance(self.area, Polygon):
                ifc_profile_def = ifc_file.create_ifc_arbitrary_closed_profile_def(self.area.points)
            elif isinstance(self.area, Rectangle):
                ifc_profile_def = ifc_file.create_ifc_rectangle_profile_def(self.area.width, self.area.height)
            else:
                raise Exception(
                    f"complex extrusion builing step for area class {type(self.area)} not implemented")
            ifc_geometry = ifc_file.create_ifc_sectioned_solid_horizontal(ifc_profile_def, ifc_polyline)

        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "AdvancedSweptSolid",
                                                                                    [ifc_geometry])
        ifc_local_placement = ifc_file.create_ifc_local_placement(Point(0.0, 0.0, 0.0))
        ifc_file.create_ifc_styled_item(ifc_geometry, ifc_style)
        if entity == ExtrusionEntity.IFC_PIPE_SEGMENT:
            ifc_element = ifc_file.create_ifc_pipe_segment(ifc_local_placement, ifc_product_definition_shape)
        elif entity == ExtrusionEntity.IFC_DISTRIBUTION_FLOW_ELEMENT:
            ifc_element = ifc_file.create_ifc_distribution_flow_element(ifc_local_placement,
                                                                        ifc_product_definition_shape)
        else:
            raise Exception(
                f"building step for feature class entity type {entity.name} not implemented")
        return ifc_element
