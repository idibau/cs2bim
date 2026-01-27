import logging
from shapely import Point, wkb
from shapely.affinity import translate
from typing import Any

from config.configuration import config, ExtrusionAttributeConfig, ExtrusionPropertyConfig, ExtrusionFeatureType
from config.extrusion_source import ExtrusionSource
from core.ifc.model.element import Element
from core.ifc.model.extrusion.circle import Circle
from core.ifc.model.extrusion.cross_section import CrossSection
from core.ifc.model.extrusion.cross_section_type import CrossSectionType
from core.ifc.model.extrusion.egg import Egg
from core.ifc.model.extrusion.extrusion import Extrusion
from core.ifc.model.extrusion.extrusion_type import ExtrusionType
from core.ifc.model.extrusion.vertical_extrusion import VerticalExtrusion
from core.ifc.model.extrusion.polygon import Polygon
from core.ifc.model.extrusion.polyline_extrusion import PolylineExtrusion
from core.ifc.model.extrusion.rectangle import Rectangle
from core.ifc.model.feature_element import FeatureElement
from service.postgis_service import PostgisService

logger = logging.getLogger(__name__)


class ExtrusionProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()

    def process(self, polygon: str, project_origin: Point) -> dict[str, list[Extrusion]]:
        feature_types = {b.name: b for b in config.ifc.extrusion_feature_types}
        if not feature_types:
            logger.info("no building feature types configured")
            return {}

        extrusions_by_key = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"create {feature_type_key} feature type")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            sql_result = self.postgis_service.fetch_feature_type_elements(sql, polygon)

            extrusions = []
            for index, row in enumerate(sql_result):
                logger.info(f"processing extrusion lines {index + 1}/{len(sql_result)}")

                try:
                    cross_section_type = CrossSectionType[row["cross_section"]]
                except Exception:
                    logger.warning(f"no valid cross section type {row['cross_section']}")
                    continue

                SECTION_FACTORIES = {
                    CrossSectionType.EGG: lambda row: self.create_simple_section(row, Egg),
                    CrossSectionType.CIRCLE: lambda row: self.create_simple_section(row, Circle),
                    CrossSectionType.RECTANGLE: self.create_rectangle,
                    CrossSectionType.POLYGON_LOCAL: lambda row: self.create_polygon(row, True),
                    CrossSectionType.POLYGON_GLOBAL: lambda row: self.create_polygon(row, False),
                }

                factory_func = SECTION_FACTORIES.get(cross_section_type)
                if not factory_func:
                    logger.warning(f"Not supported cross section type: {cross_section_type.name}")
                    continue

                cross_section = factory_func(row)
                if cross_section is None:
                    continue

                try:
                    extrusion_type = ExtrusionType[row["extrusion_type"]]
                except ValueError:
                    logger.warning(f"no valid extrusion type {row['extrusion_type']}")
                    continue

                EXTRUSION_FACTORIES = {
                    ExtrusionType.POINT: lambda row, cs: self.create_vertical_extrusion(row, cs, project_origin),
                    ExtrusionType.SURFACE: lambda row, cs: self.create_vertical_extrusion(row, cs, project_origin),
                    ExtrusionType.POLYLINE: lambda row, cs: self.create_polyline_extrusion(row, cs, project_origin),
                }

                factory_func = EXTRUSION_FACTORIES.get(extrusion_type)
                if not factory_func:
                    logger.warning(f"Not supported extrusion type: {extrusion_type.name}")
                    continue
                extrusion_result = factory_func(row, cross_section)
                if extrusion_result is not None:
                    if feature_type.entity_type_mapping is not None:
                        element_type = Element()
                        self.add_attributes(element_type, feature_type.entity_type_mapping.attributes, row)
                        self.add_properties(element_type, feature_type.entity_type_mapping.properties, row)
                        extrusion_result.element_type = element_type
                    extrusions.append((extrusion_result, row))

            for extrusion, row in extrusions:
                self.add_attributes(extrusion, feature_type.entity_mapping.attributes, row)
                self.add_properties(extrusion, feature_type.entity_mapping.properties, row)
                self.add_groups(extrusion, feature_type, row)

                spatial_structure = Element()
                self.add_attributes(spatial_structure, feature_type.spatial_structure_mapping.attributes, row)
                self.add_properties(spatial_structure, feature_type.spatial_structure_mapping.properties, row)
                extrusion.spatial_structure = spatial_structure

                if not feature_type_key in extrusions_by_key:
                    extrusions_by_key[feature_type_key] = []
                extrusions_by_key[feature_type_key].append(extrusion)
        return extrusions_by_key

    def create_simple_section(self, row: dict[str, Any], section_class):
        width = row["width"]
        if not width:
            logger.warning(f"Mandatory 'width' missing for {section_class.__name__}")
            return None
        return section_class(width / 2)

    def create_rectangle(self, row: dict[str, Any]) -> Rectangle | None:
        width = row["width"]
        height = row["height"]
        if not width or not height:
            logger.warning("Mandatory 'width' or 'height' missing for Rectangle")
            return None
        return Rectangle(width, height)

    def create_polygon(self, row: dict[str, Any], local: bool) -> Polygon | None:
        polygon_hex = row["area"]
        if not polygon_hex:
            logger.warning("Mandatory 'area' data missing for Polygon")
            return None
        try:
            polygon_wkb = bytes.fromhex(polygon_hex)
            polygon = wkb.loads(polygon_wkb)
            return Polygon(polygon, local)
        except Exception as e:
            logger.error(f"Failed to load polygon from hex: {e}")
            return None

    def create_vertical_extrusion(self, row: dict[str, Any], cross_section: CrossSection,
                                  project_origin: Point) -> VerticalExtrusion | None:
        start_hex = row["start_point"]
        end_hex = row["end_point"]
        orientation = row["orientation"] if "orientation" in row else None
        if not start_hex or not end_hex:
            logger.warning("Missing 'start_point' or 'end_point' for VerticalExtrusion")
            return None
        try:
            start_point = wkb.loads(bytes.fromhex(start_hex))
            end_point = wkb.loads(bytes.fromhex(end_hex))
            start_point = translate(start_point, xoff=-project_origin.x, yoff=-project_origin.y, zoff=-project_origin.z)
            end_point = translate(end_point, xoff=-project_origin.x, yoff=-project_origin.y, zoff=-project_origin.z)
            return VerticalExtrusion(cross_section, start_point, end_point, orientation)
        except Exception as e:
            logger.error(f"Failed to load WKB points for VerticalExtrusion: {e}")
            return None

    def create_polyline_extrusion(self, row: dict[str, Any], cross_section: CrossSection,
                                  project_origin: Point) -> PolylineExtrusion | None:
        polyline_hex = row["polyline"]
        if not polyline_hex:
            logger.warning("Missing 'polyline' data for PolylineExtrusion")
            return None
        try:
            polyline = wkb.loads(bytes.fromhex(polyline_hex))
            polyline = translate(polyline, xoff=-project_origin.x, yoff=-project_origin.y, zoff=-project_origin.z)
            return PolylineExtrusion(cross_section, polyline)
        except Exception as e:
            logger.error(f"Failed to load WKB polyline for PolylineExtrusion: {e}")
            return None

    def add_attributes(self, element: Element, attributes: list[ExtrusionAttributeConfig],
                       element_row: dict[str, Any]):
        for attribute in attributes:
            if attribute.source.type == ExtrusionSource.SQL:
                if attribute.source.expression in element_row:
                    element.add_attribute(attribute.attribute, element_row[attribute.source.expression])
            elif attribute.source.type == ExtrusionSource.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, element: Element, properties: list[ExtrusionPropertyConfig], element_row: dict[str, Any]):
        for p in properties:
            if p.source.type == ExtrusionSource.SQL:
                if p.source.expression in element_row:
                    element.add_property(p.property_set, p.property, element_row[p.source.expression])
            elif p.source.type == ExtrusionSource.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, element: FeatureElement, feature_type: ExtrusionFeatureType, element_row: dict[str, Any]):
        for group_mapping in feature_type.group_mapping:
            if group_mapping.type == ExtrusionSource.SQL:
                element.add_group(element_row[group_mapping.expression])
            elif group_mapping.type == ExtrusionSource.STATIC:
                element.add_group(group_mapping.expression)
