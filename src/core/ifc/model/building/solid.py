from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.composite_surface import CompositeSurface
from core.ifc.model.building.gml_geometry import GmlGeometry
from core.ifc.model.building.namespace import namespace


class Solid(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.exterior = CompositeSurface()
        self.interior = []

    def from_gml(self, gml: XmlElement, project_origin: Point):
        surface_exterior = gml.xpath("./gml:exterior/gml:CompositeSurface", namespaces=namespace)
        if len(surface_exterior) != 1:
            raise ValueError("Solid expects exactly one exterior composite surface")
        self.exterior.from_gml(surface_exterior[0], project_origin)
        for interior_gml in gml.xpath("./gml:interior", namespaces=namespace):
            for composite_surface_gml in interior_gml.xpath("./gml:CompositeSurface", namespaces=namespace):
                composite_surface = CompositeSurface()
                composite_surface.from_gml(composite_surface_gml, project_origin)
                self.interior.append(composite_surface)

    def create_ifc_brep(self, ifc_file: IfcFile, ifc_style: entity_instance) -> entity_instance:
        exterior_ifc_faces = self.exterior.create_ifc_faces(ifc_file)
        interior_ifc_faces_list = [cs.create_ifc_faces(ifc_file) for cs in self.interior]
        if interior_ifc_faces_list:
            ifc_brep = ifc_file.create_ifc_faceted_brep_with_voids(exterior_ifc_faces, interior_ifc_faces_list)
        else:
            ifc_brep = ifc_file.create_ifc_faceted_brep(exterior_ifc_faces)
        ifc_file.create_ifc_styled_item(ifc_brep, ifc_style)
        return ifc_brep

    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        ifc_brep = self.create_ifc_brep(ifc_file, ifc_style)
        return ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context, "Brep", [ifc_brep])
