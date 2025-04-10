with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(l.geometrie, perimeter.geom), 1)) as wkt,
    g.nbident as nbident,
    g.nummer as nummer,
    g.egris_egrid as egris_egrid,
    'USERDEFINED' as predefined_type,
    'Liegenschaft' as object_type,
    'Amtliche Vermessung.Liegenschaften' as group
from
    cs2bim.liegenschaft l
    left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
    join perimeter on ST_Intersects(l.geometrie, perimeter.geom)