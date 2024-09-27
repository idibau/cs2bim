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
    attributes : str
        Attributes of the element
    geometry : Geometry
        The geometry of the element
    groups : list[str]
        A list of all groups that this element is assigned to
    property_sets : dict[str, PropertySet]
        A map of all property sets identified by their name
    """

    def __init__(self, attributes: dict[str, str], groups: list[str], geometry: Geometry) -> None:
        self.attributes = attributes
        self.geometry = geometry
        self.groups = groups
        self.property_sets = {}

    def add_property(self, property_set: str, key: str, value: str):
        """Adds a new property to the element"""
        if not property_set in self.property_sets:
            self.property_sets[property_set] = IfcPropertySet(property_set)
        self.property_sets[property_set].add_property(key, value)
