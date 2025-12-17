with perimeter as (
    select ST_GeomFromText(%(polygon)s, 2056) as geom
),
relevant_lines as (
    select l.t_id, l.linie, l.breite, l.profiltyp, l.objektart
    from cs2bim.bl_lkmap.lklinie l
    join perimeter p on ST_Intersects(l.linie, p.geom)
),
relevant_areas as (
    select l.t_id, l.flaeche, l.objektart
    from cs2bim.bl_lkmap.lkflaeche l
    join perimeter p on ST_Intersects(l.flaeche, p.geom)
),
relevant_points as (
    select l.t_id, l.dimension1, l.symbolpos, l.objektart
    from cs2bim.bl_lkmap.lkpunkt l
    join perimeter p on ST_Intersects(l.symbolpos, p.geom)
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
    where ref_pos is not null and z_pos is not null -- Ensure pairs are complete
    group by t_id, objektart
    -- Enforce logic: Must have data to form a line
    having count(*) > 0
),
refs_single as (
    select distinct on (lkflaecheref, lkpunktref, art)
        aposition, lkflaecheref, lkpunktref, art
    from cs2bim.bl_lkmap.abstichpunkt
    where art in ('KoteRef', 'KoteZ')
    order by lkflaecheref, lkpunktref, art, t_id
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
    null as area,
    'POLYLINE' as extrusion_type,
    lg.geom_3d_line as polyline,
    null::geometry as start_point,
    null::geometry as end_point,
    l.t_id::text as t_id,
    'Leitungskataster.' || l.objektart as "group"
from relevant_lines l
join line_geometry_build lg on l.t_id = lg.t_id
union all
select
    'POLYGON',
    null,
    null,
    ST_Translate(l.flaeche, -ST_X(kr.aposition), -ST_Y(kr.aposition)),
    'LINE',
    null,
    kr.aposition,
    kz.aposition,
    l.t_id::text,
    'Leitungskataster.' ||  l.objektart
from relevant_areas l
left join refs_single kr on kr.lkflaecheref = l.t_id and kr.art = 'KoteRef'
left join refs_single kz on kz.lkflaecheref = l.t_id and kz.art = 'KoteZ'
union all
select
    'CIRCLE',
    null,
    l.dimension1::float / 1000,
    null,
    'LINE',
    null,
    kr.aposition,
    kz.aposition,
    l.t_id::text,
    'Leitungskataster.' || l.objektart
from relevant_points l
left join refs_single kr on kr.lkpunktref = l.t_id and kr.art = 'KoteRef'
left join refs_single kz on kz.lkpunktref = l.t_id and kz.art = 'KoteZ';