import psycopg2

from cs2bim.enum.epsg_code import EPSGCode
from cs2bim.bounding_box import BoundingBox
from cs2bim.configuration import config
from cs2bim.model.parcel import Parcel
from cs2bim.model.land_cover import LandCover


class PostgisService:
    """Service that accesses a postgis database according to the configuration"""

    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            f"dbname = {config.dbname} user = {config.user} host = {config.host} password = {config.password}"
        )

    def fetch_parcels(self, bounding_box: BoundingBox) -> list[Parcel]:
        """Fetch all parcels that lay inside the bounding box"""
        cur = self.connection.cursor()
        cur.execute(
            f"""
                with perimeter as 
                    (select ST_GeomFromText('{bounding_box.get_lv95_polygon_wkt()}', 2056) as geom)                    
                select ST_AsText(ST_CurveToLine(geometrie, 1)), nbident, nummer, egris_egrid 
                from cs2bim.liegenschaft l
                left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
                join perimeter on ST_Intersects(l.geometrie, perimeter.geom)
            """
        )
        results = cur.fetchall()
        return list(Parcel(result[0], result[1], result[2], result[3]) for result in results)

    def fetch_building_land_cover(self, bounding_box: BoundingBox) -> list[LandCover]:
        """Fetch all building land covers that lay inside the bounding box"""
        cur = self.connection.cursor()
        cur.execute(
            f"""
                with perimeter as 
                    (select ST_GeomFromText('{bounding_box.get_lv95_polygon_wkt()}', 2056) as geom)                    
                select ST_AsText(ST_CurveToLine(geometrie, 1))
                from cs2bim.boflaeche bb 
                join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
                where bb.art = 'Gebaeude'
            """
        )
        results = cur.fetchall()
        return list(LandCover(result[0]) for result in results)

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
        return BoundingBox(coordinates[0][1], coordinates[0][0], coordinates[2][1], coordinates[2][0], EPSGCode.LV95)
