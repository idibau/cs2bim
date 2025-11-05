from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement

from core.ifc.ifc_file import IfcFile
from core.ifc.model.coordinates import Coordinates
from core.ifc.model.gml.gml_geometry import GmlGeometry
from core.ifc.model.gml.namespace import namespace
from core.ifc.model.gml.solid import Solid


class CompositeSolid(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.solids = []

    def from_gml(self, gml: XmlElement, project_origin: Coordinates):
        for solid_gml in gml.xpath("./gml:solidMember/gml:Solid", namespaces=namespace):
            solid = Solid()
            solid.from_gml(solid_gml, project_origin)
            self.solids.append(solid)

    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance) -> list[entity_instance]:
        ifc_faceted_breps = [solid.map_to_ifc(ifc_file, ifc_style) for solid in self.solids]
        return ifc_faceted_breps

    def create_ifc_product_definition_shape(self, ifc_file: IfcFile, ifc_representation_sub_context: entity_instance,
                                            ifc_representations: list[entity_instance]) -> entity_instance:
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Brep", ifc_representations)
        return ifc_product_definition_shape
