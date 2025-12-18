from enum import Enum

class ExtrusionEntity(Enum):
    """Supported ifc entities for extrusion entities"""

    IFC_PIPE_SEGMENT = "IFC_PIPE_SEGMENT"
    IFC_DISTRIBUTION_FLOW_ELEMENT = "IFC_DISTRIBUTION_FLOW_ELEMENT"