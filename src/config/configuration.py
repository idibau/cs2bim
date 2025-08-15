import json
from pathlib import Path
from typing import List
from typing import Optional, Dict

from pydantic import BaseModel, model_validator
from pydantic_yaml import parse_yaml_file_as

from config.element_entity_type import ElementEntityType
from config.geo_referencing import GeoReferencing
from config.group_entity_type import GroupEntityType
from config.spatial_structure_entity_type import SpatialStructureEntityType
from config.triangulation_representation_type import TriangulationRepresentationType


class PropertyConfig(BaseModel):
    name: str
    set: str
    column: str


class ValueAttribute(BaseModel):
    name: str
    value: str


class SpatialStructureConfig(BaseModel):
    entity_type: SpatialStructureEntityType
    attributes: List[ValueAttribute]

    def get_key(self) -> str:
        return f"{json.dumps([attribute.model_dump_json() for attribute in self.attributes], sort_keys=True)}-{self.entity_type.name}"


class Color(BaseModel):
    r: float
    g: float
    b: float
    a: float


class Attribute(BaseModel):
    name: str
    column: str


class ClippedTerrainFeatureClass(BaseModel):
    sql_path: str
    entity_type: ElementEntityType
    attributes: List[Attribute]
    properties: List[PropertyConfig]
    spatial_structure: SpatialStructureConfig
    group_columns: List[str]
    color: Color


class BuildingFeatureClass(BaseModel):
    entity_type: ElementEntityType


class GroupConfig(BaseModel):
    entity_type: GroupEntityType
    attributes: List[ValueAttribute]


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
    buildings: Dict[str, BuildingFeatureClass]
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
        if self.ifc.buildings and self.stac.building_items_url is None:
            raise ValueError("stac.building_items_url is required when ifc.buildings is not empty")
        return self


config = Configuration.load("/workspace/config.yml")
