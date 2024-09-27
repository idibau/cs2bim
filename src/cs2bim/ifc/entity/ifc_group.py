from enum import Enum


class IfcGroupEntityType(Enum):
    IFC_DISTRIBUTION_SYSTEM = 0
    IFC_DISTRIBUTION_CIRCUIT = 1
    IFC_BUILDING_SYSTEM = 2
    # IFC_BUILT_SYSTEM = 2  This entity type is only supported in 4.3
    IFC_STRUCTURAL_ANALYSIS_MODEL = 3
    IFC_ZONE = 4


class IfcGroup:

    def __init__(self, entity_type: IfcGroupEntityType, attributes: dict[str, str]) -> None:
        self.entity_type = entity_type
        self.attributes = attributes
