from tin2ifc.enum.element_entity_type import ElementEntityType
from tin2ifc.model.entity.spatial_structure import SpatialStructure

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
        entity_type: ElementEntityType,
        spatial_structure: SpatialStructure,
        groups: list[str],
        color_definition: tuple[float, float, float, float],
    ) -> None:
        self.key = key
        self.entity_type = entity_type
        self.spatial_structure = spatial_structure
        self.groups = groups
        self.color_definition = color_definition
