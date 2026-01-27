import logging

from core.ifc.model.extrusion.cross_section import CrossSection

logger = logging.getLogger(__name__)


class Rectangle(CrossSection):

    def __init__(self, width: float, height: float):
        super().__init__()
        self.width = width
        self.height = height