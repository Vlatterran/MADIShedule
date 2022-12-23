import asyncio
import logging
import os
import sys
from pathlib import Path

import starlette.routing
import tortoise.exceptions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from tortoise import connections
from tortoise.backends.sqlite import SqliteClient
from tortoise.contrib.fastapi import register_tortoise

from .models import tortoise_models
from .routers import teachers, classrooms, schedule, groups
from .utils import is_overlapping, run_sql_script

app = FastAPI(
    title=os.environ.get('TITLE', 'ASU MADI schedule API'),
    contact={'Vlatterran': 'soboleff@mail.ru'},
    default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
            logging.info('Database connections established')
            await asyncio.sleep(2)
            logging.debug(conn.capabilities.dialect)
            break
        except tortoise.exceptions.ConfigurationError:
            logging.exception('can not establish connection to database')
            await asyncio.sleep(1)

    try:
        if isinstance(conn, SqliteClient):
            await conn._connection.create_function('is_overlapping', 4, is_overlapping)
        await asyncio.gather(*(run_sql_script(conn, script_name)
                               for script_name
                               in Path(__file__).parent.joinpath(f'models/sql/{conn.capabilities.dialect}')
                             .glob('**/*')))
    except tortoise.exceptions.OperationalError:
        logging.exception('can not execute sql script')
    except FileNotFoundError:
        logging.info('No SQL scripts for this dialect found')


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def root():
    return '/docs'
