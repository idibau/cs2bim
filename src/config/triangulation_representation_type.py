from enum import Enum


class TriangulationRepresentationType(Enum):
    """Supported build methods for the triangulations in the ifc"""

    TESSELLATION = "TESSELLATION"
    BREP = "BREP"
