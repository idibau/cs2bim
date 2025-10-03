from core.ifc.model.gml.namespace import namespace
from core.ifc.model.gml.polygon import Polygon


class CompositeSurface:
    def __init__(self):
        super().__init__()
        self.polygons = []

    def from_gml(self, gml, origin):
        for polygon_gml in gml.xpath("./gml:surfaceMember/gml:Polygon", namespaces=namespace):
            polygon = Polygon()
            polygon.from_gml(polygon_gml, origin)
            self.polygons.append(polygon)

    def map_to_ifc(self, ifc_file):
        ifc_faces = [polygon.map_to_ifc(ifc_file) for polygon in self.polygons]
        return ifc_faces
