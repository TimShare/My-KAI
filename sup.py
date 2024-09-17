import sqlite3

con = sqlite3.connect("new-bd.db")
cursor = con.cursor()

# создаем таблицу user_group
cursor.execute("""CREATE TABLE user_group
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT,  
                num_group TEXT,
                group_status TEXT)
               """)


# def update_bot():
#     a = cursor.execute("""SELECT user_id FROM user_group""").fetchall()
#     return list(map(lambda x: x[0], a))



