import os
import sys
import logging
import numpy as np
import shapely

from cs2bim.config.configuration import config
from cs2bim.config.ifc_version import IfcVersion
from cs2bim.tin.mesh import Mesh
from cs2bim.tin.polygon import Area
from cs2bim.tin.raster import RasterPoints
from cs2bim.ifc.ifc_model import IfcModel
from cs2bim.ifc.ifc_builder import IfcBuilder
from cs2bim.ifc.entity.ifc_element import IfcElement
from cs2bim.geometry.triangulation import Triangulation
from cs2bim.service.dtm_service import DTMService
from cs2bim.service.postgis_service import PostgisService

# load configuration File
config.load("config.yml")

logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(config.logging_level)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)


swiss_topo_service = DTMService()
postgis_service = PostgisService()


def main(ifc_version: IfcVersion, name: str, polygon: str):
    wkts = []
    feature_class_elements = {}
    for feature_class_key, feature_class in config.feature_classes.items():
        logger.info(f"fetch {feature_class_key}")
        elements = postgis_service.fetch_feature_class_elements(feature_class, polygon)
        feature_class_elements[feature_class_key] = elements
        for element in elements:
            wkts.append(element["wkt"])
    
    logger.info("calculate bounding box for fetching dtm files")
    # ensures that parcels that exceed the bounding box are also included in the dtm files
    if len(wkts) == 0:
        logger.warning("No content found for this polygon")
        bounding_box = postgis_service.get_bounding_box([polygon])
    else:
        bounding_box = postgis_service.get_bounding_box(wkts)

    logger.info("fetch dtm files")
    dtm_files = swiss_topo_service.fetch_dtm_files(bounding_box)
    logger.info(f"fetched {len(dtm_files)} dtm files")

    logger.info("load raster")
    p_raster_parts = list((np.loadtxt(dtm_file, delimiter=" ", skiprows=1) for dtm_file in dtm_files))
    p_raster = np.concatenate(p_raster_parts)
    origin = p_raster.min(axis=0)
    dtm_points = RasterPoints(p_raster, origin=origin)

    model = IfcModel(name, ifc_version.value, (float(origin[0]), float(origin[1]), float(origin[2])))

    for feature_class_key, feature_class in config.feature_classes.items():
        logger.info(f"create {feature_class_key} feature class")
        elements = feature_class_elements[feature_class_key]
        for index, element in enumerate(elements):
            attributes = {}
            for attribute, column in feature_class.attributes.items():
                attributes[attribute] = element[column]
            logger.info(f"create {feature_class_key} {index + 1}/{len(elements)}")
            logger.debug("create area")
            wkt_str = element["wkt"]
            if isinstance(shapely.from_wkt(wkt_str), shapely.MultiPolygon):
                logger.warn("Multipolygons are not supported at the moment. Skipping element...")
                continue
            area = Area(wkt_str=wkt_str, origin=origin[:2])
            logger.debug("calculate raster points buffer")
            raster_points_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
            logger.debug("calculate raster points within")
            raster_points_within = dtm_points.within(area.get_geometry, buffer_dist=0)
            logger.debug("create mesh")
            mesh = Mesh(raster_points_buffer)
            logger.debug("clip mesh")
            mesh_clipped = mesh.clip_mesh_by_area(area, raster_points_within)
            logger.debug("decimate clipped mesh")
            mesh_clipped_decimated = mesh_clipped.decimate(
                max_height_error=config.max_height_error, grid_size=config.grid_size
            )
            logger.info(f"area consistensy: {mesh_clipped_decimated.check_area_consistency(area.get_area, treshold=0.1)}")
            triangulation = Triangulation()
            triangulation.load_from_data(mesh_clipped_decimated.get_data())
            groups = [element[group_column] for group_column in feature_class.group_columns]
            ifc_element = IfcElement(attributes, groups, triangulation)
            for property in feature_class.properties:
                ifc_element.add_property(property.set, property.name, element[property.column])
            model.add_ifc_element(feature_class_key, ifc_element)

    ifc_builder = IfcBuilder()
    ifc_file = ifc_builder.build(model)

    ifc_file.write(f"output/{name}.ifc")


if __name__ == "__main__":
    MANDATORY_ENV_VARS = ["IFC_VERSION", "NAME", "POLYGON"]
    for var in MANDATORY_ENV_VARS:
        if var not in os.environ:
            raise EnvironmentError(f"Failed because {var} is not set.")
    ifc_version = IfcVersion[os.environ["IFC_VERSION"]]
    name = os.environ["NAME"]
    polygon = os.environ["POLYGON"]
    logger.info(f"IFC_VERSION: {ifc_version.name}, NAME: {name}, POLYGON: {polygon}")
    main(ifc_version, name, polygon)
