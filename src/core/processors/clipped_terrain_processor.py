import logging

import numpy as np
import shapely

from config.configuration import config
from core.ifc.model.clipped_terrain import ClippedTerrain
from core.tin.mesh import Mesh
from core.tin.polygon import Area
from core.tin.raster import RasterPoints
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class ClippedTerrainProcessor:

    def __init__(self):
        self.feature_classes = config.ifc.clipped_terrain
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, origin, model):
        if not self.feature_classes:
            logger.info("no clipped terrain feature classes configured")
            return

        wkts = []
        feature_class_elements = {}
        for feature_class_key, feature_class in self.feature_classes.items():
            logger.info(f"fetch {feature_class_key}")
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            elements = self.postgis_service.fetch_feature_class_elements(sql, polygon)
            feature_class_elements[feature_class_key] = elements
            for element_data in elements:
                wkts.append(element_data["wkt"])

        logger.info("calculate bounding box for fetching dtm files")
        if len(wkts) == 0:
            logger.warning("no content found for this polygon")
            bounding_box = self.postgis_service.get_bounding_box([polygon])
        else:
            bounding_box = self.postgis_service.get_bounding_box(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box, config.tin.grid_size)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        for feature_class_key, feature_class in self.feature_classes.items():
            logger.info(f"create {feature_class_key} feature class")
            elements = feature_class_elements[feature_class_key]

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

            logger.info(f"create meshes for {feature_class_key} elements")
            for index, mesh_data in enumerate(mesh_datas):
                logger.debug(f"create mesh for element {index + 1}/{len(elements)}")
                mesh = mesh_data.create_mesh()
                groups = [mesh_data.element_data[group_column] for group_column in feature_class.group_columns]
                element = ClippedTerrain(mesh.get_data(), groups)
                for attribute in feature_class.attributes:
                    if attribute.column in mesh_data.element_data:
                        element.add_attribute(attribute.name, mesh_data.element_data[attribute.column])
                for p in feature_class.properties:
                    if p.column in mesh_data.element_data:
                        element.add_property(p.set, p.name, mesh_data.element_data[p.column])
                model.add_clipped_terrain(feature_class_key, element)
            logger.info("finished creating meshes")

class MeshData:

    def __init__(self, element_data, origin):
        self.element_data = element_data
        self.area = Area(wkt_str=element_data["wkt"], origin=origin[:2])
        self.raster_points_within = []
        self.raster_points_buffer = []

    def add_raster_points(self, raster_points):
        rpb = raster_points.within(self.area.get_geometry, buffer_dist=3 * config.tin.grid_size)
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
            max_height_error=config.tin.max_height_error, grid_size=config.tin.grid_size
        )
        logger.debug(
            f"area consistency: {mesh_clipped_decimated.check_area_consistency(self.area.get_area, treshold=0.1)}"
        )
        return mesh_clipped_decimated
