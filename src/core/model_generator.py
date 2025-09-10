import logging

import numpy as np
from shapely import wkt

from core.ifc.model.ifc_version import IfcVersion
from core.ifc.model.model import Model
from core.processors.building_processor import BuildingProcessor
from core.processors.clipped_terrain_processor import ClippedTerrainProcessor

logger = logging.getLogger(__name__)


class ModelGenerator:

    def __init__(self):
        pass

    @staticmethod
    def calculate_origin_from_polygon(wkt_polygon: str):
        geo = wkt.loads(wkt_polygon)
        coords = geo.exterior.coords

        min_x = min(x for x, y in coords)
        min_y = min(y for x, y in coords)

        return min_x, min_y, 0

    def generate(self, ifc_version: IfcVersion, name: str, polygon: str,
                 project_origin: tuple[float, float, float] | None):
        logger.info("start generating model")
        if project_origin is None:
            project_origin = self.calculate_origin_from_polygon(polygon)

        origin = np.array(project_origin)
        model = Model(name, ifc_version, project_origin)

        logger.info("process clipped terrain feature classes")
        clipped_terrain_processor = ClippedTerrainProcessor()
        clipped_terrains = clipped_terrain_processor.process(polygon, origin)
        for key, clipped_terrains in clipped_terrains.items():
            model.add_clipped_terrains(key, clipped_terrains)

        logger.info("process building feature classes")
        building_processor = BuildingProcessor()
        buildings = building_processor.process(polygon, origin)
        for key, buildings in buildings.items():
            model.add_buildings(key, buildings)

        return model
