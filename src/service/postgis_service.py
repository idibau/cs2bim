import psycopg2

from configuration import config
from model.parcel import Parcel
from model.land_cover import LandCover


class PostgisService:

    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            f"dbname = {config.dbname} user = {config.user} host = {config.host} password = {config.password}"
        )

    def fetch_parcels(self, wkt: str) -> list[Parcel]:
        cur = self.connection.cursor()
        cur.execute(
            f"""
                with perimeter as 
                    (select ST_GeomFromText('{wkt}', 2056) as geom)                    
                select ST_AsText(ST_CurveToLine(geometrie)), nbident, nummer, egris_egrid 
                from cs2bim.liegenschaft l
                left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
                join perimeter on ST_Intersects(l.geometrie, perimeter.geom)
            """
        )
        results = cur.fetchall()
        return list(Parcel(result[0], result[1], result[2], result[3]) for result in results)
    
    def fetch_land_cover(self, wkt: str) -> list[LandCover]:
        cur = self.connection.cursor()
        cur.execute(
            f"""
                with perimeter as 
                    (select ST_GeomFromText('{wkt}', 2056) as geom)                    
                select ST_AsText(ST_CurveToLine(geometrie))
                from cs2bim.boflaeche bb 
                join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
                where bb.art = 'Gebaeude'
            """
        )
        results = cur.fetchall()
        return list(LandCover(result[0]) for result in results)