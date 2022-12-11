import asyncio
import os
import sys
from pathlib import Path

import aiofiles
import starlette.routing
import tortoise.exceptions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from tortoise import connections
from tortoise.contrib.fastapi import register_tortoise

from .models import tortoise_models
from .routers import teachers, classrooms, schedule, groups

app = FastAPI(
    title=os.environ.get('TITLE', 'ASU MADI schedule API'),
    contact={'Vlatterran': 'soboleff@mail.ru'},
    default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8009"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app, include_in_schema=False)


app.include_router(groups.router, prefix='/groups', tags=['groups'])
app.include_router(teachers.router, prefix='/teachers', tags=['teacher'])
app.include_router(classrooms.router, prefix='/classrooms', tags=['classrooms'])
app.include_router(schedule.router, prefix='/schedule', tags=['schedule'])

register_tortoise(app,
                  db_url=os.environ.get('DATABASE_URL', 'sqlite://db.sqlite3'),
                  modules={"model": [tortoise_models]},
                  generate_schemas=True,
                  add_exception_handlers=True)

if sys.version_info >= (3, 11):
    async def startup(self) -> None:
        async with asyncio.TaskGroup() as tg:
            for handler in self.on_startup:
                if asyncio.iscoroutinefunction(handler):
                    tg.create_task(handler())
                else:
                    handler()
else:
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
