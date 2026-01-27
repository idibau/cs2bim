import logging

from shapely import wkt

from core.ifc.model.coordinates import Coordinates
from core.ifc.model.ifc_version import IfcVersion
from core.ifc.model.model import Model
from core.processors.building_processor import BuildingProcessor
from core.processors.projection_processor import ProjectionProcessor

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

        return Coordinates(min_x, min_y, 0)

    def generate(self, ifc_version: IfcVersion, name: str, polygon: str, project_origin: Coordinates | None):
        logger.info("start generating model")
        if project_origin is None:
            project_origin = self.calculate_origin_from_polygon(polygon)

        model = Model(name, ifc_version, project_origin, polygon)

        logger.info("process projection feature types")
        projection_processor = ProjectionProcessor()
        projections = projection_processor.process(polygon, project_origin)
        for key, projections in projections.items():
            model.add_projections(key, projections)

        logger.info("process building feature types")
        building_processor = BuildingProcessor()
        buildings = building_processor.process(polygon, project_origin)
        for key, buildings in buildings.items():
            model.add_buildings(key, buildings)

        return model
