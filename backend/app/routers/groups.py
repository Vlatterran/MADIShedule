import http
import urllib.parse

from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response

from ..models.tortoise_models import Group
from ..models.pydantic_models import Group_Pydantic

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_groups():
    return await Group.all().values_list('name', flat=True)


@router.get('/{name}', response_model=Group_Pydantic)
async def get_group(name: str):
    return await Group_Pydantic.from_queryset_single(Group.get(name=name))


@router.post('/{name}', status_code=http.HTTPStatus.CREATED, response_model=Group_Pydantic,
             responses={
                 201: {'headers': {'Location': {'type': 'URL', 'description': 'URL for created group'}}}
             })
async def create_group(name: str, response: Response, request: Request):
    g = await Group.create(name=name)
    await g.fetch_related('lines')
    response.headers['Location'] = str(request.url.replace(path=urllib.parse.quote(request.url.path)))
    return Group_Pydantic.from_orm(g)


@router.delete('/{name}')
async def create_group(name: str):
    g = await Group.get(name=name)
    await g.delete()
