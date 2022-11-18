use TATOO_LOGS
/*
select mo_id, un_id, datediff(mi, viMo_hBegin, viMo_hEnd) as duration_min from Visite
			join Visite_Module on Visite.vi_id = Visite_Module.viMo_vi_id
			join Module on Module.mo_id = Visite_Module.viMo_mo_id
			join Univers on Univers.un_id = Module.mo_un_id
where Visite.vi_tsBegin > '2019-11-06 00:00:00'
*/

select distinct mo_id, un_id from Visite
			join Visite_Module on Visite.vi_id = Visite_Module.viMo_vi_id
			join Module on Module.mo_id = Visite_Module.viMo_mo_id
			join Univers on Univers.un_id = Module.mo_un_id
where Visite.vi_tsBegin > '2019-11-06 00:00:00'
order by mo_id, un_id

select distinct mo_id, mo_un_id from Module
order by mo_id, mo_un_id