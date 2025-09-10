from config.element_attribute import ElementAttribute
from config.source_type import SourceType
from core.ifc.model.property_set import PropertySet


class Element:
    """Representation of an IfcElement that can be added to a model"""

    def __init__(self) -> None:
        self.groups = []
        self.attributes = {}
        self.property_sets = {}

    @classmethod
    def from_static_element_config(cls, config):
        element = Element()
        for attribute in config.attributes:
            if attribute.source.type == SourceType.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)
        for p in config.properties:
            if p.source.type == SourceType.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)
        return element

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

    def add_group(self, name):
        """Adds a new group to the element"""
        if not name in self.groups:
            self.groups.append(name)

    def set_ifc_properties(self, ifc_file, ifc_element):
        for property_set in self.property_sets.values():
            ifc_property_single_values = []
            for key, value in property_set.properties.items():
                ifc_property_single_values.append(ifc_file.create_ifc_property_single_value(key, value))
            ifc_file.create_ifc_property_set(property_set.name, ifc_property_single_values, ifc_element)

    def set_ifc_attributes(self, ifc_element):
        for attribute, value in self.attributes.items():
            if attribute == ElementAttribute.NAME:
                ifc_attribute = "Name"
            elif attribute == ElementAttribute.DESCRIPTION:
                ifc_attribute = "Description"
            elif attribute == ElementAttribute.COMPOSITION_TYPE:
                ifc_attribute = "CompositionType"
            elif attribute == ElementAttribute.PREDEFINED_TYPE:
                ifc_attribute = "PredefinedType"
            elif attribute == ElementAttribute.OBJECT_TYPE:
                ifc_attribute = "ObjectType"
            elif attribute == ElementAttribute.LONGNAME:
                ifc_attribute = "LongName"
            else:
                raise Exception(f"building step for attribute type {attribute} not implemented")
            if hasattr(ifc_element, ifc_attribute):
                setattr(ifc_element, ifc_attribute, value)
