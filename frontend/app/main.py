import datetime
import os

import httpx
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(docs_url=None, redoc_url=None)


@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app, include_in_schema=False)


templates = Jinja2Templates(f'./{os.environ["STATIC_FILES_PATH"]}/html')

app.mount('/static', StaticFiles(directory=f'./{os.environ["STATIC_FILES_PATH"]}'), 'static')


@app.get('/')
async def root(request: Request):
    async with httpx.AsyncClient() as client:
        api = os.environ['API_URL']
        url = f"{api}/schedule/get_by_date"
        res = await client.get(url, params={'date': datetime.date.today().isoformat()})
        cl = (await client.get(f'{api}/classes')).json()
        data = res.json()
        classes = {i: {} for i in cl}
        for line in data:
            classes.setdefault(line['classroom_id'], []).append(line)
    return templates.TemplateResponse('index.html', {'request': request, 'classes': classes})
