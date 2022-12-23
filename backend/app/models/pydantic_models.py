import datetime

from tortoise.contrib.pydantic.base import PydanticModel

from .tortoise_models import LectureType, Frequency, WeekType, Weekday, Classroom, Line, Group, Teacher


class Line_Pydantic(PydanticModel):
    """
    Schema of schedule line
    """
    id: int
    name: str | None
    date: datetime.date | None
    start_time: datetime.time
    end_time: datetime.time
    teacher_id: str | None
    group_id: str
    classroom_id: str
    week_type: WeekType | None
    weekday: Weekday | None
    period: Frequency | None
    type: LectureType

    class Config:
        title = 'Line'
        orig_model = Line
        schema_extra = {
            'example': {
                "id": 121,
                "name": "Информатика",
                "date": None,
                "start_time": "15:35:00+00:00",
                "end_time": "17:05:00+00:00",
                "teacher_id": "Голубкова В.Б.",
                "group_id": "1бАСУ2",
                "classroom_id": "617л",
                "week_type": 1,
                "period": 1,
                "type": "практические занятия /семинар/"
            },
            'examples': [
                {"id": 121,
                 "name": "Информатика",
                 "date": datetime.date.today(),
                 "start_time": "15:35:00+00:00",
                 "end_time": "17:05:00+00:00",
                 "teacher_id": "Голубкова В.Б.",
                 "group_id": "1бАСУ2",
                 "classroom_id": "617л",
                 "week_type": None,
                 'weekday': None,
                 "period": None,
                 "type": "практические занятия /семинар/"}
            ]
        }


class LineIn_Pydantic(PydanticModel):
    """
    Schema of incoming schedule line that doesn't repeat
    """
    name: str | None
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    teacher_id: str | None
    group_id: str
    classroom_id: str
    type: LectureType

    class Config:
        title = 'LineIn'
        orig_model = Line
        schema_extra = {
            'example':
                {
                    'name': 'IT',
                    'start_time': '10:00',
                    'end_time': '11:30',
                    'date': '2022-10-05',
                    'type': 'лекции',
                    'classroom_id': '605л',
                    'group_id': '3ВбИТС',
                    'teacher_id': 'Сальный А.Г.',
                }

        }


class LinePeriodicIn_Pydantic(PydanticModel):
    """
    Schema of incoming schedule line that repeats
    """
    name: str | None
    start_time: datetime.time
    end_time: datetime.time
    teacher_id: str | None
    group_id: str
    classroom_id: str
    week_type: WeekType
    weekday: Weekday
    period: Frequency
    type: LectureType

    class Config:
        title = 'LineIn'
        orig_model = Line

        schema_extra = {
            'example':
                {
                    'name': 'IT',
                    'start_time': '10:00',
                    'end_time': '11:30',
                    'week_type': 0,
                    'weekday': 1,
                    'period': 1,
                    'type': 'лекции',
                    'classroom_id': '605л',
                    'group_id': '3ВбИТС',
                    'teacher_id': 'Сальный А.Г.'
                }
        }


class Group_Pydantic(PydanticModel):
    """
    Schema of group
    """
    name: str
    lines: list[Line_Pydantic]

    class Config:
        title = 'Group'
        orig_model = Group


class Teacher_Pydantic(PydanticModel):
    """
    Schema of teacher
    """
    name: str
    lines: list[Line_Pydantic]

    class Config:
        title = 'Teacher'
        orig_model = Teacher


class Classroom_Pydantic(PydanticModel):
    """
    Schema of classroom
    """
    name: str
    lines: list[Line_Pydantic]

    class Config:
        title = 'Classroom'
        orig_model = Classroom
