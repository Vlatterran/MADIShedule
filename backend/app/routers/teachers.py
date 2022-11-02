import http

from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response

from ..models.pydantic_models import Teacher_Pydantic
from ..models.tortoise_models import Teacher

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_teachers():
    return await Teacher.all().values_list('name', flat=True)


@router.get("/{name}", response_model=Teacher_Pydantic)
async def get_teacher(name: str):
    return await Teacher_Pydantic.from_queryset_single(Teacher.filter(name=name).first())


@router.post('/{name}', status_code=http.HTTPStatus.CREATED)
async def create_teacher(name: str, response: Response, request: Request):
    await Teacher.create(name=name)
    print(request.url.path)
    response.headers['Location'] = request.url.path


@router.delete('/{name}')
async def delete_teacher(name: str):
    await Teacher.filter(name=name).delete()
