with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(bb.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, bb.geometrie) as complete_geometry,
    bb.art as art,
    'Amtliche Vermessung.Bodenbedeckung.' || bb.art as group
from
    cs2bim.boflaeche bb
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art like 'humusiert%%'
