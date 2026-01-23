from enum import Enum

class CrossSectionType(Enum):
    CIRCLE = "CIRCLE"
    EGG = "EGG"
    RECTANGLE = "RECTANGLE"
    POLYGON_LOCAL = "POLYGON_LOCAL"
    POLYGON_GLOBAL = "POLYGON_GLOBAL"