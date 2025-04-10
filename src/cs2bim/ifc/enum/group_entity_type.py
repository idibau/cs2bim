from enum import Enum


class GroupEntityType(Enum):
    """Supported ifc entity types for groups"""

    IFC_DISTRIBUTION_SYSTEM = 0
    IFC_DISTRIBUTION_CIRCUIT = 1
    IFC_BUILDING_SYSTEM = 2
    # IFC_BUILT_SYSTEM = 2  This entity type is only supported in 4.3
    IFC_STRUCTURAL_ANALYSIS_MODEL = 3
    IFC_ZONE = 4
