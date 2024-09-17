from PIL import Image, ImageDraw, ImageFont
import textwrap
from m_schedule import _schedule


class schedule_day_img:
    def __init__(self, day=1, group="3239", my_schedule=[]):
        self.schedule_ = _schedule(group)
        if not my_schedule:
            self.my_schedule = self.schedule_.convert_schedule_by_day(day)
        else:
            self.my_schedule = my_schedule

    def get_size(self, text,
                 font=ImageFont.truetype("assets/Inter/Inter-Regular.ttf", 14)):  # возвращает размера текста в пикселях
        left, top, right, bottom = font.getbbox(f"{text}")
        width = right - left
        height = bottom - top
        return list(map(lambda x: x + 20, [width, 20]))

    def get_line_break(self, text, syms):  # функция переноса строки
        r = ""
        for line in textwrap.wrap(text, width=syms):
            r += line + "\n"
        return r

    def get_vid(self, text):
        d = {"лек": "Лекция", "л.р.": "Лабораторная работа", "пр": "Практика"}
        return d[text]

    def create_cell(self, _class):  # генерация блока фото одной пары
        cell = Image.new('RGB', (1100, 300), (21, 38, 52))
        draw = ImageDraw.Draw(cell)

        font = ImageFont.truetype("assets/Inter/Inter-Regular.ttf", size=94)
        text_time = _class["Время"]
        textsize = draw.textbbox((0, 0), text_time, font=font)
        textarea = (240, 70)
        draw.text((40 + (textarea[0] - textsize[2]) / 2, 70 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_time, (0, 135, 200), font=font, align='center', anchor='lt')

        font = ImageFont.truetype("assets/Inter/Inter-Regular.ttf", size=34)
        text_bild = f"Здание: {_class['Здание']}"
        if "ОЛИМП" in text_bild:
            text_bild = "Здание: ОЛИМП"
        text_bild = text_bild
        textsize = draw.textbbox((0, 0), text_bild, font=font)
        textarea = (175, 35)
        draw.text((70 + (textarea[0] - textsize[2]) / 2, 165 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_bild, (240, 240, 240), font=font, align='center', anchor='lt')

        text_aud = f"Ауд: {_class['Аудитория']}"
        if "ОЛИМП" in text_aud:
            text_aud = "-----"
        text_aud = text_aud
        textsize = draw.textbbox((0, 0), text_aud, font=font)
        textarea = (137, 35)
        draw.text((90 + (textarea[0] - textsize[2]) / 2, 205 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_aud, (240, 240, 240), font=font, align='center', anchor='lt')

        font = ImageFont.truetype("assets/Inter/Inter-Regular.ttf", size=36)
        text_discip = f"{_class['Дисциплина']}"
        text_discip = self.get_line_break(text_discip, 33)
        textsize = draw.textbbox((0, 0), text_discip, font=font)
        textarea = (670, 85)
        draw.text((345, 45 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_discip, (0, 135, 200), font=font, align='left')

        font = ImageFont.truetype("assets/Inter/Inter-Bold.ttf", size=36)
        text_vid = f"{_class['Вид занятия']}"
        text_vid = self.get_vid(text_vid)
        textsize = draw.textbbox((0, 0), text_vid, font=font)
        textarea = (695, 35)
        draw.text((345, 145 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_vid, (240, 240, 240), font=font, align='left', anchor='lt')

        font = ImageFont.truetype("assets/Inter/Inter-Bold.ttf", size=34)
        text_prepod = f"{_class['Преподаватель']}"
        textsize = draw.textbbox((0, 0), text_prepod, font=font)
        textarea = (695, 35)
        draw.text((345, 185 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_prepod, (240, 240, 240), font=font, align='left', anchor='lt')

        font = ImageFont.truetype("assets/Inter/Inter-Regular.ttf", size=36)
        text_date = f"{_class['Дата']}"
        if len(text_date) > 30:
            font = ImageFont.truetype("assets/Inter/Inter-Regular.ttf", size=24)
        textsize = draw.textbbox((0, 0), text_date, font=font)
        textarea = (695, 35)
        draw.text((345, 225 + (textarea[1] - textsize[3] + textsize[1]) / 2),
                  text_date, (0, 135, 200), font=font, align='left', anchor='lt')

        cell.save("test_cell.png")
        return cell

    def create_table_schedule(self):  # формирует фото расписания из блоков фото
        table_size = [1120, len(self.my_schedule) * 330]
        table = Image.new('RGB', table_size, (14, 26, 38))
        k = 0
        for _class in self.my_schedule:
            cell = self.create_cell(_class)
            table.paste(cell, (10, 15 + k * 330))
            k += 1
        return table


if __name__ == "__main__":
    sch = _schedule().get_schedule_today()
    table = schedule_day_img(day=1, group=3238, my_schedule=sch)
    table.create_table_schedule().show()
