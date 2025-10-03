from enum import Enum


class GmlGeometryType(Enum):
    """Supported gml geometry types"""

    MULTI_SURFACE = "MULTI_SURFACE"
    SOLID = "SOLID"
    COMPOSITE_SOLID = "COMPOSITE_SOLID"
