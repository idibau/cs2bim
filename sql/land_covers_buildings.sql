with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(geometrie, 1)) as wkt,
    bb.art,
    'USERDEFINED' as predefined_type,
    cast(gbnr.gwr_egid as text) as gwr_egid,
    'Amtliche Vermessung.Gebaeude' as group
from
    cs2bim.boflaeche bb
    left join cs2bim.gebaeudenummer gbnr on (gbnr.gebaeudenummer_von = bb.t_id)
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude'
