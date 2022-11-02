import asyncio
import logging
import re

import httpx as httpx
from bs4 import BeautifulSoup


class Schedule:
    def __init__(self, onedrive_url):
        self.onedrive_url = onedrive_url
        self.schedule = {}

    dec_ru = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье',
        # -1: 'Полнодневные занятия'
    }
    ru_dec = {
        'Понедельник': 0,
        'Вторник': 1,
        'Среда': 2,
        'Четверг': 3,
        'Пятница': 4,
        'Суббота': 5,
        'Воскресенье': 6,
        # 'Полнодневные занятия': -1
    }
    shortens = {
        'Числ': 'Числитель',
        'Знам': 'Знаменатель',
        'Еж': 'Еженедельно',
    }

    @classmethod
    async def parse(cls, group: str = ''):
        async with httpx.AsyncClient() as client:
            soup = BeautifulSoup((await client.post('https://www.madi.ru/tplan/tasks/task3,7_fastview.php',
                                                    data={'step_no': 1, 'task_id': 7}
                                                    )).text,
                                 features='lxml')
            _groups = dict(map(lambda x: (x.attrs['value'], x.text),
                               soup.select('ul>li')))

            schedule = {}
            tasks = []
            for group_id, group_name in filter(lambda kv: group == '' or (kv[1].lower() == group.lower()),
                                               _groups.items()):
                tasks.append(asyncio.create_task(cls.parse_group(group_name, group_id, schedule, client)))
            await asyncio.gather(*tasks, return_exceptions=True)
        return schedule

    @classmethod
    async def parse_group(cls,
                          group_name: str,
                          group_id: str,
                          schedule: dict,
                          client: httpx.AsyncClient):
        weekday = None
        response = await client.post('https://www.madi.ru/tplan/tasks/tableFiller.php',
                                     data={'tab': 7, 'gp_name': group_name, 'gp_id': group_id})
        soup = BeautifulSoup(response.text, features='lxml')
        raws = iter(soup.select('.timetable tr'))
        for raw in raws:
            children = [*raw.findChildren(('td', 'th'))]
            if len(children) == 1:
                weekday = raw.text
                if weekday in Schedule.ru_dec:
                    next(raws)
            else:
                context: dict[str, str] = {'weekday': weekday, 'group': group_name}
                line = {}
                if weekday not in Schedule.ru_dec:
                    for i, cell in enumerate(children):
                        match i:
                            case 0:
                                context['weekday'] = cell.text
                            case 1:
                                line['Наименование дисциплины'] = cell.text
                            case 2:
                                context['frequency'] = cell.text
                else:
                    for i, cell in enumerate(children):
                        match i:
                            case 0:
                                line['Время занятий'] = cell.text
                            case 1:
                                line['Наименование дисциплины'] = cell.text
                            case 2:
                                line['Вид занятий'] = cell.text
                            case 3:
                                context['frequency'] = cell.text
                            case 4:
                                line['Аудитория'] = cell.text
                            case 5:
                                if cell.text == '':
                                    t = '--'
                                else:
                                    t = cell.text
                                line['Преподаватель'] = re.sub(r'\s{2,}', ' ', t)
                try:
                    day = schedule.setdefault(group_name, {}).setdefault(context['weekday'], {})

                    if '.' in context['frequency']:
                        f = context['frequency'].split('.')
                        context['frequency'] = cls.shortens[f[0]]
                        line['Частота'] = f[1].strip()

                    day.setdefault(context['frequency'], []).append(line)
                except Exception as e:
                    logging.exception(e)
                    continue
