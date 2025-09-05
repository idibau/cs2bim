import json
from pathlib import Path
from typing import List, Annotated
from typing import Optional, Dict

from pydantic import BaseModel, model_validator, Field, confloat
from pydantic_yaml import parse_yaml_file_as

from config.element_attribute import ElementAttribute
from config.element_entity_type import ElementEntityType
from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.spatial_structure_entity_type import SpatialStructureEntityType
from config.triangulation_representation_type import TriangulationRepresentationType


class SqlToPropertyConfig(BaseModel):
    name: str
    set: str
    column: str


class XmlToPropertyConfig(BaseModel):
    name: str
    set: str
    xpath: str


class AttributeConfig(BaseModel):
    attribute: ElementAttribute
    value: str


class SqlToAttributeConfig(BaseModel):
    attribute: ElementAttribute
    column: str


class XmlToAttributeConfig(BaseModel):
    attribute: ElementAttribute
    xpath: str


class SpatialStructureConfig(BaseModel):
    entity_type: SpatialStructureEntityType
    attributes: Optional[List[AttributeConfig]] = Field(default_factory=list)

    def get_id(self) -> str:
        return f"{json.dumps([attribute.model_dump() for attribute in self.attributes], sort_keys=True)}-{self.entity_type.name}"


class Color(BaseModel):
    r: Annotated[float, Field(ge=0.0, le=1.0)]
    g: Annotated[float, Field(ge=0.0, le=1.0)]
    b: Annotated[float, Field(ge=0.0, le=1.0)]
    a: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0


class ClippedTerrainFeatureClass(BaseModel):
    sql_path: str
    entity_type: ElementEntityType
    spatial_structure: SpatialStructureConfig
    attributes: Optional[List[SqlToAttributeConfig]] = Field(default_factory=list)
    properties: Optional[List[SqlToPropertyConfig]] = Field(default_factory=list)
    group_columns: Optional[List[str]] = Field(default_factory=list)
    color: Color


class BuildingPartConfig(BaseModel):
    xpath: str
    entity_type: ElementEntityType
    attributes: Optional[List[XmlToAttributeConfig]] = Field(default_factory=list)
    properties: Optional[List[XmlToPropertyConfig]] = Field(default_factory=list)
    color: Color


class BuildingFeatureClass(BaseModel):
    sql_path: str
    egid_xpath: str
    spatial_structure: SpatialStructureConfig
    attributes: Optional[List[XmlToAttributeConfig]] = Field(default_factory=list)
    properties: Optional[List[XmlToPropertyConfig]] = Field(default_factory=list)
    building_parts: Optional[List[BuildingPartConfig]] = Field(default_factory=list)
    group_columns: Optional[List[str]] = Field(default_factory=list)  # TODO: Implement


class GroupConfig(BaseModel):
    entity_type: GroupEntityType
    attributes: Optional[List[AttributeConfig]] = Field(default_factory=list)


class DBConfig(BaseModel):
    dbname: str
    user: str
    host: str
    port: int
    password: str


class STACConfig(BaseModel):
    dtm_items_url: Optional[str] = None
    building_items_url: Optional[str] = None


class TINConfig(BaseModel):
    grid_size: float
    max_height_error: float


class IFCConfig(BaseModel):
    author: str
    version: str
    application_name: str
    project_name: str
    geo_referencing: GeoReferencing
    triangulation_representation_type: TriangulationRepresentationType
    clipped_terrain: Dict[str, ClippedTerrainFeatureClass]
    building: Dict[str, BuildingFeatureClass]
    groups: Dict[str, GroupConfig]


class Configuration(BaseModel):
    logging_level: str
    db: DBConfig
    stac: STACConfig
    tin: TINConfig
    ifc: IFCConfig

    @classmethod
    def load(cls, path: str | Path) -> "Configuration":
        return parse_yaml_file_as(cls, path)

    @model_validator(mode="after")
    def check_conditional_configs(self):
        if self.ifc.clipped_terrain and self.stac.dtm_items_url is None:
            raise ValueError("stac.dtm_items_url is required when ifc.clipped_terrain is not empty")
        if self.ifc.building and self.stac.building_items_url is None:
            raise ValueError("stac.building_items_url is required when ifc.building is not empty")
        return self


config = Configuration.load("/workspace/config.yml")
