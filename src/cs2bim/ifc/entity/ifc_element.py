from enum import Enum

from cs2bim.geometry.geometry import Geometry
from cs2bim.ifc.entity.ifc_property_set import IfcPropertySet


class IfcElementEntityType(Enum):
    """Supported Ifc entity types for elements"""

    IFC_GEOGRAPHIC_ELEMENT = 0


class IfcElement:
    """
    Representation of an IfcElement that can be added to a model

    Attributes
    ----------
    name : str
        Name of the element
    description : str
        Description of the element
    geometry : Geometry
        The geometry of the element
    property_sets : dict[str, PropertySet]
        A map of all property sets identified by their name
    """

    def __init__(self, name: str, description: str, geometry: Geometry) -> None:
        self.name = name
        self.description = description
        self.geometry = geometry

        self.property_sets = {}

    def add_property(self, property_set: str, key: str, value: str):
        """Adds a new property to the element"""
        if not property_set in self.property_sets:
            self.property_sets[property_set] = IfcPropertySet(property_set)
        self.property_sets[property_set].add_property(key, value)
