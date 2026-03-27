from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.gml_geometry import GmlGeometry
from core.ifc.model.building.namespace import namespace
from core.ifc.model.building.solid import Solid


class CompositeSolid(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.solids = []

    def from_gml(self, gml: XmlElement, project_origin: Point):
        for solid_gml in gml.xpath("./gml:solidMember/gml:Solid", namespaces=namespace):
            solid = Solid()
            solid.from_gml(solid_gml, project_origin)
            self.solids.append(solid)

    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        ifc_breps = [solid.create_ifc_brep(ifc_file, ifc_style) for solid in self.solids]
        return ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context, "Brep", ifc_breps)
