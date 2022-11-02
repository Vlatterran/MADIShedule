import http
import urllib.parse

from fastapi.routing import APIRouter
from fastapi.responses import Response
from fastapi.requests import Request

from ..models.tortoise_models import Classroom
from ..models.pydantic_models import Classroom_Pydantic

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_classrooms():
    return await Classroom.all().values_list('name', flat=True)


@router.get('/{name}', response_model=Classroom_Pydantic)
async def get_classroom(name: str):
    return await Classroom_Pydantic.from_queryset_single(Classroom.get(name=name).only(Classroom.fields))


@router.post('/{name}', status_code=http.HTTPStatus.CREATED, response_model=Classroom_Pydantic,
             responses={
                 201: {'headers': {'Location': {'type': 'URL', 'description': 'URL for created classroom'}}}
             })
async def create_teacher(name: str, response: Response, request: Request):
    c = await Classroom.create(name=name)
    await c.fetch_related('lines')
    response.headers['Location'] = str(request.url.replace(path=urllib.parse.quote(request.url.path)))
    return Classroom_Pydantic.from_orm(c)


@router.delete('/{name}')
async def delete_classroom(name: str):
    await Classroom.filter(name=name).delete()
