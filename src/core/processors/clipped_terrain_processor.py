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
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, origin, model):

        clipped_terrain_config = config.ifc.clipped_terrain
        tin_config = config.tin

        wkts = []
        feature_class_elements = {}
        for feature_class_key, feature_class in clipped_terrain_config.items():
            logger.info(f"fetch {feature_class_key}")
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            elements = self.postgis_service.fetch_feature_class_elements(sql, polygon)
            feature_class_elements[feature_class_key] = elements
            for element_data in elements:
                wkts.append(element_data["wkt"])

        logger.info("calculate bounding box for fetching dtm files")
        if len(wkts) == 0:
            logger.warning("No content found for this polygon")
            bounding_box = self.postgis_service.get_bounding_box([polygon])
        else:
            bounding_box = self.postgis_service.get_bounding_box(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        for feature_class_key, feature_class in clipped_terrain_config.items():
            logger.info(f"create {feature_class_key} feature class")
            elements = feature_class_elements[feature_class_key]

            rp_buffer = {}
            rp_within = {}
            areas = {}
            for dtm_file in dtm_files:
                logger.info(f"load dtm file: {dtm_file}")
                dtm_points = RasterPoints(dtm_file, origin=origin)

                for index, element_data in enumerate(elements):
                    logger.info(f"create {feature_class_key} {index + 1}/{len(elements)}")
                    logger.debug("create area")
                    wkt_str = element_data["wkt"]
                    if isinstance(shapely.from_wkt(wkt_str), shapely.MultiPolygon):
                        logger.warning("Multipolygons are not supported at the moment. Skipping element...")
                        continue
                    areas[index] = Area(wkt_str=wkt_str, origin=origin[:2])

                    logger.debug("calculate raster points buffer")
                    raster_points_buffer = dtm_points.within(areas[index].get_geometry, buffer_dist=3 * tin_config.grid_size)
                    if index not in rp_buffer:
                        rp_buffer[index] = []
                    if raster_points_buffer is not None:
                        rp_buffer[index].append(raster_points_buffer)

                    logger.debug("calculate raster points within")
                    raster_points_within = dtm_points.within(areas[index].get_geometry, buffer_dist=0)
                    if index not in rp_within:
                        rp_within[index] = []
                    if raster_points_within is not None:
                        rp_within[index].append(raster_points_within)

            for index, element_data in enumerate(elements):
                attributes = {}
                for attribute in feature_class.attributes:
                    attributes[attribute.name] = element_data[attribute.column]

                logger.info(f"create mesh {index + 1}/{len(elements)}")

                if index in rp_buffer and rp_buffer[index]:
                    raster_points_buffer = np.vstack(rp_buffer[index])
                else:
                    raster_points_buffer = np.empty((0, 3))
                if rp_buffer[index]:
                    raster_points_within = np.vstack(rp_within[index])
                else:
                    raster_points_within = np.empty((0, 3))

                mesh = Mesh(raster_points_buffer)
                logger.debug("clip mesh")
                mesh_clipped = mesh.clip_mesh_by_area(areas[index], raster_points_within)
                logger.debug("decimate clipped mesh")
                mesh_clipped_decimated = mesh_clipped.decimate(
                    max_height_error=config.tin.max_height_error, grid_size=config.tin.grid_size
                )
                logger.info(
                    f"area consistensy: {mesh_clipped_decimated.check_area_consistency(areas[index].get_area, treshold=0.1)}"
                )
                groups = [element_data[group_column] for group_column in feature_class.group_columns]
                element = ClippedTerrain(mesh_clipped_decimated.get_data(), attributes, groups)
                for p in feature_class.properties:
                    element.add_property(p.set, p.name, element_data[p.column])
                model.add_clipped_terrain(feature_class_key, element)
