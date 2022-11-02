import http

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


@router.post('/{name}', status_code=http.HTTPStatus.CREATED)
async def create_group(name: str, response: Response, request: Request):
    await Group.create(name=name)
    response.headers['Location'] = request.url.path


@router.delete('/{name}')
async def create_group(name: str):
    g = await Group.get(name=name)
    await g.delete()
