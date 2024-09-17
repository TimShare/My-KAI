import requests
import json
from tabulate import tabulate
from datetime import datetime


class _schedule:

    def __init__(self, group="3239"):
        self.group = group
        self.url_group = f"https://kai.ru/raspisanie?p_p_id=pubStudentSchedule_WAR_publicStudentSchedule10&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getGroupsURL&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1&query={self.group}"
        self.url_rasp = "https://kai.ru/raspisanie?p_p_id=pubStudentSchedule_WAR_publicStudentSchedule10&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=schedule&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1"
        self.days_in_week = {1: "Понедельник", 2: "Вторник", 3: "Среда", 4: "Четверг", 5: "Пятница", 6: "Суббота",
                             7: "Воскресенье"}
        self.days_in_week_num = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5, "Суббота": 6,
                                 "Воскресенье": 7}

    def get_groupid(self):  # получаем id группы с сервера kai
        return requests.get(self.url_group).json()

    def get_schedule(self):  # получаем расписание с сервера kai
        return requests.post(self.url_rasp, params=self.from_r_group_to_rasp()).json()

    def from_r_group_to_rasp(self):  # получаем расписание с сервера kai
        r_group = self.get_groupid()
        return {"groupId": r_group[0]["id"], "programForm": r_group[0]["forma"]}

    def unzip_schedule(self):  # распаковывываем расписание
        schedule = self.get_schedule()
        res = ""
        rasp = [["Время", "Дата", "Дисциплина", "Вид занятия", "Аудитория", "Здание", "Преподаватель", "Кафедра"]]
        for i in [1, 2, 3, 4, 5, 6]:
            res += f"{self.days_in_week[i]}\n"
            for _class in schedule[f"{i}"]:
                rasp.append([_class["dayTime"], _class["dayDate"], _class["disciplName"], _class["disciplType"],
                             _class["audNum"],
                             _class["buildNum"], _class["prepodName"], _class["orgUnitName"]])
            res += str(tabulate(rasp)) + "\n"
            rasp = [["Время", "Дата", "Дисциплина", "Вид занятия", "Аудитория", "Здание", "Преподаватель", "Кафедра"]]
        return res

    def unzip_schedule_by_day(self, day="Понедельник"): # распаковывываем расписание в определенный день
        schedule = self.get_schedule()
        rasp = [["Время", "Дата", "Дисциплина", "Вид занятия", "Аудитория", "Здание", "Преподаватель", "Кафедра"]]
        for _class in schedule[f'{self.days_in_week_num[day]}']:
            rasp.append([_class["dayTime"], _class["dayDate"], _class["disciplName"], _class["disciplType"],
                         _class["audNum"],
                         _class["buildNum"], _class["prepodName"], _class["orgUnitName"]])
        return tabulate(rasp)

    def convert_schedule(self): # конвертируем расписание в свой формат
        schedule = self.get_schedule()
        converted_schedule = {}
        for i in [1, 2, 3, 4, 5, 6]:
            converted_schedule[self.days_in_week[i]] = []
            for _class in schedule[f"{i}"]:
                converted_schedule[self.days_in_week[i]].append(
                    {"Время": " ".join(_class["dayTime"].split()), "Дата": " ".join(_class["dayDate"].split()),
                     "Дисциплина": " ".join(_class["disciplName"].split()),
                     "Вид занятия": " ".join(_class["disciplType"].split()),
                     "Аудитория": " ".join(_class["audNum"].split()), "Здание": " ".join(_class["buildNum"].split()),
                     "Преподаватель": " ".join(_class["prepodName"].split()),
                     "Кафедра": " ".join(_class["orgUnitName"].split())})
        return converted_schedule

    def convert_schedule_by_day(self, day=1): # конвертируем расписание в свой формат в определенный день
        return self.convert_schedule()[self.days_in_week[day]]

    def from_dict_to_list(self, _dict):
        sch = []
        for day in _dict:
            a = [["Время", "Дата", "Дисциплина", "Вид занятия", "Аудитория", "Здание", "Преподаватель", "Кафедра"]]
            for _class in _dict[day]:
                a.append([_class["Время"], _class["Дата"], _class["Дисциплина"], _class["Вид занятия"],
                          _class["Аудитория"],
                          _class["Здание"], _class["Преподаватель"], _class["Кафедра"]])
            sch.append(a)
        return sch

    def from_dict_to_list_day(self, _dict, day):
        a = [["Время", "Дата", "Дисциплина", "Вид занятия", "Аудитория", "Здание", "Преподаватель", "Кафедра"]]
        for _class in _dict[day]:
            a.append([_class["Время"], _class["Дата"], _class["Дисциплина"], _class["Вид занятия"],
                      _class["Аудитория"],
                      _class["Здание"], _class["Преподаватель"], _class["Кафедра"]])
        return a

    def formated_json(self, _json): # форматированный вывод в json формате
        return json.dumps(_json, indent=4, ensure_ascii=False)

    def is_group_schedule(self):
        return True if self.get_groupid() and self.get_schedule() else False

    def get_date(self):
        now = datetime.now()  # текущие дата и время
        return datetime.isoweekday(now)

    def get_week_num(self):
        week_number = datetime.today().isocalendar()[1]
        return ["чет", "неч"][week_number % 2]

    def get_schedule_today(self): # возвращает расписание в сегодняшний день
        schedule_day = []
        day = self.get_date()
        week_number = self.get_week_num()
        schedule = self.convert_schedule_by_day(day)
        for _class in schedule:
            if week_number in _class["Дата"] or _class["Дата"] == "":
                schedule_day.append(_class)
        return schedule_day


if __name__ == "__main__":
    sch = _schedule(6103)
    print(sch.is_group_schedule())