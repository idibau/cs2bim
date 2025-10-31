import logging
import math

from shapely import wkt
from shapely.geometry import box

from config.configuration import config, ProjectionFeatureType, ProjectionAttributeConfig, ProjectionPropertyConfig
from config.projection_source import ProjectionSource
from core.ifc.model.element import Element
from core.ifc.model.projection import Projection
from core.tin.polygon import Area
from core.tin.raster import RasterPoints
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)


class ProjectionProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, project_origin: tuple[float, float, float]):
        feature_types = {ct.name: ct for ct in config.ifc.feature_types.projections}
        if not feature_types:
            logger.info("no projection feature types configured")
            return {}

        wkts = []
        feature_type_elements = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"fetch {feature_type_key}")
            with open(feature_type.sql_path, "r") as file:
                sql = file.read()
            elements = self.postgis_service.fetch_feature_type_elements(sql, polygon)
            feature_type_elements[feature_type_key] = elements
            for element_data in elements:
                wkts.append(element_data["wkt"])

        logger.info("calculate bounding box for fetching dtm files")
        if len(wkts) == 0:
            logger.warning("no content found for this polygon")
            bounding_box = self.postgis_service.get_bounding_box([polygon])
        else:
            bounding_box = self.postgis_service.get_bounding_box(wkts)

        logger.info("fetch dtm files")
        dtm_files = self.stac_service.fetch_dtm_assets(bounding_box, config.tin.grid_size.value)
        logger.info(f"fetched {len(dtm_files)} dtm files")

        projections = {}
        for feature_type_key, feature_type in feature_types.items():
            logger.info(f"create {feature_type_key} feature type")
            elements = feature_type_elements[feature_type_key]

            mesh_datas = []
            for element_data in elements:
                try:
                    mesh_data = MeshData(element_data, project_origin)
                    mesh_datas.append(mesh_data)
                except Exception as e:
                    logger.error(f"Error in element data: {e}. Skipping element...")

            for dtm_file in dtm_files:
                logger.info(f"load and process dtm file: {dtm_file}")
                dtm_points = RasterPoints(dtm_file, project_origin)
                for index, mesh_data in enumerate(mesh_datas):
                    logger.debug(f"calculate raster points for element {index + 1}/{len(elements)}")
                    mesh_data.add_raster_points(dtm_points)
            logger.info(f"finished processing dtm files")

            logger.info(f"create meshes for {feature_type_key} elements")
            for index, mesh_data in enumerate(mesh_datas):
                logger.debug(f"create mesh for element {index + 1}/{len(elements)}")
                element = Projection(mesh_data.create_mesh_data())
                self.add_attributes(element, feature_type.entity_mapping.attributes, mesh_data)
                self.add_properties(element, feature_type.entity_mapping.properties, mesh_data)
                self.add_groups(element, feature_type, mesh_data)

                spatial_structure = Element()
                self.add_attributes(spatial_structure, feature_type.spatial_structure_mapping.attributes, mesh_data)
                self.add_properties(spatial_structure, feature_type.spatial_structure_mapping.properties, mesh_data)
                element.spatial_structure = spatial_structure

                if feature_type.entity_type_mapping is not None:
                    projection_element_type = Element()
                    self.add_attributes(projection_element_type, feature_type.entity_type_mapping.attributes, mesh_data)
                    self.add_properties(projection_element_type, feature_type.entity_type_mapping.properties, mesh_data)
                    element.element_type = projection_element_type

                if not feature_type_key in projections:
                    projections[feature_type_key] = []
                projections[feature_type_key].append(element)
            logger.info("finished creating meshes")
        return projections

    def add_attributes(self, element: Element, attributes: list[ProjectionAttributeConfig], mesh_data):
        for attribute in attributes:
            if attribute.source.type == ProjectionSource.SQL:
                if attribute.source.expression in mesh_data.element_data:
                    element.add_attribute(attribute.attribute, mesh_data.element_data[attribute.source.expression])
            elif attribute.source.type == ProjectionSource.STATIC:
                element.add_attribute(attribute.attribute, attribute.source.expression)

    def add_properties(self, element: Element, properties: list[ProjectionPropertyConfig], mesh_data):
        for p in properties:
            if p.source.type == ProjectionSource.SQL:
                if p.source.expression in mesh_data.element_data:
                    element.add_property(p.property_set, p.property, mesh_data.element_data[p.source.expression])
            elif p.source.type == ProjectionSource.STATIC:
                element.add_property(p.property_set, p.property, p.source.expression)

    def add_groups(self, element: Projection, feature_type: ProjectionFeatureType, mesh_data):
        for group_mapping in feature_type.group_mapping:
            if group_mapping.type == ProjectionSource.SQL:
                element.add_group(mesh_data.element_data[group_mapping.expression])
            elif group_mapping.type == ProjectionSource.STATIC:
                element.add_group(group_mapping.expression)


class MeshData:

    def __init__(self, element_data, project_origin):
        self.element_data = element_data
        self.areas = []
        polygons = self.cut_polygon_if_large(element_data["wkt"])
        for polygon in polygons:
            self.areas.append(Area(polygon, project_origin[:2]))

    def add_raster_points(self, raster_points):
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

    def cut_polygon_if_large(self, wkt_str, max_size_m=1000):
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

        if len(cut_polys) > 1:
            logger.info(f"CUT POLYYYYYY {len(cut_polys)}")

        return cut_polys
