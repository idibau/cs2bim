class PropertySet:
    """
    Class holding a set of properties

    Attributes
    ----------
    name : str
        Name of the property set
    properties : dict[str, str]
        Key/value pairs representing poperties
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.properties = {}

    def add_property(self, key: str, value: str):
        self.properties[key] = value