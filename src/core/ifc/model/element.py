from core.ifc.model.property_set import PropertySet


class Element:

    def __init__(self) -> None:
        self.attributes = {}
        self.property_sets = {}

    def add_property(self, property_set: str, key: str, value: str):
        if not property_set in self.property_sets:
            self.property_sets[property_set] = PropertySet(property_set)
        self.property_sets[property_set].add_property(key, value)

    def add_attribute(self, name, value):
        if not name in self.attributes:
            self.attributes[name] = value
        else:
            raise Exception(f"Attribute {name} already exists")

    def set_ifc_properties(self, ifc_file, ifc_element):
        for property_set in self.property_sets.values():
            ifc_property_single_values = []
            for key, value in property_set.properties.items():
                ifc_property_single_values.append(ifc_file.create_ifc_property_single_value(key, value))
            ifc_file.create_ifc_property_set(property_set.name, ifc_property_single_values, ifc_element)

    def set_ifc_attributes(self, ifc_file, ifc_element):
        for attribute, value in self.attributes.items():
            ifc_file.add_attribute(ifc_element, attribute, value)

    def __eq__(self, other):
        if not isinstance(other, Element):
            return False
        return self.attributes == other.attributes and self.property_sets == other.property_sets

    def __hash__(self):
        return hash((
            tuple(sorted(self.attributes.items())),
            tuple(sorted((name, hash(ps)) for name, ps in self.property_sets.items()))
        ))

    def __repr__(self):
        return f"Element(attributes={self.attributes!r}, " f"property_sets={list(self.property_sets.keys())!r})"
