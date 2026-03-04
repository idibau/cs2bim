import logging
from lxml import etree
from lxml.etree import _Element as XmlElement
from typing import Any

from shapely import Point

from config.building_source import BuildingSource
from config.configuration import config, BuildingFeatureType, BuildingAttributeConfig, BuildingPropertyConfig
from config.gml_geometry import GmlGeometry
from core.ifc.model.building.building import BuildingPart, Building
from core.ifc.model.element import Element
from core.ifc.model.building.composite_solid import CompositeSolid
from core.ifc.model.building.multi_surface import MultiSurface
from core.ifc.model.building.namespace import namespace
from core.ifc.model.building.solid import Solid
from service.postgis_service import PostgisService
from service.bounding_box import BoundingBox
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class BuildingProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon: str, project_origin: Point) -> dict[str, list[Building]]:
        feature_types = {b.name: b for b in config.ifc.building_feature_types}
        if not feature_types:
            logger.info("no building feature types configured")
            return {}

        logger.info(f"fetch city gml files")
        bounding_box = BoundingBox.from_wkts([polygon])
        city_gmls = self.stac_service.fetch_city_gml_assets(bounding_box)
        logger.info(f"fetched {len(city_gmls)} city gml files")

        buildings_by_key = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"create {feature_type_key} feature type")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            sql_result = self.postgis_service.fetch_feature_type_elements(sql, polygon)
            element_rows_by_egid = {row["egid"]: row for row in sql_result}

            for index, city_gml in enumerate(city_gmls):
                logger.info(f"processing city gml {index + 1}/{len(city_gmls)}")
                for key, building_config in feature_types.items():
                    context_iter = etree.iterparse(city_gml, events=("end",),
                                                   tag="{http://www.opengis.net/citygml/building/2.0}Building")
                    for event, building_gml in context_iter:
                        value_elem = building_gml.find(building_config.egid_xpath, namespaces=namespace)
                        if value_elem is not None:
                            egid = value_elem.text.strip()
                            if egid in element_rows_by_egid:
                                logger.debug(f"process building {egid}")
                                building = self.create_building(building_gml, building_config, project_origin,
                                                                element_rows_by_egid[egid])
                                if not feature_type_key in buildings_by_key:
                                    buildings_by_key[feature_type_key] = []
                                buildings_by_key[feature_type_key].append(building)
                                logger.debug(f"finished processing building")
                        building_gml.clear()

                        while building_gml.getprevious() is not None:
                            del building_gml.getparent()[0]
        return buildings_by_key

    def create_building(self, building_gml: XmlElement, building_config: BuildingFeatureType,
                        project_origin: Point, element_row: dict[str, Any]) -> Building:
        building = Building()
        self.add_attributes(building, building_config.entity_mapping.attributes, building_gml, element_row)
        self.add_properties(building, building_config.entity_mapping.properties, building_gml, element_row)
        self.add_groups(building, building_config, building_gml, element_row)
        logger.debug(f"start processing building parts")
        for building_part_config in building_config.entity_mapping.building_parts:
            geometry_mapping = building_part_config.geometry_mapping
            geometry_gmls = building_gml.xpath(geometry_mapping.xpath, namespaces=namespace)
            for geometry_gml in geometry_gmls:
                if geometry_mapping.geometry == GmlGeometry.SOLID:
                    geometry = Solid()
                elif geometry_mapping.geometry == GmlGeometry.COMPOSITE_SOLID:
                    geometry = CompositeSolid()
                elif geometry_mapping.geometry == GmlGeometry.MULTI_SURFACE:
                    geometry = MultiSurface()
                else:
                    raise NotImplementedError(
                        f"building step for gml geometry type {geometry_mapping.geometry} not implemented")
                geometry.from_gml(geometry_gml, project_origin)
                building_part = BuildingPart(building_part_config.entity, geometry, building_part_config.color)
                building.add_building_part(building_part)

        spatial_structure = Element()
        self.add_attributes(spatial_structure, building_config.spatial_structure_mapping.attributes, building_gml,
                            element_row)
        self.add_properties(spatial_structure, building_config.spatial_structure_mapping.properties, building_gml,
                            element_row)
        building.spatial_structure = spatial_structure
        return building

    def add_attributes(self, element: Element, attributes: list[BuildingAttributeConfig], building_gml: XmlElement,
                       element_row: dict[str, Any]):
        for attribute in attributes:
            if attribute.source.type == BuildingSource.CITY_GML:
                value_elem = building_gml.find(attribute.source.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_attribute(attribute.attribute, value_elem.text.strip())
            elif attribute.source.type == BuildingSource.SQL:
                if attribute.source.expression in element_row:
                    element.add_attribute(attribute.attribute, element_row[attribute.source.expression])
            elif attribute.source.type == BuildingSource.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, element: Element, properties: list[BuildingPropertyConfig], building_gml: XmlElement,
                       element_row: dict[str, Any]):
        for p in properties:
            if p.source.type == BuildingSource.CITY_GML:
                value_elem = building_gml.find(p.source.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_property(p.property_set, p.property, value_elem.text.strip())
            elif p.source.type == BuildingSource.SQL:
                if p.source.expression in element_row:
                    element.add_property(p.property_set, p.property, element_row[p.source.expression])
            elif p.source.type == BuildingSource.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, element: Element, building_config: BuildingFeatureType, building_gml: XmlElement,
                   element_row: dict[str, Any]):
        for group_mapping in building_config.group_mapping:
            if group_mapping.type == BuildingSource.CITY_GML:
                value_elem = building_gml.find(group_mapping.expression, namespaces=namespace)
                if value_elem is not None:
                    element.add_group(value_elem.text.strip())
            elif group_mapping.type == BuildingSource.SQL:
                if group_mapping.expression in element_row:
                    element.add_group(element_row[group_mapping.expression])
            elif group_mapping.type == BuildingSource.STATIC:
                element.add_group(group_mapping.expression)
