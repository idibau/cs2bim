with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(l.geometrie, 1)) as wkt,
    ST_Contains(perimeter.geom, l.geometrie) as complete_geometry,
    g.nbident as nbident,
    g.nummer as nummer,
    g.egris_egrid as egris_egrid,
    g.gueltigkeit as gueltigkeit,
    g.vollstaendigkeit as vollstaendigkeit
from
    cs2bim_dmav.liegenschaft l
    left join cs2bim_dmav.grundstueck g on (l.grundstueck = g.t_id)
    join perimeter on ST_Intersects(l.geometrie, perimeter.geom)