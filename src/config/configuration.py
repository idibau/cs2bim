import os
from pathlib import Path
from pydantic import BaseModel, model_validator, Field
from pydantic_yaml import parse_yaml_raw_as
from typing import List, Optional

from config.building_entity import BuildingEntity
from config.building_part_entity import BuildingPartEntity
from config.building_source import BuildingSource
from config.geo_referencing import GeoReferencing
from config.gml_geometry import GmlGeometry
from config.grid_size import GridSize
from config.group_entity import GroupEntity
from config.projection_entity import ProjectionEntity
from config.projection_source import ProjectionSource


class Color(BaseModel):
    """Color configuration based on red, green, blue and alpha channels"""

    r: float = Field(..., ge=0.0, le=1.0, description="Red channel")
    g: float = Field(..., ge=0.0, le=1.0, description="Green channel")
    b: float = Field(..., ge=0.0, le=1.0, description="Blue channel")
    a: float = Field(0.0, ge=0.0, le=1.0, description="Alpha channel")


class I18nConfig(BaseModel):
    """Internationalization (i18n) configuration"""

    de: Optional[str] = Field(None, description="Path to the german translation file")
    fr: Optional[str] = Field(None, description="Path to the french translation string")
    it: Optional[str] = Field(None, description="Path to the italian translation string")


class DBConfig(BaseModel):
    """Postgis connection configuration"""

    dbname: str = Field(..., description="Database name")
    user: str = Field(..., description="Database username")
    host: str = Field(..., description="Database host address")
    port: int = Field(..., description="Database port number")
    password: str = Field(..., description="Database password")


class RedisDBConfig(BaseModel):
    """Redis databases configuration"""

    celery_broker: int = Field(..., ge=0, description="DB index for Celery broker")
    celery_backend: int = Field(..., ge=0, description="DB index for Celery result backend")
    file_cache: int = Field(..., ge=0, description="DB index for file cache")


class RedisConfig(BaseModel):
    """Redis connection configuration"""

    host: str = Field(..., description="Redis host address")
    port: int = Field(..., description="Redis port number")
    db: RedisDBConfig = Field(..., description="Nested Redis database configuration")
    global_keyprefix: Optional[str] = Field(None, description="Optional global keyprefix for the Redis result backend")
    queue: Optional[str] = Field(None, description="Optional queue name for Celery tasks")


class STACConfig(BaseModel):
    """STAC URLs configuration for external data sources"""

    dtm_items_url: Optional[str] = Field(None, description="URL to STAC items for DTM data")
    building_items_url: Optional[str] = Field(None, description="URL to STAC items for building data")


class TINConfig(BaseModel):
    """TIN generation configuration"""
    grid_size: GridSize = Field(..., description="TIN grid size")
    max_height_error: float = Field(..., ge=0.0, le=0.05, description="Maximum allowed height error for TIN generation")


class ProjectionConfigSource(BaseModel):
    """Source configuration for projection feature type"""

    type: ProjectionSource = Field(..., description="Type of the data source")
    expression: str = Field(..., description="Expression defining the source data")


class ProjectionPropertyConfig(BaseModel):
    """Property mapping configuration for projection feature type"""

    property: str = Field(..., description="Property name")
    property_set: str = Field(..., description="Property set name")
    source: ProjectionConfigSource = Field(..., description="Source configuration for this property")


class ProjectionAttributeConfig(BaseModel):
    """Attribute mapping configuration for projection feature type"""

    attribute: str = Field(..., description="Attribute name (Only applied if the attribute exists on the entity)")
    source: ProjectionConfigSource = Field(..., description="Source configuration for this attribute")


class ProjectionSpatialEntityConfig(BaseModel):
    """Spatial structure mapping configuration for projection feature type"""

    attributes: List[ProjectionAttributeConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                        description="List of attribute mappings")
    properties: List[ProjectionPropertyConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                       description="List of property mappings")


class ProjectionEntityTypeConfig(BaseModel):
    """Entity type mapping configuration for projection feature type"""

    attributes: List[ProjectionAttributeConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                        description="List of attribute mappings")
    properties: List[ProjectionPropertyConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                       description="List of property mappings")


