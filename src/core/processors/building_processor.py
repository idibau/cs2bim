import logging

from lxml import etree

from config.configuration import config
from core.ifc.model.building import BuildingPart, Building
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class BuildingProcessor:

    def __init__(self):
        self.feature_classes = config.ifc.building
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

        self.ns = {
            "bldg": "http://www.opengis.net/citygml/building/2.0",
            "gml": "http://www.opengis.net/gml",
            "gen": "http://www.opengis.net/citygml/generics/2.0",
        }

    def process(self, polygon, origin, model):
        if not self.feature_classes:
            logger.info("No building feature classes configured")
            return

        logger.info(f"fetch city gml files")
        bounding_box = self.postgis_service.get_bounding_box([polygon])
        city_gmls = self.stac_service.fetch_city_gml_assets(bounding_box)
        logger.info(f"fetched {len(city_gmls)} city gml files")

        for feature_class_key, feature_class in self.feature_classes.items():
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            egids = [item["egid"] for item in self.postgis_service.fetch_feature_class_elements(sql, polygon)]

            for index, city_gml in enumerate(city_gmls):
                logger.info(f"processing city gml {index + 1}/{len(city_gmls)}")
                context_iter = etree.iterparse(city_gml, events=("end",),
                                               tag="{http://www.opengis.net/citygml/building/2.0}Building")

                for key, building_config in self.feature_classes.items():
                    for event, building in context_iter:
                        value_elem = building.find(building_config.egid_xpath, namespaces=self.ns)
                        if value_elem is not None:
                            egid = value_elem.text.strip()
                            if egid in egids:
                                logger.info(f"process building {egid}")
                                building_model = self.create_building_model(building, building_config, origin)
                                model.add_building(key, building_model)
                                logger.info(f"finished processing building")
                        building.clear()

                        while building.getprevious() is not None:
                            del building.getparent()[0]

    def create_building_model(self, building, building_config, origin):
        building_model = Building()
        self.add_attributes_and_properties(building, building_config, building_model)
        logger.debug(f"start processing building parts")
        for building_part_config in building_config.building_parts:
            points = []
            for pos_list in building.xpath(building_part_config.xpath, namespaces=self.ns):
                if pos_list is None:
                    continue
                coords = list(map(float, pos_list.text.split()))
                points.append([(float(coords[i] - origin[0]), float(coords[i + 1] - origin[1]),
                                float(coords[i + 2] - origin[2])) for i in
                               range(0, len(coords), 3)])
            building_part = BuildingPart(building_part_config.entity_type, points, building_part_config.color)
            self.add_attributes_and_properties(building, building_part_config, building_part)
            building_model.add_building_part(building_part)
        return building_model

    def add_attributes_and_properties(self, building, element_config, element):
        for attribute in element_config.attributes:
            value_elem = building.find(attribute.xpath, namespaces=self.ns)
            if value_elem is not None:
                element.add_attribute(attribute.name, value_elem.text.strip())
        for property in element_config.properties:
            value_elem = building.find(property.xpath, namespaces=self.ns)
            if value_elem is not None:
                element.add_property(property.set, property.name, value_elem.text.strip())
