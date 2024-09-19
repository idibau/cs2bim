with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(geometrie, perimeter.geom), 1)) as wkt,
    case 
        when bb.art = 'Gebaeude' then 'Amtliche Vermessung.Feature-Klassen.Bodenbedeckung (Gebaeude)' 
        else 'Amtliche Vermessung.Feature-Klassen.Bodenbedeckung (Trottoir)' 
    end as group
from
    cs2bim.boflaeche bb
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude' or bb.art = 'befestigt.Trottoir'