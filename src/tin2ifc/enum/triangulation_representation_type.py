from enum import Enum


class TriangulationRepresentationType(Enum):
    """Build methods for the triangulations in the ifc"""

    TESSELLATION = "Tessellation"
    BREP = "Brep"
