import logging
from typing import Any

from config.configuration import config, ProjectionFeatureType, ProjectionAttributeConfig, ProjectionPropertyConfig
from config.projection_source import ProjectionSource
from core.ifc.model.coordinates import Coordinates
from core.ifc.model.element import Element
from core.ifc.model.projection import Projection
from core.processors.projection_data import ProjectionData
from core.tin.raster_points import RasterPoints
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class ProjectionProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon: str, project_origin: Coordinates) -> dict[str, list[Projection]]:
        feature_types_by_key = {p.name: p for p in config.ifc.projection_feature_types}
        if not feature_types_by_key:
            logger.info("no projection feature types configured")
            return {}

        wkts = []
        sql_results_by_feature_type = {}
        for feature_type_key, feature_type in feature_types_by_key.items():
            logger.info(f"fetch {feature_type_key}")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            sql_result = self.postgis_service.fetch_feature_type_elements(sql, polygon)
            sql_results_by_feature_type[feature_type_key] = sql_result
            for row in sql_result:
                wkts.append(row["wkt"])

        logger.info("calculate bounding box for fetching dtm files")
        if len(wkts) == 0:
            logger.warning("no content found for this polygon")
            bounding_box = self.postgis_service.get_bounding_box([polygon])
        else:
            bounding_box = self.postgis_service.get_bounding_box(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box, config.tin.grid_size.value)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        projections_by_key = {}
        for feature_type_key, feature_type in feature_types_by_key.items():
            logger.info(f"create {feature_type_key} feature type")
            sql_result = sql_results_by_feature_type[feature_type_key]

            projection_data = []
            for element_row in sql_result:
                try:
                    projection_element_data = ProjectionData(element_row, project_origin)
                    projection_data.append(projection_element_data)
                except Exception as e:
                    logger.error(f"error in element data: {e}. Skipping element...")

            for dtm_file in dtm_files:
                logger.info(f"load and process dtm file: {dtm_file}")
                dtm_points = RasterPoints(dtm_file, project_origin)
                for index, projection_element_data in enumerate(projection_data):
                    logger.debug(f"calculate raster points for element {index + 1}/{len(sql_result)}")
                    projection_element_data.add_raster_points(dtm_points)
            logger.info(f"finished processing dtm files")

            logger.info(f"create meshes for {feature_type_key} elements")
            for index, projection_element_data in enumerate(projection_data):
                logger.debug(f"create mesh for element {index + 1}/{len(sql_result)}")
                projection = self.create_projection(feature_type, projection_element_data)

                if not feature_type_key in projections_by_key:
                    projections_by_key[feature_type_key] = []
                projections_by_key[feature_type_key].append(projection)
            logger.info("finished creating meshes")
        return projections_by_key

    def create_projection(self, feature_type: ProjectionFeatureType, projection_data: ProjectionData) -> Projection:
        projection = Projection(projection_data.create_mesh_data())
        self.add_attributes(projection, feature_type.entity_mapping.attributes, projection_data.element_row)
        self.add_properties(projection, feature_type.entity_mapping.properties, projection_data.element_row)
        self.add_groups(projection, feature_type, projection_data.element_row)
        spatial_structure = Element()
        self.add_attributes(spatial_structure, feature_type.spatial_structure_mapping.attributes,
                            projection_data.element_row)
        self.add_properties(spatial_structure, feature_type.spatial_structure_mapping.properties,
                            projection_data.element_row)
        projection.spatial_structure = spatial_structure
        if feature_type.entity_type_mapping is not None:
            projection_element_type = Element()
            self.add_attributes(projection_element_type, feature_type.entity_type_mapping.attributes,
                                projection_data.element_row)
            self.add_properties(projection_element_type, feature_type.entity_type_mapping.properties,
                                projection_data.element_row)
            projection.element_type = projection_element_type
        return projection

    def add_attributes(self, element: Element, attributes: list[ProjectionAttributeConfig],
                       element_row: dict[str, Any]):
        for attribute in attributes:
            if attribute.source.type == ProjectionSource.SQL:
                if attribute.source.expression in element_row:
                    element.add_attribute(attribute.attribute, element_row[attribute.source.expression])
            elif attribute.source.type == ProjectionSource.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, element: Element, properties: list[ProjectionPropertyConfig], element_row: dict[str, Any]):
        for p in properties:
            if p.source.type == ProjectionSource.SQL:
                if p.source.expression in element_row:
                    element.add_property(p.property_set, p.property, element_row[p.source.expression])
            elif p.source.type == ProjectionSource.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, element: Projection, feature_type: ProjectionFeatureType, element_row: dict[str, Any]):
        for group_mapping in feature_type.group_mapping:
            if group_mapping.type == ProjectionSource.SQL:
                element.add_group(element_row[group_mapping.expression])
            elif group_mapping.type == ProjectionSource.STATIC:
                element.add_group(group_mapping.expression)
