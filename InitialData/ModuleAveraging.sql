drop function dbo.day_part;
go
create function dbo.day_part(@start_date datetime, @end_date datetime)
returns int
as
begin
	declare @middle time;
	declare @day_part varchar(10);
	set @middle = cast(DATEADD(ms, 
          DATEDIFF(ms,@start_date, @end_date)/2,
         @start_date) as time) 
	if (DATEPART(HOUR, @middle) < 12)
		set @day_part = '!!!morning'
	if ((DATEPART(HOUR, @middle) >= 12) and (DATEPART(HOUR, @middle) <16)) 
		set @day_part = '!!day'
	if (DATEPART(HOUR, @middle) >= 16)
		set @day_part = '!evening'
	return cast(DATEPART(HOUR, @middle) as int)
		
end;

go

/*with count_per_hour as (
select  viMo_mo_id, cast(viMo_tsBegin as date) as [date],  dbo.day_part(viMo_tsBegin, viMo_tsEnd) as day_part, count(viMo_mo_id) as [count] from Visite_Module
where viMo_tsBegin > '2019-11-06 09:32:00'
group by viMo_mo_id,  cast(viMo_tsBegin as date), dbo.day_part(viMo_tsBegin, viMo_tsEnd))
select viMo_mo_id, day_part, avg([count]) as average  from count_per_hour
group by viMo_mo_id, day_part
order by viMo_mo_id, day_part
*/
/*
with time_per_module_part_date as (
select distinct viMo_vi_id, mo_id, cast(viMo_tsBegin as date) as [date], dbo.day_part(viMo_tsBegin, viMo_tsEnd) as day_part, viMo_durMin from Visite 
				--join Visite_Tag on Visite.vi_id = Visite_Tag.viTa_vi_id
				--join Tag on Visite_Tag.viTa_ta_id = Tag.ta_id
				--join Dispositif on Tag.ta_di_id = Dispositif.di_id
				join Visite_Module on Visite.vi_id = Visite_Module.viMo_vi_id
				join Module on Visite_Module.viMo_mo_id = Module.mo_id --and Dispositif.di_mo_id = Module.mo_id
where vi_tsBegin > '2019-11-06 00:00:00'), 
summed as (
select  mo_id, [date], day_part, (viMo_durMin) as average from time_per_module_part_date
--group by mo_id, [date], day_part, viMo_durMin)
)
select  mo_id, day_part, viMo_durMin from time_per_module_part_date
--group by  mo_id, day_part
order by  mo_id, day_part


go*/

with time_per_module_part_date as (
select distinct viMo_vi_id, mo_id, di_id, ta_id, viTa_tsBegin, viTa_tsEnd,  cast(viTa_tsBegin as date) as [date], dbo.day_part(viTa_tsBegin, viTa_tsEnd) as day_part, viTa_hBegin, viTa_hEnd, datediff(s, viTa_hBegin, viTa_hEnd) as diff from Visite 
				join Visite_Tag on Visite.vi_id = Visite_Tag.viTa_vi_id
				join Tag on Visite_Tag.viTa_ta_id = Tag.ta_id
				join Dispositif on Tag.ta_di_id = Dispositif.di_id
				join Visite_Module on Visite.vi_id = Visite_Module.viMo_vi_id
				join Module on Visite_Module.viMo_mo_id = Module.mo_id and Dispositif.di_mo_id = Module.mo_id
where vi_tsBegin > '2019-11-06 00:00:00' and datediff(s, viTa_hBegin, viTa_hEnd) > 0), 
summed as (
select   viMo_vi_id, mo_id, di_id,[date],day_part, sum(diff) as diff from time_per_module_part_date
group by viMo_vi_id, mo_id, di_id,[date],day_part)
select  di_id, day_part, diff from summed
order by  di_id, day_part, diff

--select mo_id, day_part, avg([count]) as average  from time_per_module_part_date
--group by mo_id, day_part
--order by mo_id, day_part


--vi_id, vi_tsBegin, vi_tsEnd, ta_id, viTa_tsBegin, viTa_tsEnd, di_id, mo_id, viMo_order, viMo_tsBegin, viMo_tsEnd
/*With data_ as (select * from Visite_Module where viMo_mo_id =3  and viMo_tsBegin > '2019-11-06 09:32:00'), 
Times AS(
    SELECT V.[Time] AS Start_Time,
           LEAD(V.Time) OVER (ORDER BY V.Time) AS End_Time
    FROM data_ d
         CROSS APPLY (VALUES(d.viMo_tsBegin),(d.viMo_tsEnd))V([Time]))
SELECT T.Start_Time,
       T.End_Time,
       COUNT(d.viMo_vi_id) AS [Count]
FROM Times T
     LEFT JOIN data_ d ON d.viMo_tsBegin < T.End_Time
                         AND d.viMo_tsEnd > T.Start_Time
WHERE T.End_Time IS NOT NULL
GROUP BY T.Start_Time,
         T.End_Time;
*/
