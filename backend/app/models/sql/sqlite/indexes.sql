create unique index if not exists my_index
    on line (start, end, weekday, week_type, period, classroom_id)
    where period != 2;