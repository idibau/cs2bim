from enum import Enum


class BuildingSourceType(Enum):
    """Supported source types for properties and attributes in building feature types"""

    STATIC = "STATIC"
    SQL = "SQL"
    CITY_GML = "CITY_GML"