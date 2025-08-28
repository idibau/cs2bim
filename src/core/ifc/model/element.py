from core.ifc.model.property_set import PropertySet
from abc import ABC


class Element(ABC):
    """
    Representation of an IfcElement that can be added to a model

    Attributes
    ----------
    attributes : dict[str, str]
        Attributes of the element
    groups : list[str]
        A list of all groups that this element is assigned to
    property_sets : dict[str, PropertySet]
        A map of all property sets identified by their name
    """

    def __init__(self, groups: list[str] = None) -> None:
        self.attributes = {}
        self.groups = groups if groups is not None else []
        self.property_sets = {}

    def add_property(self, property_set: str, key: str, value: str):
        """Adds a new property to the element"""
        if not property_set in self.property_sets:
            self.property_sets[property_set] = PropertySet(property_set)
        self.property_sets[property_set].add_property(key, value)

    def add_attribute(self, name, value):
        """Adds a new attribute to the element"""
        if not name in self.attributes:
            self.attributes[name] = value
        else:
            raise Exception(f"Attribute {name} already exists")

