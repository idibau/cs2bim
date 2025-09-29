import logging

import numpy as np

from config.configuration import config
from config.projection_source_type import ProjectionSourceType
from core.ifc.model.projection import Projection
from core.tin.mesh import Mesh
from core.tin.polygon import Area
from core.tin.raster import RasterPoints
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class ProjectionProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, origin):
        feature_types = {ct.name: ct for ct in config.ifc.feature_types.projections}
        if not feature_types:
            logger.info("no clipped terrain feature typees configured")
            return {}

        wkts = []
        feature_type_elements = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"fetch {feature_type_key}")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            elements = self.postgis_service.fetch_feature_type_elements(sql, polygon)
            feature_type_elements[feature_type_key] = elements
            for element_data in elements:
                wkts.append(element_data["wkt"])

        logger.info("calculate bounding box for fetching dtm files")
        if len(wkts) == 0:
            logger.warning("no content found for this polygon")
            bounding_box = self.postgis_service.get_bounding_box([polygon])
        else:
            bounding_box = self.postgis_service.get_bounding_box(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box, config.tin.grid_size.value)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        projections = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"create {feature_type_key} feature type")
            elements = feature_type_elements[feature_type_key]

            mesh_datas = []
            for element_data in elements:
                try:
                    mesh_data = MeshData(element_data, origin)
                    mesh_datas.append(mesh_data)
                except Exception as e:
                    logger.error(f"Error in element data: {e}. Skipping element...")

            for dtm_file in dtm_files:
                logger.info(f"load and process dtm file: {dtm_file}")
                dtm_points = RasterPoints(dtm_file, origin=origin)
                for index, mesh_data in enumerate(mesh_datas):
                    logger.debug(f"calculate raster points for element {index + 1}/{len(elements)}")
                    mesh_data.add_raster_points(dtm_points)
            logger.info(f"finished processing dtm files")

            logger.info(f"create meshes for {feature_type_key} elements")
            for index, mesh_data in enumerate(mesh_datas):
                logger.debug(f"create mesh for element {index + 1}/{len(elements)}")
                mesh = mesh_data.create_mesh()
                element = Projection(mesh.get_data())
                for attribute in feature_type.entity_mapping.attributes:
                    if attribute.source.type == ProjectionSourceType.SQL:
                        if attribute.source.expression in mesh_data.element_data:
                            element.add_attribute(attribute.attribute, mesh_data.element_data[attribute.source.expression])
                    elif attribute.source.type == ProjectionSourceType.STATIC:
                        element.add_attribute(attribute.attribute, attribute.source.expression)
                for p in feature_type.entity_mapping.properties:
                    if p.source.type == ProjectionSourceType.SQL:
                        if p.source.expression in mesh_data.element_data:
                            element.add_property(p.property_set, p.property, mesh_data.element_data[p.source.expression])
                    elif p.source.type == ProjectionSourceType.STATIC:
                        element.add_property(p.property_set, p.property, p.source.expression)
                for group_mapping in feature_type.group_mapping:
                    if group_mapping.type == ProjectionSourceType.SQL:
                        element.add_group(mesh_data.element_data[group_mapping.expression])
                    elif group_mapping.type == ProjectionSourceType.STATIC:
                        element.add_group(group_mapping.expression)

                if not feature_type_key in projections:
                    projections[feature_type_key] = []
                projections[feature_type_key].append(element)
            logger.info("finished creating meshes")
        return projections

class MeshData:

    def __init__(self, element_data, origin):
        self.element_data = element_data
        self.area = Area(wkt_str=element_data["wkt"], origin=origin[:2])
        self.raster_points_within = []
        self.raster_points_buffer = []

    def add_raster_points(self, raster_points):
        rpb = raster_points.within(self.area.get_geometry, buffer_dist=3 * config.tin.grid_size.value)
        if rpb is not None:
            self.raster_points_buffer.append(rpb)
        rpw = raster_points.within(self.area.get_geometry, buffer_dist=0)
        if rpw is not None:
            self.raster_points_within.append(rpw)

    def create_mesh(self):
        if self.raster_points_buffer:
            mesh = Mesh(np.vstack(self.raster_points_buffer))
        else:
            mesh = Mesh(np.empty((0, 3)))
        if self.raster_points_within:
            mesh_clipped = mesh.clip_mesh_by_area(self.area, np.vstack(self.raster_points_within))
        else:
            mesh_clipped = mesh.clip_mesh_by_area(self.area, np.empty((0, 3)))
        mesh_clipped_decimated = mesh_clipped.decimate(
            max_height_error=config.tin.max_height_error, grid_size=config.tin.grid_size.value
        )
        logger.debug(
            f"area consistency: {mesh_clipped_decimated.check_area_consistency(self.area.get_area, treshold=0.1)}"
        )
        return mesh_clipped_decimated
