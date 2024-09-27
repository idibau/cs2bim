import json
from enum import Enum


class IfcSpatialStructureEntityType(Enum):
    """Supported ifc entity types for spatial structures"""

    IFC_SITE = 0


class IfcSpatialStructure:
    """Ifc spatial structure"""

    def __init__(self, type: IfcSpatialStructureEntityType, attributes: dict[str, str]) -> None:
        self.type = type
        self.attributes = attributes

    def get_key(self) -> str:
        """Returns a key to identify a spatial structure instance"""
        return f"{json.dumps(self.attributes, sort_keys=True)}-{self.type.name}"
