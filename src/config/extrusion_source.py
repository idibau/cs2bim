from enum import Enum


class ExtrusionSource(Enum):
    """Supported source types for properties and attributes in extrusion feature types"""

    STATIC = "STATIC"
    SQL = "SQL"