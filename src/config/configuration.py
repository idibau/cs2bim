import json

from ifcopenshell.validate import entity_type
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_file_as
from typing import Dict, List
from pathlib import Path

from cs2bim.ifc.enum.geo_referencing import GeoReferencing
from cs2bim.ifc.enum.triangulation_representation_type import TriangulationRepresentationType
from cs2bim.ifc.enum.element_entity_type import ElementEntityType
from cs2bim.ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType
from cs2bim.ifc.enum.group_entity_type import GroupEntityType


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


class FeatureClass(BaseModel):
    sql_path: str
    entity_type: ElementEntityType
    attributes: List[Attribute]
    properties: List[PropertyConfig]
    spatial_structure: SpatialStructureConfig
    group_columns: List[str]
    color: Color


class GroupConfig(BaseModel):
    entity_type: GroupEntityType
    attributes: List[ValueAttribute]


class DBConfig(BaseModel):
    dbname: str
    user: str
    host: str
    port: int
    password: str


class DTMConfig(BaseModel):
    stac_api: str


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
    feature_classes: Dict[str, FeatureClass]
    groups: Dict[str, GroupConfig]


class Configuration(BaseModel):
    logging_level: str
    db: DBConfig
    dtm: DTMConfig
    tin: TINConfig
    ifc: IFCConfig

    @classmethod
    def load(cls, path: str | Path) -> "Configuration":
        return parse_yaml_file_as(cls, path)


config = Configuration.load("/workspace/config.yml")
