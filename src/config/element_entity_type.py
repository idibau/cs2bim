from enum import Enum


class ElementEntityType(Enum):
    """Supported Ifc entity types for elements"""

    IFC_GEOGRAPHIC_ELEMENT = "IFC_GEOGRAPHIC_ELEMENT"
    IFC_WALL = "IFC_WALL"
    IFC_SLAB = "IFC_SLAB"
    IFC_ROOF = "IFC_ROOF"
    IFC_SPACE = "IFC_SPACE"
