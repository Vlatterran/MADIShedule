import datetime

from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from tortoise.expressions import RawSQL
from tortoise.queryset import QuerySet

from ..models.pydantic_models import Line_Pydantic, LineIn_Pydantic, LinePeriodicIn_Pydantic
from ..models.tortoise_models import Line, Frequency

router = APIRouter()


async def check_time(existing_lines: QuerySet[Line], line: LineIn_Pydantic | LinePeriodicIn_Pydantic) -> str | None:
    if line.start_time > line.end_time:
        return f'End time must be greater than start'
    async for existing_line in existing_lines:
        if not (existing_line.start_time.replace(tzinfo=None) > line.end_time or
                existing_line.end_time.replace(tzinfo=None) < line.start_time):
            if hasattr(line, 'period') and existing_line.period == line.period == Frequency.MONTH:
                query = Line.filter(RawSQL(f"overlaps(start_time, end_time, {line.start_time}, {line.end_time})"),
                                    classroom=line.classroom_id,
                                    week_type=line.week_type,
                                    weekday=line.weekday,
                                    period=Frequency.MONTH)
                c = await query.count()
                if c == 1:
                    continue
                return f'overlapping time with schedule line(ids={await query.values_list("id", flat=True)})'
            return f'overlapping time with schedule line(id={existing_line.id})'


@router.post("/", response_model=list[Line_Pydantic],
             deprecated=True,
             description='For debug only',
             tags=['debug'])
async def get_schedule(filters: dict = None):
    return await Line_Pydantic.from_queryset(Line.all().filter(**filters))


@router.get("/get_by_date", response_model=list[Line_Pydantic])
async def get_schedule(date: datetime.date = Query(example='2022-10-05'),
                       teacher: str = Query(default=None),
                       classroom: str = Query(default=None),
                       group: str = Query(default=None)
                       ):
    filtes = {}
    if teacher is not None:
        filtes['teacher'] = teacher
    if classroom is not None:
        filtes['classroom'] = classroom
    if group is not None:
        filtes['group'] = group
    return await Line_Pydantic.from_queryset(Line.get_by_date(date=date)
                                             .filter(**filtes))


@router.get('/by_id/{id}', response_model=Line_Pydantic)
async def get_by_id(id: int):
    return await Line_Pydantic.from_queryset_single(Line.get(id=id))


@router.post("/create_non_periodic", response_model=Line_Pydantic)
async def create_schedule(line: LineIn_Pydantic):
    error = await check_time(Line.get_by_date(line.date).filter(classroom_id=line.classroom_id), line)
    if error is not None:
        return JSONResponse(status_code=422, content={'detail': error})
    l = await Line.create(**line.dict())

    await l.fetch_related('group', 'teacher', 'classroom')
    return Line_Pydantic.from_orm(l)


@router.post("/create_periodic", response_model=Line_Pydantic)
async def create_schedule(line: LinePeriodicIn_Pydantic):
    error = await check_time(Line.filter(classroom_id=line.classroom_id,
                                         weekday=line.weekday,
                                         week_type__in=(line.week_type, 0),
                                         period=1),
                             line)
    if error is not None:
        return JSONResponse(status_code=422, content={'detail': error})
    l = await Line.create(**line.dict())

    await l.fetch_related('group', 'teacher', 'classroom')
    return Line_Pydantic.from_orm(l)


@router.post('/{id}/specify_date')
async def specify(id: int, date: datetime.date = Query(example=datetime.date.fromisoformat('2022-10-05'))):
    line = await Line.get(id=id).prefetch_related()
    params = (Line_Pydantic.from_orm(line).dict() | dict(date=date, origin=line))
    params.pop('id')
    return Line_Pydantic.from_orm(await Line.create(**params))


@router.delete('/{id}')
async def delete_schedule(id: int):
    await Line.filter(id=id).delete()
