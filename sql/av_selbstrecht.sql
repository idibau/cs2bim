with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(s.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, s.geometrie) as complete_geometry,
    g.nbident as nbident,
    g.nummer as nummer,
    g.egris_egrid as egris_egrid,
    g.gueltigkeit as gueltigkeit,
    g.vollstaendigkeit as vollstaendigkeit
from
    cs2bim.selbstrecht s
    left join cs2bim.grundstueck g on (s.selbstrecht_von = g.t_id)
    join perimeter on ST_Intersects(s.geometrie, perimeter.geom)