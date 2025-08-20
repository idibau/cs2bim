with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    cast(gbnr.gwr_egid as text) as egid
from
    cs2bim.boflaeche bb
    left join cs2bim.gebaeudenummer gbnr on (gbnr.gebaeudenummer_von = bb.t_id)
    join perimeter on ST_Contains(perimeter.geom, bb.geometrie)
where
    bb.art = 'Gebaeude'