from fastapi import FastAPI

from schedule import Schedule

from CaseInsensitiveDict import CaseInsensitiveDict

app = FastAPI()

schedule = CaseInsensitiveDict()


@app.on_event('startup')
async def startup():
    global schedule
    while True:
        try:
            schedule.update(await Schedule.parse())
            break
        except Exception as e:
            print(e)


@app.get("/groups")
async def groups():
    return set(schedule.keys())


@app.get("/schedule/{group}")
async def group_schedule(group: str):
    return schedule.get(group)


@app.get("/schedule/{group}/{weekday}")
async def group_schedule(group: str, weekday: str):
    return schedule.get(group, {}).get(weekday.title())
