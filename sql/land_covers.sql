with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(geometrie, 1)) as wkt,
    "Amtliche Vermessung.Feature-Klassen.Bodenbedeckung (Gebaeude)" as group
from
    cs2bim.boflaeche bb
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude'