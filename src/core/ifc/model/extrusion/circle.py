import logging

from core.ifc.model.extrusion.cross_section import CrossSection

logger = logging.getLogger(__name__)


class Circle(CrossSection):

    def __init__(self, radius: float):
        self.radius = radius