import os

import httpx
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(f'./{os.environ["STATIC_FILES_PATH"]}/html')

app.mount('/static', StaticFiles(directory=f'./{os.environ["STATIC_FILES_PATH"]}'), 'static')


@app.get('/')
async def root(request: Request):
    async with httpx.AsyncClient() as client:
        api = os.environ['API_URL']
        url = f"{api}/schedule/get_by_date"
        res = await client.get(url, params={'date': '2022-11-23'})
        cl = (await client.get(f'{api}/classes')).json()
        data = res.json()
        classes = {i: {} for i in cl}
        for line in data:
            classes.setdefault(line['classroom_id'], []).append(line)
    return templates.TemplateResponse('index.html', {'request': request, 'classes': classes})
