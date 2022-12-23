create or replace function is_overlapping(s_1 TIME, e_1 TIME, s_2 TIME, e_2 TIME)
    returns bool as
$$
BEGIN
    return (s_1, e_1) overlaps (s_2, e_2);
end;
$$ language plpgsql;