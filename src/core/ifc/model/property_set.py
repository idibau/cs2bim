class PropertySet:
    """Class holding a set of properties"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.properties = {}

    def add_property(self, key: str, value: str):
        if not key in self.properties:
            self.properties[key] = value
        else:
            raise Exception(f"Property {key} already exists")

    def __eq__(self, other):
        if not isinstance(other, PropertySet):
            return False
        return self.name == other.name and self.properties == other.properties

    def __hash__(self):
        return hash((self.name, tuple(sorted(self.properties.items()))))

    def __repr__(self):
        return f"MyObject(name={self.name!r}, properties={self.properties!r})"