with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(l.geometrie, 1)) as wkt,
    g.nbident,
    g.nummer,
    g.egris_egrid,
    'Amtliche Vermessung.Feature-Klassen.Liegenschaften' as group
from
    cs2bim.liegenschaft l
    left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
    join perimeter on ST_Contains(perimeter.geom, l.geometrie)