class ProjectionEntityConfig(ProjectionEntityTypeConfig):
    """Entity mapping configuration for projection feature type"""

    entity: ProjectionEntity = Field(..., description="Type of entity")


class ProjectionFeatureType(BaseModel):
    """Feature type configuration for projection feature type"""

    name: str = Field(..., description="Feature type name for the projection")
    sql_path: str = Field(...,
                          description="Path to SQL definition for the projection feature type. Must return at least a column named 'wkt'.")
    entity_mapping: ProjectionEntityConfig = Field(..., description="Entity mapping configuration for the projection")
    entity_type_mapping: Optional[ProjectionEntityTypeConfig] = Field(None,
                                                                      description="Entity type mapping configuration for the projection. (Only supported for entities with TypeObject)")
    spatial_structure_mapping: ProjectionSpatialEntityConfig = Field(...,
                                                                     description="Spatial structure mapping for the projection")
    group_mapping: List[ProjectionConfigSource] = Field(default_factory=list, json_schema_extra={"default": []},
                                                        description="Group mappings for the projection feature type")
    color: Color = Field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0), json_schema_extra={"default": "white"},
                         description="Color assigned to the projection feature type")


class GmlGeometryMapping(BaseModel):
    """Geometry mapping for building part"""

    xpath: str = Field(..., description="XPath expression to locate the building part geometry in source data")
    geometry: GmlGeometry = Field(..., description="Referenced geometry type of the building part")


class BuildingPartConfig(BaseModel):
    """Building part configuration for building feature type"""

    entity: BuildingPartEntity = Field(..., description="Type of entity")
    geometry_mapping: Optional[GmlGeometryMapping] = Field(None, description="Geometry mapping for the building part")
    color: Color = Field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0), json_schema_extra={"default": "white"},
                         description="Color assigned to the building part")


class BuildingSourceConfig(BaseModel):
    """Source configuration for building feature type"""

    type: BuildingSource = Field(..., description="Type of the data source")
    expression: str = Field(..., description="Expression defining the source data")


class BuildingPropertyConfig(BaseModel):
    """Property mapping configuration for building feature type"""

    property: str = Field(..., description="Property name")
    property_set: str = Field(..., description="Property set name")
    source: BuildingSourceConfig = Field(..., description="Source configuration for this property")


class BuildingAttributeConfig(BaseModel):
    """Attribute mapping configuration for building feature type"""

    attribute: str = Field(..., description="Attribute name (Only applied if the attribute exists on the entity)")
    source: BuildingSourceConfig = Field(..., description="Source configuration for this attribute")


class BuildingSpatialEntityConfig(BaseModel):
    """Spatial structure mapping configuration for building feature type"""

    attributes: List[BuildingAttributeConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                      description="List of attribute mappings")
    properties: List[BuildingPropertyConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                     description="List of property mappings")


class BuildingEntityTypeConfig(BaseModel):
    """Entity type mapping configuration for building feature type"""

    attributes: List[BuildingAttributeConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                      description="List of attribute mappings")
    properties: List[BuildingPropertyConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                     description="List of property mappings")


class BuildingEntityConfig(BuildingEntityTypeConfig):
    """Entity mapping configuration for building feature type"""

    entity: BuildingEntity = Field(..., description="Type of entity")
    building_parts: List[BuildingPartConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                     description="List of building parts belonging to this building entity")


class BuildingFeatureType(BaseModel):
    """Feature type configuration for building feature type"""

    name: str = Field(..., description="Feature type name for the building")
    sql_path: str = Field(...,
                          description="Path to SQL definition for the building feature type. Must return at least a column named 'egid'.")
    egid_xpath: str = Field(...,
                            description="XPath expression to extract EGID identifier from city gml building entities")
    entity_mapping: BuildingEntityConfig = Field(..., description="Entity mapping configuration for the building")
    spatial_structure_mapping: BuildingSpatialEntityConfig = Field(...,
                                                                   description="Spatial structure mapping for the building")
    group_mapping: List[BuildingSourceConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                                      description="Group mappings for the building feature type")


