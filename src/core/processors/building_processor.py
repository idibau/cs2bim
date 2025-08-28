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

            ns = {
                "bldg": "http://www.opengis.net/citygml/building/2.0",
                "gml": "http://www.opengis.net/gml",
                "gen": "http://www.opengis.net/citygml/generics/2.0",
            }

            for index, city_gml in enumerate(city_gmls):
                logger.info(f"processing city gml {index}/{len(city_gmls)}")
                context_iter = etree.iterparse(city_gml, events=("end",),
                                               tag="{http://www.opengis.net/citygml/building/2.0}Building")

                for key, building_config in self.feature_classes.items():
                    for event, building in context_iter:
                        value_elem = building.find(building_config.egid_xpath, namespaces=ns)
                        if value_elem is not None:
                            egid = value_elem.text.strip()
                            if egid in egids:
                                logger.info(f"process building {egid}")
                                building_model = Building()

                                for building_attribute in building_config.attributes:
                                    value_elem = building.find(building_attribute.xpath, namespaces=ns)
                                    if value_elem is not None:
                                        building_model.add_attribute(building_attribute.name, value_elem.text.strip())

                                for building_property in building_config.properties:
                                    value_elem = building.find(building_property.xpath, namespaces=ns)
                                    if value_elem is not None:
                                        building_model.add_property(building_property.set, building_property.name, value_elem.text.strip())

                                logger.debug(f"start processing building parts")
                                for building_part_config in building_config.building_parts:
                                    points = []
                                    for pos_list in building.xpath(building_part_config.xpath, namespaces=ns):
                                        if pos_list is None:
                                            continue
                                        coords = list(map(float, pos_list.text.split()))
                                        points.append([(float(coords[i] - origin[0]), float(coords[i + 1] - origin[1]),
                                                        float(coords[i + 2] - origin[2])) for i in
                                                       range(0, len(coords), 3)])
                                    building_part = BuildingPart(building_part_config.entity_type, points, building_part_config.color, building_part_attributes)

                                    for building_part_attribute in building_part_config.attributes:
                                        value_elem = building.find(building_part_attribute.xpath, namespaces=ns)
                                        if value_elem is not None:
                                            building_part.add_attribute(building_part_attribute.name, value_elem.text.strip())

                                    for building_part_property in building_part_config.properties:
                                        value_elem = building.find(building_part_property.xpath, namespaces=ns)
                                        if value_elem is not None:
                                            building_part.add_property(building_part_property.set, building_part_property.name,
                                                                        value_elem.text.strip())

                                    building_model.add_building_part(building_part)

                                logger.info(f"finished processing building")
                                model.add_building(key, building_model)
                        building.clear()

                        while building.getprevious() is not None:
                            del building.getparent()[0]
