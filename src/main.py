import os
import sys
import logging
import tracemalloc
import shapely
from datetime import datetime

from config.configuration import config
from cs2bim.tin.mesh import Mesh
from cs2bim.tin.polygon import Area
from cs2bim.tin.raster import RasterPoints
from cs2bim.ifc.enum.ifc_version import IfcVersion
from cs2bim.ifc.ifc_builder import IfcBuilder
from cs2bim.ifc.model.model import Model
from cs2bim.ifc.model.element import Element
from cs2bim.ifc.geometry.triangulation import Triangulation
from service.dtm_service import DTMService
from service.postgis_service import PostgisService

# load configuration File
config.load("config.yml")

logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))
log_file_name = datetime.now().strftime("%Y-%m-%d--%H-%M-%S.log")
file_handler = logging.FileHandler(f"output/{log_file_name}")
file_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(config.logging_level)
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

dmt_service = DTMService()
postgis_service = PostgisService()

import numpy as np
from shapely import wkt


def first_coord(wkt_polygon: str) -> np.ndarray:
    """
    Extrahiert die erste Koordinate eines WKT-Polygons als NumPy-Array [x, y].

    Parameter:
        wkt_polygon (str): Das Polygon im WKT-Format.

    Rückgabe:
        np.ndarray: Die erste Koordinate als Array [x, y].
    """
    geo = wkt.loads(wkt_polygon)
    first_coord = geo.exterior.coords[0]
    first_coord += (0,)
    return first_coord


def main(ifc_version: IfcVersion, name: str, polygon: str, project_origin: tuple[float, float, float] | None):
    wkts = []
    feature_class_elements = {}
    for feature_class_key, feature_class in config.feature_classes.items():
        logger.info(f"fetch {feature_class_key}")
        elements = postgis_service.fetch_feature_class_elements(feature_class.sql, polygon)
        feature_class_elements[feature_class_key] = elements
        for element_data in elements:
            wkts.append(element_data["wkt"])

    log_memory_usage()
    logger.info("load raster")
    if project_origin is None:
        project_origin = first_coord(polygon)

    origin = np.array(project_origin)
    log_memory_usage()
    model = Model(name, ifc_version, project_origin)

    for feature_class_key, feature_class in config.feature_classes.items():
        logger.info(f"create {feature_class_key} feature class")
        elements = feature_class_elements[feature_class_key]
        for index, element_data in enumerate(elements):
            attributes = {}
            for attribute, column in feature_class.attributes.items():
                attributes[attribute] = element_data[column]
            logger.info(f"create {feature_class_key} {index + 1}/{len(elements)}")
            logger.debug("create area")
            wkt_str = element_data["wkt"]
            if isinstance(shapely.from_wkt(wkt_str), shapely.MultiPolygon):
                logger.warn("Multipolygons are not supported at the moment. Skipping element...")
                continue
            area = Area(wkt_str=wkt_str, origin=origin[:2])

            bounding_box = postgis_service.get_bounding_box([wkt_str])
            dtm_files = dmt_service.fetch_dtm_files(bounding_box)
            dtm_points = RasterPoints(dtm_files, origin=origin)

            logger.debug("calculate raster points buffer")
            raster_points_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
            logger.debug("calculate raster points within")
            raster_points_within = dtm_points.within(area.get_geometry, buffer_dist=0)
            logger.debug("create mesh")
            mesh = Mesh(raster_points_buffer)
            logger.debug("clip mesh")
            mesh_clipped = mesh.clip_mesh_by_area(area, raster_points_within)
            logger.debug("decimate clipped mesh")
            log_memory_usage()
            mesh_clipped_decimated = mesh_clipped.decimate(
                max_height_error=config.max_height_error, grid_size=config.grid_size
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

    ifc_builder = IfcBuilder(
        config.author,
        config.version,
        config.application_name,
        config.project_name,
        config.geo_referencing,
        config.triangulation_representation_type,
        config.feature_classes,
        config.groups,
    )
    ifc_file = ifc_builder.build(model)

    ifc_file.write(f"output/{name}.ifc")


def log_memory_usage() -> None:
    logger.debug(
        f"Current Memory usage: {tracemalloc.get_traced_memory()[0] / 1000000}mb, Peak memory usage: {tracemalloc.get_traced_memory()[1] / 1000000}mb"
    )


if __name__ == "__main__":
    tracemalloc.start()
    MANDATORY_ENV_VARS = ["IFC_VERSION", "NAME", "POLYGON"]
    for var in MANDATORY_ENV_VARS:
        if var not in os.environ:
            raise EnvironmentError(f"Failed because {var} is not set.")
    ifc_version = IfcVersion[os.environ["IFC_VERSION"]]
    name = os.environ["NAME"]
    polygon = os.environ["POLYGON"]
    if "PROJECT_ORIGIN" in os.environ:
        try:
            string_values = os.environ["PROJECT_ORIGIN"].split(",")
            project_origin = (float(string_values[0]), float(string_values[1]), float(string_values[2]))
        except:
            raise EnvironmentError(f"PROJECT_ORIGIN need to be of format float,float,float")
    else:
        project_origin = None
    logger.info(
        f"IFC_VERSION: {ifc_version.name}, NAME: {name}, POLYGON: {polygon}, PROJECT_ORIGIN: {project_origin if not project_origin is None else 'calculated'}"
    )
    main(ifc_version, name, polygon, project_origin)
    log_memory_usage()
    tracemalloc.stop()
