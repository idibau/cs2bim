import os
import sys
import logging
import numpy as np
from wkt2tin.polygon import Area
from wkt2tin.raster import RasterPoints
from wkt2tin.mesh import Mesh
from tin2ifc.model.ifc_model import IfcModel
from tin2ifc.model.entitiy.element import Element
from tin2ifc.model.geometry.triangulation import Triangulation
from tin2ifc.build.ifc_builder import IfcBuilder

from cs2bim.configuration import config
from cs2bim.enum.ifc_version import IfcVersion
from cs2bim.service.swisstopo_service import SwisstopoService
from cs2bim.service.postgis_service import PostgisService


logging_format = "%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s"
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(logging_format))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)

logger = logging.getLogger(__name__)

# load configuration File
config.load("config.yml")

swiss_topo_service = SwisstopoService()
postgis_service = PostgisService()


def main(ifc_version: IfcVersion, name: str, polygon: str):
    logger.info("fetch parcels")
    parcels = postgis_service.fetch_parcels(polygon)

    logger.info("fetch landcovers (building)")
    land_covers = postgis_service.fetch_building_land_cover(polygon)

    logger.info("calculate bounding box for fetching dtm files")
    # ensures that parcels that exceed the bounding box are also included in the dtm files
    wkts = []
    for parcel in parcels:
        wkts.append(parcel.wkt)
    for land_cover in land_covers:
        wkts.append(land_cover.wkt)

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

    model = IfcModel(name, ifc_version.value, (float(origin[0]), float(origin[1]), float(origin[2])))

    logger.info("create parcel feature class")
    feature_class = config.feature_classes["parcel"]
    for index, parcel in enumerate(parcels):
        logger.info(f"create parcel {parcel.egris_egrid} ({index + 1}/{len(parcels)})")
        area = Area(wkt_str=parcel.wkt, origin=origin[:2])
        dtm_points = RasterPoints(p_raster, origin=origin)
        raster_points_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
        raster_points_within = dtm_points.within(area.get_geometry, buffer_dist=0)
        mesh = Mesh(raster_points_buffer)
        mesh_clipped = mesh.clip_mesh_by_area(area, raster_points_within)
        mesh_clipped_decimated = mesh_clipped.decimate(
            max_height_error=config.max_height_error, grid_size=config.grid_size
        )
        logger.debug(f"area consistensy: {mesh_clipped_decimated.check_area_consistency(area.get_area, treshold=0.1)}")
        triangulation = Triangulation()
        triangulation.load_from_data(mesh_clipped_decimated.get_data())
        element = Element(parcel.egris_egrid, "", triangulation)
        element.add_property("CHKGK_CS", "NBIdent", parcel.nbident)
        element.add_property("CHKGK_CS", "Nummer", parcel.nummer)
        element.add_property("CHKGK_CS", "EGRIS_EGRID", parcel.egris_egrid)
        model.add_element(feature_class.key, element)

    logger.info("create land cover (building) feature class")
    feature_class = config.feature_classes["land_cover"]
    for index, land_cover in enumerate(land_covers):
        logger.info(f"create land cover ({index + 1}/{len(land_covers)})")
        area = Area(wkt_str=land_cover.wkt, origin=origin[:2])
        dtm_points = RasterPoints(p_raster, origin=origin)
        raster_points_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
        raster_points_within = dtm_points.within(area.get_geometry, buffer_dist=0)
        mesh = Mesh(raster_points_buffer)
        mesh_clipped = mesh.clip_mesh_by_area(area, raster_points_within)
        mesh_clipped_decimated = mesh_clipped.decimate(
            max_height_error=config.max_height_error, grid_size=config.grid_size
        )
        logger.debug(f"area consistensy: {mesh_clipped_decimated.check_area_consistency(area.get_area, treshold=0.1)}")
        triangulation = Triangulation()
        triangulation.load_from_data(mesh_clipped_decimated.get_data())
        element = Element("", "", triangulation)
        model.add_element(feature_class.key, element)

    ifc_builder = IfcBuilder(
        config.author,
        config.version,
        config.application_name,
        config.project_name,
        config.geo_referencing,
        config.triangulation_representation_type,
        config.feature_classes,
    )
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
