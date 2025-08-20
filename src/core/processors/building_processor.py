import logging

from lxml import etree

from config.configuration import config
from core.ifc.model.building import Building
from service.postgis_service import PostgisService
from service.stac_service import STACService

logger = logging.getLogger(__name__)



class BuildingProcessor:

    def __init__(self):
        self.postgis_service = PostgisService()
        self.stac_service = STACService()

    def process(self, polygon, origin, model):

        building_config = config.ifc.building
        bounding_box = self.postgis_service.get_bounding_box([polygon])
        city_gmls = self.stac_service.fetch_city_gml_assets(bounding_box)
        logger.info(f"fetched {len(city_gmls)} city gml files")

        for feature_class_key, feature_class in building_config.items():
            logger.info(f"fetch {feature_class_key}")
            with open(feature_class.sql_path, "r") as file:
                sql = file.read()
            egids = [item["egid"] for item in self.postgis_service.fetch_feature_class_elements(sql, polygon)]

            ns = {
                "bldg": "http://www.opengis.net/citygml/building/2.0",
                "gml": "http://www.opengis.net/gml",
                "gen": "http://www.opengis.net/citygml/generics/2.0",
            }

            for city_gml in city_gmls:
                context_iter = etree.iterparse(city_gml, events=("end",), tag="{http://www.opengis.net/citygml/building/2.0}Building")

                for event, building in context_iter:
                    egid_elem = building.find(".//gen:intAttribute[@name='EGID']", namespaces=ns)
                    if egid_elem is not None:
                        value_elem = egid_elem.find("gen:value", namespaces=ns)
                        if value_elem is not None:
                            egid = value_elem.text.strip()
                            if egid in egids:
                                for pos_list in building.xpath(".//bldg:lod2Solid/gml:Solid[@srsName='EPSG:2056' and @srsDimension='3']/gml:exterior/gml:CompositeSurface/gml:surfaceMember/gml:Polygon/gml:exterior/gml:LinearRing/gml:posList", namespaces=ns):
                                    if pos_list is None:
                                        continue

                                    coords = list(map(float, pos_list.text.split()))
                                    points = [(float(coords[i] - origin[0]), float(coords[i + 1] - origin[1]), float(coords[i + 2] - origin[2])) for i in range(0, len(coords), 3)]

                                    element = Building(points)
                                    model.add_building(feature_class_key, element)

                    building.clear()

                    while building.getprevious() is not None:
                        del building.getparent()[0]