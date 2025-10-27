from enum import Enum


class ProjectionEntity(Enum):
    """Supported ifc entities for projection entities"""

    IFC_GEOGRAPHIC_ELEMENT = "IFC_GEOGRAPHIC_ELEMENT"
    IFC_ANNOTATION = "IFC_ANNOTATION"
    IFC_SITE = "IFC_SITE"
    IFC_BUILDING = "IFC_BUILDING"
    IFC_SPATIAL_ZONE = "IFC_SPATIAL_ZONE"