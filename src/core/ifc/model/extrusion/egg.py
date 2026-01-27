import math
import logging

from shapely import Point

from core.ifc.model.extrusion.cross_section import CrossSection

logger = logging.getLogger(__name__)


class Egg(CrossSection):
    def __init__(self, width: float, num_points: int = 12):
        if width <= 0: raise ValueError("Width must be a positive number.")

        self.W, self.H = width, width * 1.5
        rx = self.W / 2
        ry_top, ry_bot = self.H * 0.35, self.H * 0.65
        step = 2 * math.pi / num_points

        self.points = [
            Point(
                rx * math.cos(i * step),
                ry_bot + (ry_top if math.sin(i * step) > 0 else ry_bot) * math.sin(i * step)
            )
            for i in range(num_points)
        ]