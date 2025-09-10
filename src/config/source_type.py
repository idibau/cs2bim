from enum import Enum


class SourceType(Enum):
    """Supported source types for properties and attributes"""

    STATIC = "STATIC"
    SQL = "SQL"
    CITY_GML = "CITY_GML"