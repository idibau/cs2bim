with perimeter as (
    select ST_GeomFromText(%(polygon)s, 2056) as geom
),
relevant_lines as (
    select l.t_id, l.linie, l.breite, l.profiltyp, l.objektart, l.breite_annahme, l.lagebestimmung, l.hoehenbestimmung, l.astatus, l.eigentuemerref
    from cs2bim.bl_lkmap.lklinie l
    join perimeter p on ST_Intersects(l.linie, p.geom)
),
line_pairs as (
    select
        l.t_id,
        l.objektart,
        row_number() over(partition by l.t_id, a.art order by ST_LineLocatePoint(l.linie, ST_Force2D(a.aposition))) as pair_idx,
        a.art,
        a.aposition
    from cs2bim.bl_lkmap.abstichpunkt a
    join relevant_lines l on a.lklinieref = l.t_id
    where a.art in ('KoteRef', 'KoteZ')
),
line_geometry_build as (
    select
        t_id,
        objektart,
        ST_MakeLine(
            ST_MakePoint(
                ST_X(ref_pos),
                ST_Y(ref_pos),
                (ST_Z(ref_pos) + ST_Z(z_pos)) / 2.0
            ) order by pair_idx
        ) as geom_3d_line,
        avg(ST_Z(z_pos) - ST_Z(ref_pos)) as avg_height
    from (
        select
            t_id,
            objektart,
            pair_idx,
            max(aposition) filter (where art = 'KoteRef') as ref_pos,
            max(aposition) filter (where art = 'KoteZ')   as z_pos
        from line_pairs
        group by t_id, objektart, pair_idx
    ) pairs
    where ref_pos is not null and z_pos is not null
    group by t_id, objektart
    having count(*) > 0
)
select
    case l.profiltyp
        when 'Kreisprofil'     then 'CIRCLE'
        when 'Rechteckprofil'  then 'RECTANGLE'
        when 'Eiprofil'        then 'EGG'
        else null
    end as cross_section,
    lg.avg_height::float as height,
    l.breite::float / 1000 as width,
    l.breite_annahme::float / 1000 as breite_annahme,
    l.profiltyp as profiltyp,
    'POLYLINE' as extrusion_type,
    lg.geom_3d_line as polyline,
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
    'LKLINIE' as name,
    l.lagebestimmung as lagebestimmung,
    l.hoehenbestimmung as hoehenbestimmung,
    l.astatus as status,
    o.t_ili_tid as eigentuemer,
    l.objektart as objektart
from relevant_lines l
join line_geometry_build lg on l.t_id = lg.t_id
left join cs2bim.bl_lkmap.organisation o on l.eigentuemerref = o.t_id