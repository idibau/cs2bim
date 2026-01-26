with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(l.geometrie, 1)) as wkt,
    g.nbident as nbident,
    g.nummer as nummer,
    g.egris_egrid as egris_egrid,
    g.gueltigkeit as gueltigkeit,
    g.vollstaendigkeit as vollstaendigkeit
from
    cs2bim.liegenschaft l
    left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
    join perimeter on ST_Intersects(l.geometrie, perimeter.geom)