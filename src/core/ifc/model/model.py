from core.ifc.model.building import Building
from core.ifc.model.clipped_terrain import ClippedTerrain
from core.ifc.model.ifc_version import IfcVersion
from core.ifc.model.element import Element


class Model:
    """
    Class holding all variable data for creating the ifc

    Attributes
    ----------
    file_name : str
        Name of the file
    schema : str
        IFC schema has to be either IFC4 or IFC4x3
    origin: tuple[float, float, float]
        Origin coordinate (east, north, height)
    elements : list[Element]
        List of all elements that should be added
    """

    def __init__(self, file_name: str, schema: IfcVersion, origin: tuple[float, float, float]) -> None:
        self.file_name = file_name
        self.schema = schema
        self.origin = origin
        self.clipped_terrains = {}
        self.buildings = {}

    def add_clipped_terrain(self, feature_class_key: str, clipped_terrain: ClippedTerrain) -> None:
        if not feature_class_key in self.clipped_terrains:
            self.clipped_terrains[feature_class_key] = []
        self.clipped_terrains[feature_class_key].append(clipped_terrain)

    def add_building(self, feature_class_key: str, element: Building) -> None:
        if not feature_class_key in self.buildings:
            self.buildings[feature_class_key] = []
        self.buildings[feature_class_key].append(element)
