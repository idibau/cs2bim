import logging

from lxml import etree

from config.building_source import BuildingSource
from config.configuration import config
from config.gml_geometry import GmlGeometry
from core.ifc.model.building import BuildingPart, Building
from core.ifc.model.element import Element
from core.ifc.model.gml.composite_solid import CompositeSolid
from core.ifc.model.gml.multi_surface import MultiSurface
from core.ifc.model.gml.namespace import namespace
from core.ifc.model.gml.solid import Solid
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class BuildingProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, origin):
        feature_types = {b.name: b for b in config.ifc.feature_types.buildings}
        if not feature_types:
            logger.info("No building feature typees configured")
            return {}

        logger.info(f"fetch city gml files")
        bounding_box = self.postgis_service.get_bounding_box([polygon])
        city_gmls = self.stac_service.fetch_city_gml_assets(bounding_box)
        logger.info(f"fetched {len(city_gmls)} city gml files")

        buildings = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"create {feature_type_key} feature type")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            result_set = self.postgis_service.fetch_feature_type_elements(sql, polygon)
            egids = {item["egid"]: item for item in result_set}

            for index, city_gml in enumerate(city_gmls):
                logger.info(f"processing city gml {index + 1}/{len(city_gmls)}")
                context_iter = etree.iterparse(city_gml, events=("end",),
                                               tag="{http://www.opengis.net/citygml/building/2.0}Building")

                for key, building_config in feature_types.items():
                    for event, building in context_iter:
                        value_elem = building.find(building_config.egid_xpath, namespaces=namespace)
                        if value_elem is not None:
                            egid = value_elem.text.strip()
                            if egid in egids:
                                logger.debug(f"process building {egid}")
                                building_model = self.create_building_model(building, building_config, origin,
                                                                            egids[egid])
                                if not feature_type_key in buildings:
                                    buildings[feature_type_key] = []
                                buildings[feature_type_key].append(building_model)
                                logger.debug(f"finished processing building")
                        building.clear()

                        while building.getprevious() is not None:
                            del building.getparent()[0]
        return buildings

    def create_building_model(self, building, building_config, origin, result_set):
        building_model = Building()
        self.add_attributes(building, building_config.entity_mapping.attributes, building_model, result_set)
        self.add_properties(building, building_config.entity_mapping.properties, building_model, result_set)
        self.add_groups(building, building_config, building_model, result_set)
        logger.debug(f"start processing building parts")
        for building_part_config in building_config.entity_mapping.building_parts:
            geometry_mapping = building_part_config.geometry_mapping
            geometry_gmls = building.xpath(geometry_mapping.xpath, namespaces=namespace)
            if geometry_mapping.geometry == GmlGeometry.SOLID:
                geometry = Solid()
            elif geometry_mapping.geometry == GmlGeometry.COMPOSITE_SOLID:
                geometry = CompositeSolid()
            elif geometry_mapping.geometry == GmlGeometry.MULTI_SURFACE:
                geometry = MultiSurface()
            else:
                raise NotImplementedError(
                    f"building step for gml geometry type {geometry_mapping.geometry} not implemented")
            for geometry_gml in geometry_gmls:
                geometry.from_gml(geometry_gml, origin)
                building_part = BuildingPart(building_part_config.entity, geometry, building_part_config.color)
                building_model.add_building_part(building_part)

        spatial_structure = Element()
        self.add_attributes(building, building_config.spatial_structure_mapping.attributes, spatial_structure,
                            result_set)
        self.add_properties(building, building_config.spatial_structure_mapping.properties, spatial_structure,
                            result_set)
        building_model.spatial_structure = spatial_structure
        return building_model

    def add_attributes(self, building, attributes, element, result_set):
        for attribute in attributes:
            if attribute.source.type == BuildingSource.CITY_GML:
                value_elem = building.find(attribute.source.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_attribute(attribute.attribute, value_elem.text.strip())
            elif attribute.source.type == BuildingSource.SQL:
                if attribute.source.expression in result_set:
                    element.add_attribute(attribute.attribute, result_set[attribute.source.expression])
            elif attribute.source.type == BuildingSource.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, building, properties, element, result_set):
        for p in properties:
            if p.source.type == BuildingSource.CITY_GML:
                value_elem = building.find(p.source.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_property(p.property_set, p.property, value_elem.text.strip())
            elif p.source.type == BuildingSource.SQL:
                if p.source.expression in result_set:
                    element.add_property(p.property_set, p.property, result_set[p.source.expression])
            elif p.source.type == BuildingSource.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, building, building_config, element, result_set):
        for group_mapping in building_config.group_mapping:
            if group_mapping.type == BuildingSource.CITY_GML:
                value_elem = building.find(group_mapping.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_group(value_elem.text.strip())
            elif group_mapping.type == BuildingSource.SQL:
                if group_mapping.expression in result_set:
                    element.add_group(result_set[group_mapping.expression])
            elif group_mapping.type == BuildingSource.STATIC:
                element.add_group(group_mapping.expression)
