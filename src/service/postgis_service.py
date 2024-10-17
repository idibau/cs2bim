from typing import Any
import psycopg2

from config.configuration import config
from service.bounding_box import BoundingBox


class PostgisService:
    """Service that accesses a postgis database according to the configuration"""

    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            f"dbname = {config.dbname} user = {config.user} host = {config.host} password = {config.password} port = {config.port}"
        )

    def fetch_feature_class_elements(self, sql: str, polygon: str) -> list[dict[str, Any]]:
        cur = self.connection.cursor()
        cur.execute(sql, {"polygon": polygon})
        rows = cur.fetchall()
        if cur.description is not None:
            column_names = [desc[0] for desc in cur.description]
        else:
            raise Exception("Invalid sql")
        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        cur.close()
        return result

    def get_bounding_box(self, wkts: list[str]) -> BoundingBox:
        """Calculates and returns a minimal bounding box containing all geometries from the wkts"""
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
        cur.close()
        return BoundingBox(coordinates[0][1], coordinates[0][0], coordinates[2][1], coordinates[2][0])
