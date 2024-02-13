import sqlite3
from location import analyze_location
import datetime
import telebot
async def cleaning_chat(bot, message, n):
    for num in range(message.id, message.id-n, -1):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=num)
        except:
            pass
async def send_data(bot, id, rows, admin=False, user_history=False):
    if user_history is False and admin is False:
        for row in rows:

            image = row[2]
            latitude = row[3]
            longitude = row[4]
            time_ = row[6]
            street_name = analyze_location(latitude, longitude)
            time = datetime.datetime.strptime(time_, "%Y-%m-%d %H:%M:%S")
            readable_time = time.strftime("%d %B %Y %H:%M")
            button = telebot.types.InlineKeyboardButton(text="Взяти в обробку", callback_data=f"Taken|{time_}")
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(button)

            photo_mesage = await bot.send_photo(chat_id=id, photo=image, caption=f"Місце порушення - {street_name}\n"
                                                                                                   f"Дата і час - {readable_time}")
            await bot.send_location(chat_id=id, latitude=latitude, longitude=longitude, reply_to_message_id=photo_mesage.message_id, reply_markup=keyboard)
    if user_history is True:
        if rows == []:
            await bot.send_message(chat_id=id, text="Ви ще не зафіксуали жодного порушення")
            return
        for row in rows:


            image = row[2]
            latitude = row[3]
            longitude = row[4]
            time = row[6]
            street_name = analyze_location(latitude, longitude)
            status = row[5]
            if status == "In progress":
                status = "Інспектор взяв в обробку ваш запит"
            elif status == "Unvalidated":
                status = "Ваш запит обробляється системою"
            elif status == "Declined":
                status = "Ваш запит не підійшов, можливо ви не дотримались інструкції звітування порушення"
            elif status == "Validated":
                status = "Ваш запит пройшов обробку в системі, очікуємо інспектора для підтвердження"
            elif status == "Fined":
                status = "Водія ТЗ оштрафовано!"
            time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            readable_time = time.strftime("%d %B %Y %H:%M")
            photo_mesage = await bot.send_photo(chat_id=id, photo=image, caption=f"Місце порушення - {street_name}\n"
                                                                                                   f"Дата і час - {readable_time}\n"
                                                                                 f"Статус заявки - {status}")
    if admin is True:
        for row in rows:
            image_id = row[1]
            image = row[2]
            latitude = row[3]
            longitude = row[4]
            time_ = row[6]
            street_name = analyze_location(latitude, longitude)
            time = datetime.datetime.strptime(time_, "%Y-%m-%d %H:%M:%S")
            readable_time = time.strftime("%d %B %Y %H:%M")
            button1 =telebot.types.InlineKeyboardButton(text="Підтвердити", callback_data=f"True|{time_}")
            button2 = telebot.types.InlineKeyboardButton(text="Видалити", callback_data=f"False|{time_}")
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(button1).add(button2)

            await bot.send_photo(chat_id=id, photo=image, caption=f"Місце порушення - {street_name}\n"
                                                                                 f"Дата і час - {readable_time}", reply_markup=keyboard)



async def get_data_from_bigdb(id=None, date=None, bot=None, admin=False, user_history=False, automate=False):
    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()
    if date is not None:
        try:
            date = datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
            cursor.execute('SELECT * FROM reports WHERE timestamp = ?', (date,))
            rows = cursor.fetchall()
            return rows[0][0]
        except sqlite3.Error as e:
            print("SQLite error:", e)

    if user_history is True:
        cursor.execute('SELECT * FROM reports WHERE user_id = ?',(id,))
    elif admin is True:
        cursor.execute('SELECT * FROM reports WHERE status = ?', ("Unvalidated",))
    if admin is False and user_history is False:
        cursor.execute('SELECT * FROM reports WHERE status = ?', ("Validated",))

    rows = cursor.fetchall()
    conn.close()
    if automate is False:
        return rows
    elif automate is True:
        await send_data(bot, id, rows, admin, user_history)
