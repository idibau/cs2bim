from lxml.etree import _Element as XmlElement

from core.ifc.model.coordinates import Coordinates


class PosList:
    def __init__(self):
        super().__init__()
        self.coordinates = []

    def from_gml(self, gml: XmlElement, project_origin: Coordinates):
        coords = list(map(float, gml.text.split()))
        if len(coords) % 3 != 0:
            raise ValueError("PosList is not 3 dimensional")
        if len(coords) < 12:
            raise ValueError("PosList must have at least 4 coordinates")
        if coords[:3] != coords[-3:]:
            raise ValueError("PosList must be closed")
        for i in range(0, len(coords) - 3, 3):
            self.coordinates.append(
                Coordinates(float(coords[i] - project_origin.x), float(coords[i + 1] - project_origin.y),
                            float(coords[i + 2] - project_origin.z)))
