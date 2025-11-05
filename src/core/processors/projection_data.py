import logging
import math
from typing import Any

from shapely import wkt
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

from core.ifc.model.coordinates import Coordinates
from core.tin.area import Area
from core.tin.raster_points import RasterPoints

logger = logging.getLogger(__name__)


class ProjectionData:

    def __init__(self, element_row: dict[str, Any], project_origin: Coordinates):
        self.element_row = element_row
        self.areas = []
        polygons = self.cut_polygon_if_large(element_row["wkt"])
        for polygon in polygons:
            self.areas.append(Area(polygon, project_origin))

    def add_raster_points(self, raster_points: RasterPoints):
        for area in self.areas:
            area.add_raster_points(raster_points)

    def create_mesh_data(self):
        points_total = []
        point_to_index = {}
        indices_total = []

        for area in self.areas:
            mesh = area.create_mesh()
            points, faces = mesh.get_data()

            for face in faces:
                new_face = []
                for local_idx in face:
                    p = tuple(points[local_idx])
                    if p not in point_to_index:
                        point_to_index[p] = len(points_total)
                        points_total.append(p)
                    new_face.append(point_to_index[p])
                indices_total.append(tuple(new_face))

        return points_total, indices_total

    def cut_polygon_if_large(self, wkt_str: str, max_size_m: int = 1000) -> list[BaseGeometry]:
        poly = wkt.loads(wkt_str)

        minx, miny, maxx, maxy = poly.bounds
        width = maxx - minx
        height = maxy - miny

        if width <= max_size_m and height <= max_size_m:
            return [poly]

        nx = math.ceil(width / max_size_m)
        ny = math.ceil(height / max_size_m)

        cut_polys = []
        for i in range(nx):
            for j in range(ny):
                x1 = minx + i * max_size_m
                y1 = miny + j * max_size_m
                x2 = min(x1 + max_size_m, maxx)
                y2 = min(y1 + max_size_m, maxy)
                cell = box(x1, y1, x2, y2)
                inter = poly.intersection(cell)
                if inter.is_empty:
                    continue
                if inter.geom_type == "Polygon":
                    cut_polys.append(inter)
                elif inter.geom_type == "MultiPolygon":
                    cut_polys.extend(list(inter.geoms))
                else:
                    pass

        return cut_polys
