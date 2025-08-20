import logging

from config.configuration import config
from core.ifc.ifc_builder import IfcBuilder
from core.ifc.model.ifc_version import IfcVersion
from core.ifc.model.model import Model
from core.processors.building_processor import BuildingProcessor
from core.processors.clipped_terrain_processor import ClippedTerrainProcessor
from service.stac_service import STACService
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
            config.ifc.clipped_terrain,
            config.ifc.building,
            config.ifc.groups,
        )
        self.postgis_service = PostgisService()
        self.dmt_service = STACService()

    def first_coord(self, wkt_polygon: str) -> np.ndarray:
        geo = wkt.loads(wkt_polygon)
        first_coord = geo.exterior.coords[0]
        first_coord += (0,)
        return first_coord

    def generate(self, ifc_version: IfcVersion, name: str, polygon: str,
                 project_origin: tuple[float, float, float] | None):

        logger.info("load raster")
        if project_origin is None:
            project_origin = self.first_coord(polygon)

        origin = np.array(project_origin)
        model = Model(name, ifc_version, project_origin)

        clipped_terrain_processor =  ClippedTerrainProcessor()
        clipped_terrain_processor.process(polygon, origin, model)

        building_processor = BuildingProcessor()
        building_processor.process(polygon, origin, model)

        ifc_file = self.ifc_builder.build(model)
        return ifc_file
