with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    cast(gbnr.gwr_egid as text) as egid,
    g.egris_egrid as egris_egrid
from
    cs2bim.boflaeche bb
    left join cs2bim.gebaeudenummer gbnr on (gbnr.gebaeudenummer_von = bb.t_id)
    left join cs2bim.liegenschaft l on ST_Intersects(bb.geometrie, l.geometrie)
    left join cs2bim.grundstueck g on (l.liegenschaft_von = g.t_id)
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude'