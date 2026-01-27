with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(bb.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, bb.geometrie) as complete_geometry,
    bb.art as art,
    'Amtliche Vermessung.Bodenbedeckung.' || bb.art as group,
    gbnr.nummer as nummer,
    gbnr.gwr_egid as egid
from
    cs2bim.boflaeche bb
    left join cs2bim.gebaeudenummer gbnr on (gbnr.gebaeudenummer_von = bb.t_id)
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude'
