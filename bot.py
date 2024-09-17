import telebot
from telebot import types
from weather import my_weather
from m_schedule import _schedule
from generate_table import schedule_day_img
from io import BytesIO
import sqlite3
import schedule

# Токен для доступа к боту
telebot_token = "7182476955:AAE6eNJpU_Mj-cBmPf3JkmltvJqmXYDacSg"
bot = telebot.TeleBot(telebot_token)

# Подключение к базе данных
con = sqlite3.connect("new-bd.db", check_same_thread=False)
cursor = con.cursor()


# Функция для обновления бота и отправки сообщения пользователям
def update_bot():
    a = cursor.execute("""SELECT user_id FROM user_group""").fetchall()
    user_id_list = list(map(lambda x: x[0], a))
    # for id in user_id_list:
    #     bot.send_message(id, "Бот обновился!\nПожалуйста, напишите '/start'")



update_bot()


def daily_schedule():
    pass


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def url(message):
    # Создание клавиатуры с кнопками
    markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    weather_btn = types.KeyboardButton(text='🌤️Погода')
    schedule_btn = types.KeyboardButton(text='📆Расписание')
    group_btn = types.KeyboardButton(text='👥Изменить номер группы')
    markup_start.add(weather_btn, schedule_btn, group_btn)

    # Проверка, зарегистрирован ли пользователь
    info = cursor.execute('SELECT * FROM user_group WHERE user_id=?', (message.from_user.id,))
    if info.fetchone() is None:
        # Если пользователь не зарегистрирован, запросить номер группы
        bot.send_message(message.from_user.id,
                         "Привет!\nДля персонализированной помощи мне нужен номер твоей учебной группы в КАИ.\n"
                         "Пожалуйста, отправь мне свой номер группы, чтобы я мог предоставить тебе наилучшую поддержку и актуальную информацию.\n"
                         "Спасибо! 🎓", reply_markup=markup_start)
        bot.register_next_step_handler(message, get_num_group)
    else:
        bot.send_message(message.from_user.id, "И снова привет!")


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '🌤️Погода':
        weather = my_weather()
        bot.send_message(message.from_user.id, text=weather.formated_print())

    if message.text == '📆Расписание':
        days_keyboard = types.InlineKeyboardMarkup()
        pon_button = types.InlineKeyboardButton(text="Понедельник", callback_data="day_pon")
        vt_button = types.InlineKeyboardButton(text="Вторник", callback_data="day_vt")
        sr_button = types.InlineKeyboardButton(text="Среда", callback_data="day_sr")
        ch_button = types.InlineKeyboardButton(text="Чертверг", callback_data="day_ch")
        pt_button = types.InlineKeyboardButton(text="Пятница", callback_data="day_pt")
        sub_button = types.InlineKeyboardButton(text="Суббота", callback_data="day_sub")
        days_keyboard.add(pon_button, vt_button, sr_button, ch_button, pt_button, sub_button)

        if cursor.execute("""SELECT num_group FROM user_group where user_id = ?""",
                          (message.from_user.id,)).fetchone()[0] != "-":
            bot.send_message(message.from_user.id, "Выбери день недели", reply_markup=days_keyboard)
        else:
            bot.send_message(message.from_user.id, "Укажи номер группы")
            bot.register_next_step_handler(message, get_variable_num_group)
    if message.text == "👥Изменить номер группы":
        bot.send_message(message.from_user.id,
                         "🔄 Конечно! Если у тебя изменился номер учебной группы или есть необходимость его обновить, просто отправь мне новый номер группы")
        bot.register_next_step_handler(message, get_num_group)


# Обработчик ввода номера группы, если ранее он не был указан
def get_variable_num_group(message: types.Message):
    if _schedule(message.text).is_group_schedule():
        cursor.execute("""UPDATE user_group SET num_group = ? WHERE user_id = ?""",
                       (message.text, message.from_user.id))
        con.commit()
        days_keyboard = types.InlineKeyboardMarkup()
        pon_button = types.InlineKeyboardButton(text="Понедельник", callback_data="day_pon")
        vt_button = types.InlineKeyboardButton(text="Вторник", callback_data="day_vt")
        sr_button = types.InlineKeyboardButton(text="Среда", callback_data="day_sr")
        ch_button = types.InlineKeyboardButton(text="Чертверг", callback_data="day_ch")
        pt_button = types.InlineKeyboardButton(text="Пятница", callback_data="day_pt")
        sub_button = types.InlineKeyboardButton(text="Суббота", callback_data="day_sub")
        days_keyboard.add(pon_button, vt_button, sr_button, ch_button, pt_button, sub_button)

        bot.send_message(message.from_user.id, "Выбери день недели", reply_markup=days_keyboard)


