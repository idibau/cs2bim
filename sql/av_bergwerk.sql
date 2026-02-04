with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(b.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, b.geometrie) as complete_geometry,
    g.nbident as nbident,
    g.nummer as nummer,
    g.egris_egrid as egris_egrid,
    g.gueltigkeit as gueltigkeit,
    g.vollstaendigkeit as vollstaendigkeit
from
    cs2bim.bergwerk b
    left join cs2bim.grundstueck g on (b.bergwerk_von = g.t_id)
    join perimeter on ST_Intersects(b.geometrie, perimeter.geom)