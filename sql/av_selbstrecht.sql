with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(sr.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, sr.geometrie) as complete_geometry
from
    cs2bim.selbstrecht sr
    join perimeter on ST_Intersects(sr.geometrie, perimeter.geom)