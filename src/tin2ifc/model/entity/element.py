from tin2ifc.model.entity.property_set import PropertySet
from tin2ifc.model.geometry.geometry import Geometry


class Element:
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
            self.property_sets[property_set] = PropertySet(property_set)
        self.property_sets[property_set].add_property(key, value)
