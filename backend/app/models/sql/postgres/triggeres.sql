create or replace function check_monthly_overwhelming() returns trigger as
$check_monthly_overwhelming$
begin
    if new.period = 2 then
        if
                (select count(*)
                 from line
                 where period = new.period
                   and (start_time, end_time) overlaps (new.start_time, new.end_time)
                   and weekday = new.weekday
                   and week_type = new.week_type
                   and classroom_id = new.classroom_id) = 2 THEN
            raise integrity_constraint_violation using message = 'Can not add more rows at this time';
        end if;
    elseif
            (select count(*)
             from line
             where (period = new.period)
               and (start_time, end_time) overlaps (new.start_time, new.end_time)
               and weekday = new.weekday
               and week_type = new.week_type
               and classroom_id = new.classroom_id) = 1 then

        raise integrity_constraint_violation using message = 'Can not add more rows at this time';
    end if;
    return NEW;
end;
$check_monthly_overwhelming$ language plpgsql;

create or replace trigger check_monthly_overwhelming
    before insert
    on line
    for each row
execute function check_monthly_overwhelming();