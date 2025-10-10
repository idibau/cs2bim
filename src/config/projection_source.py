from enum import Enum


class ProjectionSource(Enum):
    """Supported source types for properties and attributes in projection feature types"""

    STATIC = "STATIC"
    SQL = "SQL"