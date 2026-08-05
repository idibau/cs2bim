import logging
import math
import numpy as np
import shapely
from shapely import wkt, Point
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry
from typing import Any

from config.configuration import config, ProjectionFeatureType, ProjectionAttributeConfig, ProjectionPropertyConfig
from config.projection_source import ProjectionSource
from core.ifc.model.element import Element
from core.ifc.model.projection.projection import Projection
from core.tin.area import Area
from core.tin.raster_points import RasterPoints
from service.bounding_box import BoundingBox
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class ProjectionProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon: str, project_origin: Point, feature_types: list[str]) -> dict[str, list[Projection]]:
        feature_types_by_key = {ft.name: ft for ft in config.ifc.projection_feature_types if
                                not feature_types or ft.name in feature_types}
        if not feature_types_by_key:
            logger.info("no projection feature types configured or selected")
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
            bounding_box = BoundingBox.from_wkts([polygon])
        else:
            bounding_box = BoundingBox.from_wkts(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box, config.tin.grid_size.value)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        projections_by_key = {}
        for feature_type_key, feature_type in feature_types_by_key.items():
            logger.info(f"create {feature_type_key} feature type")
            sql_result = sql_results_by_feature_type[feature_type_key]

            elements = []
            for element_row in sql_result:
                try:
                    areas = self._build_areas(element_row)
                    elements.append((element_row, areas))
                except Exception as e:
                    logger.error(f"error in element data: {e}. Skipping element...")

            for dtm_file in dtm_files:
                logger.info(f"load and process dtm file: {dtm_file}")
                dtm_points = RasterPoints(dtm_file)
                for index, (_, areas) in enumerate(elements):
                    logger.debug(f"calculate raster points for element {index + 1}/{len(sql_result)}")
                    for area in areas:
                        area.add_raster_points(dtm_points)
            logger.info(f"finished processing dtm files")

            logger.info(f"create meshes for {feature_type_key} elements")
            for index, (element_row, areas) in enumerate(elements):
                logger.debug(f"create mesh for element {index + 1}/{len(sql_result)}")
                mesh_data = self._create_mesh_data(areas, project_origin)
                projection = self.create_projection(feature_type, element_row, mesh_data)

                if feature_type_key not in projections_by_key:
                    projections_by_key[feature_type_key] = []
                projections_by_key[feature_type_key].append(projection)
            logger.info("finished creating meshes")
        return projections_by_key

    def create_projection(self, feature_type: ProjectionFeatureType, element_row: dict[str, Any],
                          mesh_data: tuple[list, list]) -> Projection:
        projection = Projection(mesh_data)
        self.add_attributes(projection, feature_type.entity_mapping.attributes, element_row)
        self.add_properties(projection, feature_type.entity_mapping.properties, element_row)
        self.add_groups(projection, feature_type, element_row)
        spatial_structure = Element()
        self.add_attributes(spatial_structure, feature_type.spatial_structure_mapping.attributes, element_row)
        self.add_properties(spatial_structure, feature_type.spatial_structure_mapping.properties, element_row)
        projection.spatial_structure = spatial_structure
        if feature_type.entity_type_mapping is not None:
            projection_element_type = Element()
            self.add_attributes(projection_element_type, feature_type.entity_type_mapping.attributes, element_row)
            self.add_properties(projection_element_type, feature_type.entity_type_mapping.properties, element_row)
            projection.element_type = projection_element_type
        return projection

    def _create_mesh_data(self, areas: list[Area], project_origin: Point) -> tuple[list, list]:
        points_total = []
        point_to_index = {}
        indices_total = []

        for area in areas:
            points, faces = area.create_mesh()
            if len(points) == 0 or len(faces) == 0:
                logger.warning("No points or faces found for area %s", area.polygon)
                continue
            points = points - np.array([project_origin.x, project_origin.y, project_origin.z])

            for face in faces:
                new_face = []
                for local_idx in face:
                    p = tuple(points[local_idx])
                    if p not in point_to_index:
                        point_to_index[p] = len(points_total)
                        points_total.append(p)
                    new_face.append(point_to_index[p])
                indices_total.append(tuple(new_face))

        return points_total, indices_total

    def _cut_polygon_if_large(self, poly: shapely.Polygon, max_size_m: int = 1000) -> list[BaseGeometry]:
        minx, miny, maxx, maxy = poly.bounds
        width = maxx - minx
        height = maxy - miny

        if width <= max_size_m and height <= max_size_m:
            return [poly]

        nx = math.ceil(width / max_size_m)
        ny = math.ceil(height / max_size_m)

        cut_polys = []
        for i in range(nx):
            for j in range(ny):
                x1 = minx + i * max_size_m
                y1 = miny + j * max_size_m
                x2 = min(x1 + max_size_m, maxx)
                y2 = min(y1 + max_size_m, maxy)
                cell = box(x1, y1, x2, y2)
                inter = poly.intersection(cell)
                if inter.is_empty:
                    continue
                if inter.geom_type == "Polygon":
                    cut_polys.append(inter)
                elif inter.geom_type == "MultiPolygon":
                    cut_polys.extend(list(inter.geoms))
                else:
                    logger.debug(f"Skipping degenerate intersection geometry: {inter.geom_type}")

        return cut_polys

    def _build_areas(self, element_row: dict[str, Any]) -> list[Area]:
        polygon = wkt.loads(element_row["wkt"])
        areas = []
        if polygon.geom_type == "Polygon":
            for cut_polygon in self._cut_polygon_if_large(polygon):
                areas.append(Area(cut_polygon))
        elif polygon.geom_type == "MultiPolygon":
            for sub_polygon in polygon.geoms:
                for cut_polygon in self._cut_polygon_if_large(sub_polygon):
                    areas.append(Area(cut_polygon))
        else:
            logger.debug(f"Skipping unsupported geometry: {polygon.geom_type}")
        return areas

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
