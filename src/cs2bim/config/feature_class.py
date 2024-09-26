from cs2bim.ifc.entity.ifc_element import IfcElementEntityType
from cs2bim.ifc.entity.ifc_spatial_structure import IfcSpatialStructure


class Property:
    """
    Describes a property that is added to an ifc element

    Attributes
    ----------
    name : str
        Name of the property
    set : str
        Name of the property set
    column : str
        Column that holds the property value
    """

    def __init__(self, name: str, set: str, column: str) -> None:
        self.name = name
        self.set = set
        self.column = column


class FeatureClass:
    """
    Data class for a feature class object

    Attributes
    ----------
    sql : str
        Path to the sql file
    entity_type : ElementEntityType
        Entity type of all elemets assigned to this feature class
    element_name_column : str
        Column that holds element name information
    properties : list[Property]
        List of property definitions (name, column, set)
    spatial_structure : SpatialStructure
        Parent spatial structure of all elemets assigned to this feature class
    group_columns : list[str]
        Columns that holds the Ifc group names for an element
    color_definition : tuple[float, float, float, float]
        Color of of all elemets assigned to this feature class
    """

    def __init__(
        self,
        sql: str,
        entity_type: IfcElementEntityType,
        element_name_column: str,
        properties: list[Property],
        spatial_structure: IfcSpatialStructure,
        group_columns: list[str],
        color_definition: tuple[float, float, float, float],
    ) -> None:
        self.sql = sql
        self.element_name_column = element_name_column
        self.properties = properties
        self.entity_type = entity_type
        self.spatial_structure = spatial_structure
        self.group_columns = group_columns
        self.color_definition = color_definition
