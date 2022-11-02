import http
import urllib.parse

from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.routing import APIRouter

from ..models.pydantic_models import Teacher_Pydantic
from ..models.tortoise_models import Teacher

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_teachers():
    return await Teacher.all().values_list('name', flat=True)


@router.get("/{name}", response_model=Teacher_Pydantic)
async def get_teacher(name: str):
    return await Teacher_Pydantic.from_queryset_single(Teacher.filter(name=name).first())


@router.post('/{name}', status_code=http.HTTPStatus.CREATED, response_model=Teacher_Pydantic,
             responses={
                 201: {'headers': {'Location': {'type': 'URL', 'description': 'URL for created teacher'}}}
             })
async def create_teacher(name: str, response: Response, request: Request):
    t = await Teacher.create(name=name)
    await t.fetch_related()
    response.headers['Location'] = str(request.url.replace(path=urllib.parse.quote(request.url.path)))
    return Teacher_Pydantic.from_orm(t)


@router.delete('/{name}')
async def delete_teacher(name: str):
    await Teacher.filter(name=name).delete()
