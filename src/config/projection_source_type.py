from enum import Enum


class ProjectionSourceType(Enum):
    """Supported source types for properties and attributes in projection feature types"""

    STATIC = "STATIC"
    SQL = "SQL"