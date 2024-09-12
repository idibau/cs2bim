import yaml

from cs2bim.config.feature_class import FeatureClass, Property
from cs2bim.config.geo_referencing import GeoReferencing
from cs2bim.geometry.triangulation import TriangulationRepresentationType
from cs2bim.ifc.entity.ifc_element import IfcElementEntityType
from cs2bim.ifc.entity.ifc_spatial_structure import IfcSpatialStructure, IfcSpatialStructureEntityType


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
        self.schema = db_config["schema"]

        # init swisstopo configuration
        swisstopo_config = self.config_file["swisstopo"]
        self.stac_api = swisstopo_config["stac_api"]

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
            element_name_column = value["element_name_column"]
            properties = []
            for property in value["properties"]:
                property_name = property["name"]
                property_column = property["column"]
                property_set = property["set"]
                properties.append(Property(property_name, property_column, property_set))
            entity_type = IfcElementEntityType[value["entity_type"]]
            spatial_structure = IfcSpatialStructure(
                IfcSpatialStructureEntityType[value["spatial_structure"]["entity_type"]],
                value["spatial_structure"]["name"],
            )
            group_columns = value["group_columns"]
            color_definition = (
                value["color_definition"]["r"],
                value["color_definition"]["g"],
                value["color_definition"]["b"],
                value["color_definition"]["a"],
            )
            feature_class = FeatureClass(
                sql,
                element_name_column,
                properties,
                entity_type,
                spatial_structure,
                group_columns,
                color_definition,
            )
            self.feature_classes[key] = feature_class


config = Configuration()
