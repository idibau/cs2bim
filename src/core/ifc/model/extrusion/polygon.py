import logging

from shapely import Point
from shapely.geometry.base import BaseGeometry

from core.ifc.model.extrusion.cross_section import CrossSection

logger = logging.getLogger(__name__)


class Polygon(CrossSection):

    def __init__(self, polygon: BaseGeometry):
        super().__init__()
        self.points = [Point(x, y) for x, y in polygon.exterior.coords]
