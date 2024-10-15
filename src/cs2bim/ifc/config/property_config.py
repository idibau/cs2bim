class PropertyConfig:
    """Build instructions for an ifc property including the set it belongs to"""

    def __init__(self, name: str, set: str, column: str) -> None:
        self.name = name
        self.set = set
        self.column = column