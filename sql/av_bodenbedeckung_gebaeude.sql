with perimeter as (
    select
        ST_GeomFromText(%(polygon)s, 2056) as geom
), address as (
    select ln.atext || ' ' || gbei.hausnummer as strasse_hausnummer, gbei.lage as lage, gbei.gwr_egid as addr_egid
    from cs2bim.gebaeudeeingang gbei
    join cs2bim.lokalisationsname ln on (ln.benannte = gbei.gebaeudeeingang_von)
)
select
    ST_AsText(ST_CurveToLine(ST_Intersection(bb.geometrie, perimeter.geom), 1)) as wkt,
    ST_Contains(perimeter.geom, bb.geometrie) as complete_geometry,
    bb.art as art,
    'Amtliche Vermessung.Bodenbedeckung.' || bb.art as "group",
    STRING_AGG(gbnr.nummer, ', ') as nummer,
    STRING_AGG(gbnr.gwr_egid::text, ', ') as gwr_egid,
    COALESCE(STRING_AGG(objn.aname, ', '), '-') as gebaeudename,
    STRING_AGG(addr.strasse_hausnummer, ', ') as strasse_hausnummer,
    STRING_AGG(ortn.atext, ', ') as ort
from
    cs2bim.boflaeche bb
    left join cs2bim.gebaeudenummer gbnr on (gbnr.gebaeudenummer_von = bb.t_id)
    left join cs2bim.objektname objn on (objn.objektname_von = bb.t_id)
    left join address addr on ST_Contains(bb.geometrie, addr.lage)
    left join cs2bim.ortschaft ort on ST_Contains(ort.flaeche, bb.geometrie)
    left join cs2bim.ortschaftsname ortn on (ort.t_id = ortn.ortschaftsname_von)
    join perimeter on ST_Intersects(bb.geometrie, perimeter.geom)
where
    bb.art = 'Gebaeude'
group by
    bb.t_id,
    bb.geometrie,
    perimeter.geom,
    bb.art