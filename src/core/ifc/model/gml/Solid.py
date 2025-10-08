from ifcopenshell import entity_instance

from core.ifc.model.gml.composite_surface import CompositeSurface
from core.ifc.model.gml.gml_geometry import GmlGeometry
from core.ifc.model.gml.namespace import namespace


class Solid(GmlGeometry):
    def __init__(self):
        super().__init__()
        self.exterior = CompositeSurface()
        self.interior = []

    def from_gml(self, gml, origin):
        surface_exterior = gml.xpath("./gml:exterior/gml:CompositeSurface", namespaces=namespace)
        if len(surface_exterior) != 1:
            raise ValueError("Solid expects exactly one exterior composite surface")
        self.exterior.from_gml(surface_exterior[0], origin)
        for interior_gml in gml.xpath("./gml:interior", namespaces=namespace):
            for composite_surface_gml in interior_gml.xpath("./gml:CompositeSurface", namespaces=namespace):
                composite_surface = CompositeSurface()
                composite_surface.from_gml(composite_surface_gml, origin)
                self.interior.append(composite_surface)

    def map_to_ifc(self, ifc_file, ifc_style):
        exterior_ifc_faces = self.exterior.create_ifc_faces(ifc_file)
        interior_ifc_faces_list = []
        for composite_surface in self.interior:
            interior_ifc_faces = composite_surface.create_ifc_faces(ifc_file)
            interior_ifc_faces_list.append(interior_ifc_faces)
        if interior_ifc_faces_list:
            ifc_faceted_brep = ifc_file.create_ifc_faceted_brep_with_voids(exterior_ifc_faces, interior_ifc_faces_list)
        else:
            ifc_faceted_brep = ifc_file.create_ifc_faceted_brep(exterior_ifc_faces)
        ifc_file.create_ifc_styled_item(ifc_faceted_brep, ifc_style)
        return [ifc_faceted_brep]

    def create_ifc_product_definition_shape(self, ifc_file, ifc_representation_sub_context,
                                            ifc_representations: list[entity_instance]):
        ifc_product_definition_shape = ifc_file.create_ifc_product_definition_shape(ifc_representation_sub_context,
                                                                                    "Brep", ifc_representations)
        return ifc_product_definition_shape
