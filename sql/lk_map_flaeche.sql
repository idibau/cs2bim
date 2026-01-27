with perimeter as (
    select ST_GeomFromText(%(polygon)s, 2056) as geom
),
relevant_areas as (
    select l.t_id, l.flaeche, l.objektart, l.eigentuemerref, l.lagebestimmung, l.hoehenbestimmung, l.astatus
    from cs2bim.bl_lkmap.lkflaeche l
    join perimeter p on ST_Intersects(l.flaeche, p.geom)
),
refs_single as (
    select distinct on (lkflaecheref, lkpunktref, art)
        aposition, lkflaecheref, lkpunktref, art
    from cs2bim.bl_lkmap.abstichpunkt
    where art in ('KoteRef', 'KoteZ')
    order by lkflaecheref, lkpunktref, art, t_id
)
select
    'POLYGON' as cross_section,
    ST_Translate(l.flaeche, -ST_X(kr.aposition), -ST_Y(kr.aposition)) as area,
    'LINE' as extrusion_type,
    kr.aposition as start_point,
    kz.aposition as end_point,
    case
        when l.objektart like 'Abwasser%%' then 'Leitungskataster.Abwasser'
        when l.objektart like 'Elektrizität%%' then 'Leitungskataster.Elektrizitaet'
        when l.objektart like 'Fernwirkkabel%%' then 'Leitungskataster.Fernwirkkabel'
        when l.objektart like 'Gas%%' then 'Leitungskataster.Gas'
        when l.objektart like 'Kommunikation%%' then 'Leitungskataster.Kommunikation'
        when l.objektart like 'Schutzrohr%%' then 'Leitungskataster.Schutzrohr'
        when l.objektart like 'Wärme%%' then 'Leitungskataster.Waerme'
        when l.objektart like 'Wasser%%' then 'Leitungskataster.Wasser'
        when l.objektart like 'weitere Medien%%' then 'Leitungskataster.weitere Medien'
        else null
    end as "group",
    'LKFLAECHE' as name,
    l.lagebestimmung as lagebestimmung,
    l.hoehenbestimmung as hoehenbestimmung,
    l.astatus as status,
    o.t_ili_tid as eigentuemer,
    l.objektart as objektart
from relevant_areas l
left join refs_single kr on kr.lkflaecheref = l.t_id and kr.art = 'KoteRef'
left join refs_single kz on kz.lkflaecheref = l.t_id and kz.art = 'KoteZ'
left join cs2bim.bl_lkmap.organisation o on l.eigentuemerref = o.t_id