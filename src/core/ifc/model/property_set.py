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
