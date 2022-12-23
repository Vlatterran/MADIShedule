import asyncio
import datetime
import enum

import dpath.options
from dpath.util import values
from tortoise import fields, Tortoise
from tortoise.expressions import Q
from tortoise.fields import ReverseRelation
from tortoise.models import Model
from tortoise.queryset import QuerySet

from ..utils import is_week_even

dpath.options.ALLOW_EMPTY_STRING_KEYS = True


class Model(Model):
    @property
    @classmethod
    def fields(cls):
        return set(values(cls.describe(), '/**/name', afilter=lambda x: isinstance(x, str) and '.' not in x))


class Frequency(enum.IntEnum):
    """
    1 - repeats once a WeekType
    2 - repeats once a month
    """
    WEEK = 1
    MONTH = 2


class WeekType(enum.IntEnum):
    """
    0 - Every week
    1 - Odd week
    2 - #ven week
    """
    EVERY = 0
    ODD = 1
    EVEN = 2


class LectureType(enum.Enum):
    LECTURE = 'лекции'
    PRACTICE = 'практические занятия /семинар/'
    LAB = 'лабораторные занятия'
    EXAM = 'экзамен'
    CONSULT = 'консультация'


class Group(Model):
    name = fields.CharField(max_length=10, pk=True)
    lines: ReverseRelation['Line']

    def __str__(self):
        return self.name


class Teacher(Model):
    name = fields.CharField(max_length=20, pk=True)
    lines: ReverseRelation['Line']

    def __str__(self):
        return self.name


class Classroom(Model):
    name = fields.CharField(max_length=5, pk=True)
    lines: ReverseRelation['Line']

    def __str__(self):
        return self.name


class Weekday(enum.IntEnum):
    MONDAY = 0
    TUESDAY = 1
    Wednesday = 2
    Thursday = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Line(Model):
    name: str = fields.TextField(null=True)
    start_time: datetime.time = fields.TimeField()
    end_time: datetime.time = fields.TimeField()
    type: LectureType = fields.CharEnumField(LectureType)
    teacher = fields.ForeignKeyField('model.Teacher', null=True)
    group = fields.ForeignKeyField('model.Group')
    classroom = fields.ForeignKeyField('model.Classroom')

    date: datetime.date = fields.DateField(null=True)

    origin_line = fields.ForeignKeyField('model.Line', null=True)

    week_type: WeekType = fields.IntEnumField(WeekType, null=True)
    weekday: Weekday = fields.IntEnumField(Weekday, null=True)
    period: Frequency = fields.IntEnumField(Frequency, null=True)

    def __str__(self):
        return f'{self.name} {self.start_time}-{self.end_time} {self.group}' \
               f' {self.teacher} {self.classroom} {self.date} {self.period}'

    @classmethod
    def get_by_date(cls, date: datetime.date) -> QuerySet['Line']:
        return Line.filter(Q(date=date) |
                           (Q(weekday=date.weekday()) &
                            Q(week_type__in=[0, 1 + is_week_even(date.timetuple())]) &
                            Q(period=1)))

    class Meta:
        unique_together = (
            ('start_time', 'end_time', 'classroom', 'date'),
        )


async def init():
    # Here we create a SQLite DB using file "models.sqlite3"
    #  also specify the backend name of "models"
    #  which contain models from "backend.models"
    await Tortoise.init(
        db_url='sqlite://models.sqlite3',
        modules={'model': ['__main__']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()
    await Classroom.create(name='605л')


if __name__ == '__main__':
    asyncio.run(init())
