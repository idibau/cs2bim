from enum import Enum


class ElementAttribute(Enum):
    """Supported attributes for elements"""

    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    COMPOSITION_TYPE = "COMPOSITION_TYPE"
    PREDEFINED_TYPE = "PREDEFINED_TYPE"
    OBJECT_TYPE = "OBJECT_TYPE"
    LONGNAME = "LONGNAME"
