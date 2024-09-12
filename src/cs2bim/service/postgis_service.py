from typing import Any
import psycopg2

from cs2bim.config.feature_class import FeatureClass
from cs2bim.service.bounding_box import BoundingBox
from cs2bim.config.configuration import config


class PostgisService:
    """Service that accesses a postgis database according to the configuration"""

    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            f"dbname = {config.dbname} user = {config.user} host = {config.host} password = {config.password} port = {config.port}"
        )

    def fetch_feature_class_elements(self, feature_class: FeatureClass, polygon: str) -> list[dict[str, Any]]:
        cur = self.connection.cursor()
        cur.execute(feature_class.sql, {"polygon": polygon})
        rows = cur.fetchall()
        if cur.description is not None:
            column_names = [desc[0] for desc in cur.description]
        else:
            raise Exception("Invalid sql")
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        return result

    def get_bounding_box(self, wkts: list[str]) -> BoundingBox:
        """Calculates and returns a minimal bounding box containg all geometries from the wkts"""
        cur = self.connection.cursor()
        cur.execute(
            f"""
                select ST_AsText(ST_Envelope(ST_Collect(ARRAY[{",".join(f"ST_GeomFromText('{wkt}')" for wkt in wkts)}])))
            """
        )
        wkt = cur.fetchall()[0][0]
        coordinates = []
        for points in wkt[9:-2].split(","):
            coordinates.append((float(points.split(" ")[0]), float(points.split(" ")[1])))
        return BoundingBox(coordinates[0][1], coordinates[0][0], coordinates[2][1], coordinates[2][0])
