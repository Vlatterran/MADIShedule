create trigger if not exists check_monthly_overwhelming
    before insert
    on line
begin
    select case
               when (select count(*)
                     from line
                     where period = new.period
                       and cast(start as varchar) like new.start || '%'
                       and weekday = new.weekday
                       and week_type = new.week_type
                       and classroom_id = new.classroom_id
                       and cast(end as varchar) like new.end || '%') = 2
                   then raise(abort, 'Can not add more rows at this time')
               end;
end;