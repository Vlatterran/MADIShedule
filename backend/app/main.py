import asyncio
import os
import pathlib
from pathlib import Path

import aiofiles
import starlette.routing
import tortoise.exceptions
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, ORJSONResponse
from starlette.staticfiles import StaticFiles
from tortoise import connections
from tortoise.contrib.fastapi import register_tortoise

from .models import tortoise_models
from .routers import teachers, classrooms, schedule, groups

app = FastAPI(
    title=os.environ.get('TITLE', 'ASU MADI schedule API'),
    contact={'Vlatterran': 'soboleff@mail.ru'},
    default_response_class=ORJSONResponse)

app.mount('/static', StaticFiles(directory=f'{os.path.join(pathlib.Path(__file__).parents[1], "static")}'),
          name="static")
app.include_router(groups.router, prefix='/groups', tags=['groups'])
app.include_router(teachers.router, prefix='/teachers', tags=['teacher'])
app.include_router(classrooms.router, prefix='/classrooms', tags=['classrooms'])
app.include_router(schedule.router, prefix='/schedule', tags=['schedule'])

register_tortoise(app,
                  db_url=os.environ.get('DATABASE_URL', 'sqlite://db.sqlite3'),
                  modules={"model": [tortoise_models]},
                  generate_schemas=True,
                  add_exception_handlers=True)


async def startup(self) -> None:
    """
    Run any `.on_startup` event handlers.
    """
    tasks = []
    for handler in self.on_startup:
        if asyncio.iscoroutinefunction(handler):
            tasks.append(asyncio.create_task(handler()))
        else:
            handler()
    await asyncio.gather(*tasks)


starlette.routing.Router.startup = startup


@app.on_event('startup')
async def add_unique_constraint():
    while True:
        try:
            conn = connections.get('default')
            await asyncio.sleep(0.2)
            break
        except tortoise.exceptions.ConfigurationError:
            await asyncio.sleep(0.1)
    ap = Path(__file__)

    async def run_sql_script(path: Path):
        async with aiofiles.open(path, 'r', encoding='utf8') as f:
            await conn.execute_query(await f.read())

    while True:
        try:
            await asyncio.gather(*(run_sql_script(script_name)
                                   for script_name
                                   in ap.parent.joinpath('models/sql/sqlite').glob('**/*')))
            break
        except tortoise.exceptions.OperationalError:
            await asyncio.sleep(0.1)


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def root():
    return '/docs'
