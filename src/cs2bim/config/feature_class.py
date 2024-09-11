from cs2bim.ifc.entity.ifc_element import IfcElementEntityType
from cs2bim.ifc.entity.ifc_spatial_structure import IfcSpatialStructure

class FeatureClass:
    """
    Data class for a feature class object

    Attributes
    ----------
    key : str
        Feature class key
    entity_type : ElementEntityType
        Entity type of all elemets assigned to this feature class
    spatial_structure : SpatialStructure
        Parent spatial structure of all elemets assigned to this feature class
    groups : list[str]
        Ifc groups of all elemets assigned to this feature class
    color_definition : tuple[float, float, float, float]
        Color of of all elemets assigned to this feature class
    """

    def __init__(
        self,
        key: str,
        entity_type: IfcElementEntityType,
        spatial_structure: IfcSpatialStructure,
        groups: list[str],
        color_definition: tuple[float, float, float, float],
    ) -> None:
        self.key = key
        self.entity_type = entity_type
        self.spatial_structure = spatial_structure
        self.groups = groups
        self.color_definition = color_definition
