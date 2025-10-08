from ifcopenshell import entity_instance

from core.ifc.model.gml.composite_surface import CompositeSurface
from core.ifc.model.gml.gml_geometry import GmlGeometry
from core.ifc.model.gml.namespace import namespace
from core.ifc.model.gml.polygon import Polygon


class MultiSurface(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.polygons = []
        self.composite_surfaces = []

    def from_gml(self, gml, origin):
        for polygon_gml in gml.xpath("./gml:surfaceMember/gml:Polygon | ./gml:surfaceMembers/gml:Polygon",
                                     namespaces=namespace):
            polygon = Polygon()
            polygon.from_gml(polygon_gml, origin)
            self.polygons.append(polygon)

        for composite_surface_gml in gml.xpath(
                "./gml:surfaceMember/gml:CompositeSurface | ./gml:surfaceMembers/gml:CompositeSurface",
                namespaces=namespace):
            composite_surface = CompositeSurface()
            composite_surface.from_gml(composite_surface_gml, origin)
            self.composite_surfaces.append(composite_surface_gml)

    def map_to_ifc(self, ifc_file, ifc_style):
        ifc_face_sets = []
        vertices = {}
        ifc_faces = [polygon.create_ifc_indexed_polygonal_face(ifc_file, vertices) for polygon in self.polygons]
        ifc_face_sets.append(ifc_file.create_ifc_polygonal_face_set(list(vertices.keys()), ifc_faces))
        for composite_surface in self.composite_surfaces:
            vertices = {}
            ifc_faces = composite_surface.create_ifc_indexed_polygonal_faces(ifc_file, vertices)
            ifc_face_set = ifc_file.create_ifc_polygonal_face_set(list(vertices.keys()), ifc_faces)
            ifc_face_sets.append(ifc_face_set)
        for ifc_face_set in ifc_face_sets:
            ifc_file.create_ifc_styled_item(ifc_face_set, ifc_style)
        return ifc_face_sets

    def create_ifc_product_definition_shape(self, ifc_file, ifc_representation_sub_context,
                                            ifc_representations: list[entity_instance]):
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(
            ifc_representation_sub_context, "Tessellation", ifc_representations)
        return ifc_product_definition_shape