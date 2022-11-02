import http

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


@router.post('/{name}', status_code=http.HTTPStatus.CREATED)
async def create_teacher(name: str, response: Response, request: Request):
    await Classroom.create(name=name)
    response.headers['Location'] = request.url.path


@router.delete('/{name}')
async def delete_classroom(name: str):
    await Classroom.filter(name=name).delete()
