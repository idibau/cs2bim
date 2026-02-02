with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(b.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, b.geometrie) as complete_geometry
from
    cs2bim.bergwerk b
    join perimeter on ST_Intersects(b.geometrie, perimeter.geom)