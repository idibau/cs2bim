from enum import Enum


class BuildingPartEntity(Enum):
    """Supported ifc entity types for building part entities"""

    IFC_WALL = "IFC_WALL"
    IFC_SLAB = "IFC_SLAB"
    IFC_ROOF = "IFC_ROOF"
    IFC_BUILDING_ELEMENT_PROXY = "IFC_BUILDING_ELEMENT_PROXY"
