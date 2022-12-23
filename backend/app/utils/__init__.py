import time
import datetime
from pathlib import Path

import aiofiles


def is_week_even(day: time.struct_time):
    return ((day.tm_yday + datetime.datetime(day=1, month=1, year=2022).weekday()) // 7) % 2 == 0


def is_overlapping(s_1: datetime.time, e_1: datetime.time,
                   s_2: datetime.time, e_2: datetime.time) -> bool:
    return s_2 < s_1 < e_2 or s_2 < e_1 < e_2 or s_1 < s_2 < e_1 or s_1 < e_2 < e_1


async def run_sql_script(conn, path: Path):
    async with aiofiles.open(path, 'r', encoding='utf8') as f:
        await conn.execute_script(await f.read())
