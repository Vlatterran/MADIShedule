import asyncio
import json
from pprint import pprint

import httpx
from bs4 import BeautifulSoup


class Schedule:
    dec_ru = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье',
        -1: 'Полнодневные занятия'
    }
    ru_dec = {
        'Понедельник': 0,
        'Вторник': 1,
        'Среда': 2,
        'Четверг': 3,
        'Пятница': 4,
        'Суббота': 5,
        'Воскресенье': 6
    }
    shortens = {
        'Числ': 'Числитель',
        'Знам': 'Знаменатель',
        'Еж': 'Еженедельно',
    }
    week_type = {
        'Числитель': 1,
        'Знаменатель': 2,
        'Еженедельно': 0,
    }


local_url = 'http://localhost:8008'


async def main():
    async with httpx.AsyncClient() as client:
        weekday = None
        teacher = None
        schedule = []
        response = await client.post('https://www.madi.ru/tplan/tasks/tableFiller.php',
                                     headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                     data=dict(tab=11, kf_id=61,
                                               kf_name='Автоматизированных систем управления',
                                               sort=1, tp_year=22, sem_no=1))
        soup = BeautifulSoup(response.text, features='lxml')
        raws = iter(soup.select('.timetable tr'))
        teachers = []
        groups = set()
        classrooms = set()
        for raw in raws:
            children = [*raw.findChildren(('td', 'th'))]
            if len(children) == 1:
                if children[0].has_attr('class'):
                    teacher = ' '.join(children[0].text.split())
                    teachers.append(teacher)
                else:
                    weekday = raw.text
                    next(raws)
            else:
                line = {'teacher_id': teacher, 'weekday': Schedule.ru_dec[weekday]}
                for i, text in enumerate(filter(lambda x: x != '',
                                                map(lambda x: x.text.strip().strip('\n'),
                                                    raw.children))):
                    # print(i, text)
                    if i == 0:
                        line['start'], line['end'] = text.split(' - ')
                    elif i == 1:
                        if '.' in text:
                            line['week_type'] = Schedule.week_type[Schedule.shortens[text.split('.')[0]]]
                            line['period'] = 2
                        else:
                            line['week_type'] = Schedule.week_type[text]
                            line['period'] = 1
                    elif i == 2:
                        line['classroom_id'] = text
                        classrooms.add(text)
                    elif i == 3:
                        line['group_id'] = text
                        groups.add(text)
                    elif i == 4:
                        line['name'] = text
                    elif i == 5:
                        line['type'] = text.lower()
                schedule.append(line)
        tasks = [client.post(f'{local_url}/teachers/{i}') for i in teachers]
        tasks += [client.post(f'{local_url}/classrooms/{i}') for i in classrooms]
        tasks += [client.post(f'{local_url}/groups/{i}') for i in groups]
        await asyncio.gather(*tasks)
        tasks = [client.post(f'{local_url}/schedule/create_periodic', json=i) for i in schedule]
        responses = await asyncio.gather(*tasks)
        for resp in filter(lambda x: x.status_code != 200, responses):
            pprint(json.loads(resp.request.content))
            pprint(resp.json())
    return schedule


asyncio.run(main())