class FeatureTypesConfig(BaseModel):
    """Feature types configuration for IFC export"""

    projections: List[ProjectionFeatureType] = Field(default_factory=list, json_schema_extra={"default": []},
                                                     description="List of projection feature type definitions")
    buildings: List[BuildingFeatureType] = Field(default_factory=list, json_schema_extra={"default": []},
                                                 description="List of building feature type definitions")


class PropertyConfig(BaseModel):
    """Property mapping configuration"""

    property: str = Field(..., description="Property name")
    property_set: str = Field(..., description="Property set name")
    value: str = Field(..., description="Property value")


class AttributeConfig(BaseModel):
    """Attribute mapping configuration"""

    attribute: str = Field(..., description="Attribute name (Only applied if the attribute exists on the entity)")
    value: str = Field(..., description="Attribute value")


class GroupEntityConfig(BaseModel):
    """Entity mapping configuration for group"""

    entity: GroupEntity = Field(..., description="Type of entity")
    attributes: List[AttributeConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                              description="List of attribute mappings")
    properties: List[PropertyConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                             description="List of property mappings")


class GroupConfig(BaseModel):
    """Group configuration for IFC export"""

    path: str = Field(..., description="Path identifier for the group")
    entity_mapping: GroupEntityConfig = Field(..., description="Entity mapping configuration for the group")


class IFCConfig(BaseModel):
    """IFC export configuration"""

    author: str = Field(..., description="Author of the IFC model")
    version: str = Field(..., description="IFC schema version")
    application_name: str = Field(..., description="Name of the application generating IFC")
    project_name: str = Field(..., description="Project name in IFC")
    geo_referencing: GeoReferencing = Field(..., description="Georeferencing configuration for IFC")
    feature_types: FeatureTypesConfig = Field(..., description="Configured feature types for IFC")
    groups: List[GroupConfig] = Field(default_factory=list, json_schema_extra={"default": []},
                                      description="List of group configurations for IFC")


class Configuration(BaseModel):
    """
    Root application configuration.

    This class defines the complete configuration model for the application. It aggregates
    settings for logging, internationalization (i18n), Redis and PostGIS database connections,
    STAC data sources, TIN generation, and IFC export configuration. The configuration is
    typically loaded from a YAML file using the `load()` class method, which supports
    environment variable expansion.
    """
    logging_level: str = Field(..., description="Logging level for the application (e.g., DEBUG, INFO, WARNING)")
    i18n: Optional[I18nConfig] = Field(None, description="Internationalization (i18n) configuration")
    redis: RedisConfig = Field(..., description="Redis configuration")
    db: DBConfig = Field(..., description="Database configuration")
    stac: STACConfig = Field(..., description="STAC configuration for external data sources")
    tin: TINConfig = Field(default_factory=lambda: TINConfig(grid_size=GridSize.SMALL, max_height_error=0.05),
                           description="TIN (Triangulated Irregular Network) generation configuration")
    ifc: IFCConfig = Field(..., description="IFC (Industry Foundation Classes) export configuration")

    @classmethod
    def load(cls, path: str) -> "Configuration":
        """
        Load configuration from a YAML file

        Args:
            path (str): Path to the YAML configuration file.

        Returns:
            Configuration: An instance of the configuration loaded from the provided file.

        Raises:
            FileNotFoundError: If the configuration file does not exist at the given path.
            ValidationError: If the YAML content does not conform to the expected schema.
        """
        text = Path(path).read_text()
        expanded = os.path.expandvars(text)
        return parse_yaml_raw_as(cls, expanded)

    @model_validator(mode="after")
    def check_conditional_configs(self):
        """
        Validate conditional configuration dependencies

        Returns:
            Configuration: The validated configuration instance.

        Raises:
            ValueError: If `stac.dtm_items_url` is missing while projections are defined,
                or if `stac.building_items_url` is missing while building feature types are defined.
        """
        if self.ifc.feature_types.projections and self.stac.dtm_items_url is None:
            raise ValueError("stac.dtm_items_url is required when ifc.feature_types.projections is not empty")
        if self.ifc.feature_types.buildings and self.stac.building_items_url is None:
            raise ValueError("stac.building_items_url is required when ifc.feature_types.building is not empty")
        return self


config = Configuration.load("/workspace/config.yml")
