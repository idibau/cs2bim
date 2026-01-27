from ifcopenshell import entity_instance
from lxml.etree import _Element as XmlElement
from shapely import Point

from core.ifc.ifc_file import IfcFile
from core.ifc.model.building.namespace import namespace
from core.ifc.model.building.polygon import Polygon


class CompositeSurface:
    def __init__(self):
        super().__init__()
        self.polygons = []

    def from_gml(self, gml: XmlElement, project_origin: Point):
        for polygon_gml in gml.xpath("./gml:surfaceMember/gml:Polygon", namespaces=namespace):
            polygon = Polygon()
            polygon.from_gml(polygon_gml, project_origin)
            self.polygons.append(polygon)

    def create_ifc_indexed_polygonal_faces(self, ifc_file: IfcFile, coordinates: dict[tuple, int]) -> list[
        entity_instance]:
        ifc_faces = [polygon.create_ifc_indexed_polygonal_face(ifc_file, coordinates) for polygon in self.polygons]
        return ifc_faces

    def create_ifc_faces(self, ifc_file: IfcFile) -> list[entity_instance]:
        ifc_faces = [polygon.create_ifc_face(ifc_file) for polygon in self.polygons]
        return ifc_faces
