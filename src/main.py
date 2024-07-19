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

from configuration import config
from service.swisstopo_service import SwisstopoService
from service.postgis_service import PostgisService


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


def main(ifc_version: str, name: str, polygon: str):
    dtm_file = swiss_topo_service.fetch_dtm_file("")
    p_raster = np.loadtxt(dtm_file, delimiter=" ", skiprows=1)
    origin = p_raster.min(axis=0)

    # create model object
    model = IfcModel(name, ifc_version, (float(origin[0]), float(origin[1]), float(origin[2])))

    # add elements for "PARCEL" feature class
    feature_class = config.feature_classes["parcel"]
    parcels = postgis_service.fetch_parcels(polygon)
    for parcel in parcels:
        area = Area(wkt_str=parcel.wkt, origin=origin[:2])
        dtm_points = RasterPoints(p_raster, origin=origin)
        subset_P_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
        mesh = Mesh(subset_P_buffer)
        mesh_clipped = mesh.clip_mesh_by_area(area)
        mesh_clipped_decimated = mesh_clipped.decimate(
            max_height_error=config.max_height_error, grid_size=config.grid_size
        )
        triangulation = Triangulation()
        triangulation.load_from_data(mesh_clipped_decimated.get_data())
        element = Element("-", "-", triangulation)
        element.add_property("CHKGK_CS", "NBIdent", parcel.nbident)
        element.add_property("CHKGK_CS", "Nummer", parcel.nummer)
        element.add_property("CHKGK_CS", "EGRIS_EGRID", parcel.egris_egrid)
        model.add_element(feature_class.key, element)

    # add elements for "BODEN" feature class
    feature_class = config.feature_classes["land_cover"]
    land_covers = postgis_service.fetch_land_cover(polygon)
    for land_cover in land_covers:
        area = Area(wkt_str=land_cover.wkt, origin=origin[:2])
        dtm_points = RasterPoints(p_raster, origin=origin)
        subset_P_buffer = dtm_points.within(area.get_geometry, buffer_dist=3 * config.grid_size)
        mesh = Mesh(subset_P_buffer)
        mesh_clipped = mesh.clip_mesh_by_area(area)
        mesh_clipped_decimated = mesh_clipped.decimate(
            max_height_error=config.max_height_error, grid_size=config.grid_size
        )
        triangulation = Triangulation()
        triangulation.load_from_data(mesh_clipped_decimated.get_data())
        element = Element("-", "-", triangulation)
        model.add_element(feature_class.key, element)

    # build ifc object
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

    # write ifc file
    ifc_file.write("files/test5.ifc")


if __name__ == "__main__":
    ifc_version = "IFC4"
    name = "Test"
    polygon = "POLYGON ((2689625.65 1283556.46, 2689594.44 1283614.38, 2689527.96 1283597.71, 2689625.65 1283556.46))"

    main(ifc_version, name, polygon)
