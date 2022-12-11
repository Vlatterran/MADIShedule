import datetime
import os

from fastapi import FastAPI, Path
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
async def root(request: Request, date: datetime.date = None):
    if date is None:
        date = datetime.date.today()
    return templates.TemplateResponse('index.html', {'request': request, 'date': date.isoformat()})
