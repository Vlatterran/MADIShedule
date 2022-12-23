create unique index if not exists my_index
    on line (start_time, end_time, weekday, week_type, period, classroom_id)
    where period != 2;