# Обработчик ввода номера группы при регистрации
def get_num_group(message: types.Message):
    if message.text != "-":
        if not _schedule(message.text).get_groupid():
            bot.send_message(message.from_user.id,
                             "⚠️ Ой! Кажется, произошла ошибка. Пожалуйста, убедитесь, что введенный номер учебной группы корректен, и попробуйте еще раз.")
            bot.send_message(message.from_user.id,
                             '🤖 Если не хочешь указывать номер учебной группы прямо сейчас, не беспокойся! Просто напиши "-"')
            bot.register_next_step_handler(message, get_num_group)
        else:
            bot.send_message(message.from_user.id,
                             "🌟 Отлично! Спасибо за предоставленную информацию. Твоя учебная группа успешно записана.")

            info = cursor.execute('SELECT * FROM user_group WHERE user_id=?', (message.from_user.id,))
            if info.fetchone() is None:
                inf = (message.from_user.id, message.text, "stable")
                cursor.execute("INSERT INTO user_group (user_id, num_group, group_status) VALUES (?, ?, ?)", inf)
                con.commit()
            else:
                cursor.execute("""UPDATE user_group SET num_group = ? WHERE user_id = ?""",
                               (message.text, message.from_user.id))
                cursor.execute("""UPDATE user_group SET group_status = ? WHERE user_id = ?""",
                               ("stable", message.from_user.id))
                con.commit()
    else:
        bot.send_message(message.from_user.id,
                         "👌 Нет проблем! Если когда-то захочешь указать номер учебной группы или у тебя возникнут вопросы, не стесняйся обращаться.")
        info = cursor.execute('SELECT * FROM user_group WHERE user_id=?', (message.from_user.id,))
        if info.fetchone() is None:
            inf = (message.from_user.id, message.text, "variable")
            cursor.execute("INSERT INTO user_group (user_id, num_group, group_status) VALUES (?, ?, ?)", inf)
            con.commit()
        else:
            cursor.execute("""UPDATE user_group SET num_group = ? WHERE user_id = ?""",
                           (message.text, message.from_user.id))
            cursor.execute("""UPDATE user_group SET group_status = ? WHERE user_id = ?""",
                           ("variable", message.from_user.id))
            con.commit()


# Обработчик inline-кнопок для выбора дня недели
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data in ["day_pon", "day_vt", "day_sr", "day_ch", "day_pt", "day_sub"]:
            group = (cursor.execute("""SELECT num_group FROM user_group where user_id = ?""",
                                    (call.from_user.id,)).fetchone())[0]
            print(group)
            if _schedule(group).is_group_schedule():
                days = {"day_pon": 1, "day_vt": 2, "day_sr": 3, "day_ch": 4, "day_pt": 5, "day_sub": 6}
                day = days[call.data]
                table = schedule_day_img(day=day, group=group)
                img = table.create_table_schedule()
                bio = BytesIO()
                bio.name = 'image.jpeg'
                img.save(bio, 'JPEG')
                bio.seek(0)
                bot.send_photo(call.message.chat.id, photo=bio)
                if (cursor.execute("""SELECT group_status FROM user_group where user_id = ?""",
                                   (call.from_user.id,)).fetchone())[0] == "variable":
                    cursor.execute("""UPDATE user_group SET num_group = ? WHERE user_id = ?""",
                                   ("-", call.from_user.id))
                    con.commit()
            else:
                bot.send_message(call.from_user.id, "Занятий нет")

    elif call.inline_message_id:
        if call.data == "test":
            bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")


# Вспомогательная функция для отображения таблицы расписания без изменения БД
def call_table_without_bd(call, group):
    if call.message:
        if call.data in ["day_pon", "day_vt", "day_sr", "day_ch", "day_pt", "day_sub"]:
            days = {"day_pon": 1, "day_vt": 2, "day_sr": 3, "day_ch": 4, "day_pt": 5, "day_sub": 6}
            day = days[call.data]
            table = schedule_day_img(day=day, group=group)
            img = table.create_table_schedule()
            bio = BytesIO()
            bio.name = 'image.jpeg'
            img.save(bio, 'JPEG')
            bio.seek(0)
            bot.send_photo(call.message.chat.id, photo=bio)


# Запуск бота
bot.polling(none_stop=True, interval=0)
