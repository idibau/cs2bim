from tin2ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType

class SpatialStructure:
    """Ifc spatial structure"""

    def __init__(self, type: SpatialStructureEntityType, name: str) -> None:
        self.type = type
        self.name = name

    def get_key(self) -> str:
        """Returns a key to identify a spatial structure instance"""
        return f"{self.name}-{self.type.name}"
