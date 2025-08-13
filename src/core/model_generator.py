import logging

import shapely

from config.configuration import config
from core.ifc.enum.ifc_version import IfcVersion
from core.ifc.geometry.triangulation import Triangulation
from core.ifc.ifc_builder import IfcBuilder
from core.ifc.model.element import Element
from core.ifc.model.model import Model
from core.tin.mesh import Mesh
from core.tin.polygon import Area
from core.tin.raster import RasterPoints
from service.dtm_service import DTMService
from service.postgis_service import PostgisService

logger = logging.getLogger(__name__)

import numpy as np
from shapely import wkt


class ModelGenerator:

    def __init__(self):
        self.ifc_builder = IfcBuilder(
            config.ifc.author,
            config.ifc.version,
            config.ifc.application_name,
            config.ifc.project_name,
            config.ifc.geo_referencing,
            config.ifc.triangulation_representation_type,
            config.ifc.feature_classes,
            config.ifc.groups,
        )
        self.postgis_service = PostgisService()
        self.dmt_service = DTMService()

    def first_coord(self, wkt_polygon: str) -> np.ndarray:
        geo = wkt.loads(wkt_polygon)
        first_coord = geo.exterior.coords[0]
        first_coord += (0,)
        return first_coord

    def generate(self, ifc_version: IfcVersion, name: str, polygon: str,
                 project_origin: tuple[float, float, float] | None):
        wkts = []
        feature_class_elements = {}
        for feature_class_key, feature_class in config.ifc.feature_classes.items():
            logger.info(f"fetch {feature_class_key}")
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            elements = self.postgis_service.fetch_feature_class_elements(sql, polygon)
            feature_class_elements[feature_class_key] = elements
            for element_data in elements:
                wkts.append(element_data["wkt"])

        logger.info("load raster")
        if project_origin is None:
            project_origin = self.first_coord(polygon)

        origin = np.array(project_origin)
        model = Model(name, ifc_version, project_origin)

        for feature_class_key, feature_class in config.ifc.feature_classes.items():
            logger.info(f"create {feature_class_key} feature class")
            elements = feature_class_elements[feature_class_key]
            for index, element_data in enumerate(elements):
                attributes = {}
                for attribute in feature_class.attributes:
                    attributes[attribute.name] = element_data[attribute.column]
                logger.info(f"create {feature_class_key} {index + 1}/{len(elements)}")
                logger.debug("create area")
                wkt_str = element_data["wkt"]
                if isinstance(shapely.from_wkt(wkt_str), shapely.MultiPolygon):
                    logger.warning("Multipolygons are not supported at the moment. Skipping element...")
                    continue
                area = Area(wkt_str=wkt_str, origin=origin[:2])

                bounding_box = self.postgis_service.get_bounding_box([wkt_str])

                dtm_files = self.dmt_service.fetch_dtm_files(bounding_box)
                dtm_points = RasterPoints(dtm_files, origin=origin)

                logger.debug("calculate raster points buffer")
                raster_points_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.tin.grid_size)
                logger.debug("calculate raster points within")
                raster_points_within = dtm_points.within(area.get_geometry, buffer_dist=0)
                logger.debug("create mesh")
                mesh = Mesh(raster_points_buffer)
                logger.debug("clip mesh")
                mesh_clipped = mesh.clip_mesh_by_area(area, raster_points_within)
                logger.debug("decimate clipped mesh")
                mesh_clipped_decimated = mesh_clipped.decimate(
                    max_height_error=config.tin.max_height_error, grid_size=config.tin.grid_size
                )
                logger.info(
                    f"area consistensy: {mesh_clipped_decimated.check_area_consistency(area.get_area, treshold=0.1)}"
                )
                triangulation = Triangulation()
                triangulation.load_from_points_and_faces(mesh_clipped_decimated.get_data())
                groups = [element_data[group_column] for group_column in feature_class.group_columns]
                element = Element(attributes, groups, triangulation)
                for property in feature_class.properties:
                    element.add_property(property.set, property.name, element_data[property.column])
                model.add_element(feature_class_key, element)

        ifc_file = self.ifc_builder.build(model)
        return ifc_file
