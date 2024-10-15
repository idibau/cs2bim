from cs2bim.ifc.model.color import Color
from cs2bim.ifc.enum.element_entity_type import ElementEntityType
from cs2bim.ifc.config.property_config import PropertyConfig
from cs2bim.ifc.config.spatial_structure_config import SpatialStructureConfig


class FeatureClass:
    """
    Data class for a feature class object

    Attributes
    ----------
    sql : str
        Path to the sql file
    entity_type : ElementEntityType
        Entity type of all elemets assigned to this feature class
    attributes : dict[str, str]
        All columns that should be represented in a attribute (name: column)
    properties : list[PropertyConfig]
        List of property configs (name, column, set) that define which properties are
        created for the elements of this feature class
    spatial_structure : SpatialStructureConfig
        Config of the parent spatial structure of all elemets assigned to this feature class
    group_columns : list[str]
        Columns that holds the Ifc group names for an element
    color : Color
        Color of of all elemets assigned to this feature class
    """

    def __init__(
        self,
        sql: str,
        entity_type: ElementEntityType,
        attributes: dict[str, str],
        properties: list[PropertyConfig],
        spatial_structure: SpatialStructureConfig,
        group_columns: list[str],
        color: Color,
    ) -> None:
        self.sql = sql
        self.attributes = attributes
        self.properties = properties
        self.entity_type = entity_type
        self.spatial_structure = spatial_structure
        self.group_columns = group_columns
        self.color = color
