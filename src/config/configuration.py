import yaml

from cs2bim.ifc.config.feature_class import FeatureClass
from cs2bim.ifc.config.group_config import GroupConfig
from cs2bim.ifc.config.property_config import PropertyConfig
from cs2bim.ifc.config.spatial_structure_config import SpatialStructureConfig
from cs2bim.ifc.enum.geo_referencing import GeoReferencing
from cs2bim.ifc.enum.triangulation_representation_type import TriangulationRepresentationType
from cs2bim.ifc.enum.element_entity_type import ElementEntityType
from cs2bim.ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType
from cs2bim.ifc.enum.group_entity_type import GroupEntityType
from cs2bim.ifc.model.color import Color


class Configuration:
    """
    Holds the configuration information
    """

    def __init__(self) -> None:
        pass

    def load(self, file_name: str) -> None:
        with open(file_name, "r") as file:
            self.config_file = yaml.safe_load(file)

        # init general configuration
        self.logging_level = self.config_file["logging_level"]

        # init postgis configuration
        db_config = self.config_file["db"]
        self.dbname = db_config["dbname"]
        self.user = db_config["user"]
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.password = db_config["password"]

        # init dtm configuration
        dtm_config = self.config_file["dtm"]
        self.stac_api = dtm_config["stac_api"]

        # init tin configuration
        tin_config = self.config_file["tin"]
        self.grid_size = tin_config["grid_size"]
        self.max_height_error = tin_config["max_height_error"]

        # init ifc configuration
        ifc_config = self.config_file["ifc"]
        self.author = ifc_config["author"]
        self.version = ifc_config["version"]
        self.application_name = ifc_config["application_name"]
        self.project_name = ifc_config["project_name"]
        self.geo_referencing = GeoReferencing[ifc_config["geo_referencing"]]
        self.triangulation_representation_type = TriangulationRepresentationType[
            ifc_config["triangulation_representation_type"]
        ]
        self.feature_classes = {}
        for key, value in ifc_config["feature_classes"].items():
            with open(value["sql"], "r") as file:
                sql = file.read()
            entity_type = ElementEntityType[value["entity_type"]]
            attributes = {}
            for attribute in value["attributes"]:
                attribute_name = attribute["attribute"]
                attribute_column = attribute["column"]
                attributes[attribute_name] = attribute_column
            properties = []
            for property in value["properties"]:
                property_name = property["name"]
                property_set = property["set"]
                property_column = property["column"]
                properties.append(PropertyConfig(property_name, property_set, property_column))
            spatial_structure_entity_type = SpatialStructureEntityType[value["spatial_structure"]["entity_type"]]
            spatial_structure_attributes = {}
            for spatial_structure_attribute in value["spatial_structure"]["attributes"]:
                attribute_name = spatial_structure_attribute["attribute"]
                attribute_value = spatial_structure_attribute["value"]
                spatial_structure_attributes[attribute_name] = attribute_value
            spatial_structure = SpatialStructureConfig(spatial_structure_entity_type, spatial_structure_attributes)
            group_columns = value["group_columns"]
            color = Color(
                value["color_definition"]["r"],
                value["color_definition"]["g"],
                value["color_definition"]["b"],
                value["color_definition"]["a"],
            )
            feature_class = FeatureClass(
                sql, entity_type, attributes, properties, spatial_structure, group_columns, color
            )
            self.feature_classes[key] = feature_class
        self.groups = {}
        for key, value in ifc_config["groups"].items():
            entity_type = GroupEntityType[value["entity_type"]]
            group_attributes = {}
            for group_attribute in value["attributes"]:
                attribute_name = group_attribute["attribute"]
                attribute_value = group_attribute["value"]
                group_attributes[attribute_name] = attribute_value
            ifc_group = GroupConfig(entity_type, group_attributes)
            self.groups[key] = ifc_group


config = Configuration()
