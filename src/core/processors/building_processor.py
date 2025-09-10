import logging

from lxml import etree

from config.source_type import SourceType
from core.ifc.model.building import BuildingPart, Building
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class BuildingProcessor:

    def __init__(self, config):
        self.feature_classes = {b.name: b for b in config.ifc.building}
        self.postgis_service = PostgisService(config.db)
        self.stac_service = STACService(config.stac)

        self.ns = {
            "bldg": "http://www.opengis.net/citygml/building/2.0",
            "gml": "http://www.opengis.net/gml",
            "gen": "http://www.opengis.net/citygml/generics/2.0",
        }

    def process(self, polygon, origin):
        if not self.feature_classes:
            logger.info("No building feature classes configured")
            return {}

        logger.info(f"fetch city gml files")
        bounding_box = self.postgis_service.get_bounding_box([polygon])
        city_gmls = self.stac_service.fetch_city_gml_assets(bounding_box)
        logger.info(f"fetched {len(city_gmls)} city gml files")

        buildings = {}
        for feature_class_key, feature_class in self.feature_classes.items():
            logger.info(f"create {feature_class_key} feature class")
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            result_set = self.postgis_service.fetch_feature_class_elements(sql, polygon)
            egids = {item["egid"]: item for item in result_set}

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
                                logger.debug(f"process building {egid}")
                                building_model = self.create_building_model(building, building_config, origin,
                                                                            egids[egid])
                                if not feature_class_key in buildings:
                                    buildings[feature_class_key] = []
                                buildings[feature_class_key].append(building_model)
                                logger.debug(f"finished processing building")
                        building.clear()

                        while building.getprevious() is not None:
                            del building.getparent()[0]
        return buildings

    def create_building_model(self, building, building_config, origin, result_set):
        building_model = Building()
        self.add_attributes(building, building_config, building_model, result_set)
        self.add_properties(building, building_config, building_model, result_set)
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
            self.add_attributes(building, building_part_config, building_part, result_set)
            self.add_properties(building, building_part_config, building_part, result_set)
            self.add_groups(building, building_part_config, building_part, result_set)
            building_model.add_building_part(building_part)
        return building_model

    def add_attributes(self, building, element_config, element, result_set):
        for attribute in element_config.attributes:
            if attribute.source.type == SourceType.CITY_GML:
                value_elem = building.find(attribute.source.expression, namespaces=self.ns)
                if value_elem is not None:
                    element.add_attribute(attribute.attribute, value_elem.text.strip())
            elif attribute.source.type == SourceType.SQL:
                if attribute.source.expression in result_set:
                    element.add_attribute(attribute.attribute, result_set[attribute.source.expression])
            elif attribute.source.type == SourceType.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, building, element_config, element, result_set):
        for p in element_config.properties:
            if p.source.type == SourceType.CITY_GML:
                value_elem = building.find(p.source.expression, namespaces=self.ns)
                if value_elem is not None:
                    element.add_property(p.property_set, p.property, value_elem.text.strip())
            elif p.source.type == SourceType.SQL:
                if p.source.expression in result_set:
                    element.add_property(p.property_set, p.property, result_set[p.source.expression])
            elif p.source.type == SourceType.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, building, element_config, element, result_set):
        for group_assignment in element_config.group_assignments:
            if group_assignment.type == SourceType.CITY_GML:
                value_elem = building.find(group_assignment.expression, namespaces=self.ns)
                if value_elem is not None:
                    element.add_group(value_elem.text.strip())
            elif group_assignment.type == SourceType.SQL:
                if group_assignment.expression in result_set:
                    element.add_group(result_set[group_assignment.expression])
            elif group_assignment.type == SourceType.STATIC:
                element.add_group(group_assignment.expression)
