from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.composite_surface import CompositeSurface
from core.ifc.model.building.gml_geometry import GmlGeometry
from core.ifc.model.building.namespace import namespace
from core.ifc.model.building.polygon import Polygon


class MultiSurface(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.polygons: list[Polygon] = []
        self.composite_surfaces = []

    def from_gml(self, gml: XmlElement, project_origin: Point):
        for polygon_gml in gml.xpath("./gml:surfaceMember/gml:Polygon | ./gml:surfaceMembers/gml:Polygon",
                                     namespaces=namespace):
            polygon = Polygon()
            polygon.from_gml(polygon_gml, project_origin)
            self.polygons.append(polygon)

        for composite_surface_gml in gml.xpath(
                "./gml:surfaceMember/gml:CompositeSurface | ./gml:surfaceMembers/gml:CompositeSurface",
                namespaces=namespace):
            composite_surface = CompositeSurface()
            composite_surface.from_gml(composite_surface_gml, project_origin)
            self.composite_surfaces.append(composite_surface)

    def map_to_ifc(self, ifc_file: IfcFile, ifc_style: entity_instance,
                   ifc_representation_sub_context: entity_instance) -> entity_instance:
        ifc_face_sets = []
        vertices = {}
        ifc_faces = [polygon.create_ifc_indexed_polygonal_face(ifc_file, vertices) for polygon in self.polygons]
        ifc_face_sets.append(ifc_file.create_ifc_polygonal_face_set([Point(t) for t in vertices.keys()], ifc_faces))
        for composite_surface in self.composite_surfaces:
            vertices = {}
            ifc_faces = composite_surface.create_ifc_indexed_polygonal_faces(ifc_file, vertices)
            ifc_face_set = ifc_file.create_ifc_polygonal_face_set([Point(t) for t in vertices.keys()], ifc_faces)
            ifc_face_sets.append(ifc_face_set)
        for ifc_face_set in ifc_face_sets:
            ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Tessellation", ifc_face_sets)
        return ifc_product_definition_shape
