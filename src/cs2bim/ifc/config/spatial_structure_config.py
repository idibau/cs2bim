import json

from cs2bim.ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType


class SpatialStructureConfig:
    """Build instructions for an ifc spatial structure"""

    def __init__(self, type: SpatialStructureEntityType, attributes: dict[str, str]) -> None:
        self.type = type
        self.attributes = attributes

    def get_key(self) -> str:
        """Returns a key to identify a spatial structure instance"""
        return f"{json.dumps(self.attributes, sort_keys=True)}-{self.type.name}"
