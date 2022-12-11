import time
import datetime


def is_week_even(day: time.struct_time):
    return ((day.tm_yday + datetime.datetime(day=1, month=1, year=2022).weekday()) // 7) % 2 == 0
