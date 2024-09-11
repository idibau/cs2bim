from enum import Enum


class IfcSpatialStructureEntityType(Enum):
    """Supported ifc entity types for spatial structures"""

    IFC_SITE = 0


class IfcSpatialStructure:
    """Ifc spatial structure"""

    def __init__(self, type: IfcSpatialStructureEntityType, name: str) -> None:
        self.type = type
        self.name = name

    def get_key(self) -> str:
        """Returns a key to identify a spatial structure instance"""
        return f"{self.name}-{self.type.name}"
