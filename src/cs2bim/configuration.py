import yaml
from tin2ifc.enum.geo_referencing import GeoReferencing
from tin2ifc.enum.triangulation_representation_type import TriangulationRepresentationType
from tin2ifc.enum.element_entity_type import ElementEntityType
from tin2ifc.model.feature_class import FeatureClass
from tin2ifc.enum.spatial_structure_entity_type import SpatialStructureEntityType
from tin2ifc.model.entitiy.spatial_structure import SpatialStructure

class Configuration:
    """
    Holds the configuration information
    """

    def __init__(self) -> None:
        pass

    def load(self, file_name: str) -> None:
        with open(file_name, "r") as file:
            self.config_file = yaml.safe_load(file)

        # init db configuration
        db_config = self.config_file["db"]
        self.dbname = db_config["dbname"]
        self.user = db_config["user"]
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.password = db_config["password"]

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
            entity_type = ElementEntityType[value["entity_type"]]
            spatial_structure = SpatialStructure(
                SpatialStructureEntityType[value["spatial_structure"]["entity_type"]],
                value["spatial_structure"]["name"],
            )
            groups = value["groups"]
            color_definition = (
                value["color_definition"]["r"],
                value["color_definition"]["g"],
                value["color_definition"]["b"],
                value["color_definition"]["a"],
            )
            feature_class = FeatureClass(key, entity_type, spatial_structure, groups, color_definition)
            self.feature_classes[key] = feature_class


config = Configuration()
