from telebot import asyncio_filters
import telebot
from telebot import async_telebot
import asyncio
import sqlite3
from quart import Quart
import requests
import json
import locale
import datetime
import pytz


from universal_functions import get_data_from_bigdb
from data_handling import change_status

from api_data import admin_bot_token as TOKEN, admin_chat_id


bot = async_telebot.AsyncTeleBot(TOKEN)

app = Quart(__name__)

loop = asyncio.get_event_loop()

locale.setlocale(locale.LC_TIME, 'uk_UA')
date_format = locale.nl_langinfo(locale.D_FMT)
time_zone = pytz.timezone('Europe/Kiev')

@app.route('/new_data', methods=['POST'])
async def get_webhook():
    await get_data_from_bigdb(id=admin_chat_id, bot=bot, admin=True, automate=True)
    return "Success", 200

@bot.message_handler(commands=['start'])
async def fer(message):
    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()
    await bot.send_message(chat_id=admin_chat_id, text="Новий інспектор підключився")
    # Create a table to store user data
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS inspectors (
               user_id INTEGER PRIMARY KEY
           )
       ''')
    conn.commit()
    try:
        cursor.execute('''
            INSERT INTO inspectors (user_id) VALUES (?)
        ''', (message.chat.id,))
    except:
        pass

    conn.commit()
    conn.close()



@bot.callback_query_handler(func=lambda call: call.data.startswith('True'))
async def get_new(call):
    date = call.data.split('|')[1]
    change_status("Validated", date, photo=False)


    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM inspectors')
    rows = cursor.fetchall()
    conn.close()


    for user_id in rows:
        await get_data_from_bigdb(id=user_id[0], bot=bot, automate=True)
    change_status("Sent", date, photo=False)
    try:
        await bot.delete_message(chat_id=admin_chat_id, message_id=call.message.id)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('False'))
async def get_new(call):
    date = call.data.split('|')[1]
    change_status("Declined", date, photo=False)
    await bot.delete_message(chat_id=admin_chat_id, message_id=call.message.id)

    date = call.data.split('|')[1]
    js_date = {'date': f'{date}'}
    requests.post('http://127.0.0.1:5002/non_valid', data=json.dumps(js_date),
                  headers={'Content-Type': 'application/json'})


@bot.callback_query_handler(func=lambda call: call.data.startswith('Taken'))
async def get_new(call):
    # time_when_taken = datetime.datetime.now()
    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM inspectors')
    rows = cursor.fetchall()
    conn.close()
    message_count_num = []

    for user_id in rows:
        if call.message.chat.id != user_id[0]:
            deleting_message = await bot.send_message(chat_id=user_id[0], text="Видалення")
            last_message_for_inspectors = None
            i = 1
            while True:
                try:
                    last_message_for_inspectors = await bot.forward_message(admin_chat_id, user_id[0], deleting_message.message_id - i)
                    break
                except:
                    try:
                        await bot.delete_message(admin_chat_id, deleting_message.message_id - i)
                    except:
                        pass
                    i += 1


            count = len(rows) * 5 - 1

            while count >= 0:
                count -= 1
                if (time_zone.localize(datetime.datetime.utcfromtimestamp(last_message_for_inspectors.date)) - datetime.timedelta(
                    seconds=30)) <= time_zone.localize(datetime.datetime.utcfromtimestamp(deleting_message.date)) <= (time_zone.localize(
                        datetime.datetime.utcfromtimestamp(last_message_for_inspectors.date)) + datetime.timedelta(
                    seconds=30)) and deleting_message.chat.id == user_id[0]:
                    try:
                        await bot.delete_message(chat_id=user_id[0], message_id=deleting_message.message_id - count)
                    except:
                        pass
                else:
                    pass
        else:
            pass

        #видалення time >= повідомлення прийшло інспекторам-30сек and <= повідомлення прийшло інспекторам+30

# for i in range(5):

                # await bot.delete_message(chat_id=user_id[0], message_id=chat_to_delete.message_id - i)

            # chat_to_delete = await bot.send_message(chat_id=user_id[0], text="Видалення")
            #
            # # await bot.send_message(admin_chat_id, text=f"{chat_to_delete.message_id}")
            # # await bot.forward_message(admin_chat_id, user_id[0], chat_to_delete.message_id)
            # await bot.delete_message(chat_id=user_id[0], message_id=chat_to_delete.message_id, timeout=300)
            #
            # # await bot.send_message(admin_chat_id, text=f"{chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2 - 1)}")
            # # await bot.forward_message(admin_chat_id, user_id[0],chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2 - 1))
            # await bot.delete_message(chat_id=user_id[0], timeout=300,
            #                              message_id=(chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2 - 1)))
            #
            # # await bot.send_message(admin_chat_id, text=f"{chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2)}")
            # # await bot.forward_message(admin_chat_id, user_id[0], chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2))
            # await bot.delete_message(chat_id=user_id[0], timeout=300,
            #                              message_id=(chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2)))






    date = call.data.split('|')[1]
    change_status("In progress", date, photo=False)
    button1 = telebot.types.InlineKeyboardButton(text="Оштрафувати", callback_data=f"Fined|{date}")
    button2 = telebot.types.InlineKeyboardButton(text="Відхилити", callback_data=f"Declined|{date}")
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(button1).add(button2)
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, inline_message_id=call, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('Fined'))
async def get_new(call):
    date = call.data.split('|')[1]
    js_date = {'date': f'{date}'}
    requests.post('http://127.0.0.1:5002/approven', data=json.dumps(js_date), headers={'Content-Type': 'application/json'})


    change_status("Fined", date, photo=False)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    button = telebot.types.InlineKeyboardButton(url="https://www.buymeacoffee.com/Finerbot", text="Подяка")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button)
    await bot.edit_message_caption(caption="Дякуємо що скористались нашим ботом, ми повідомимо відправника про успішність його заявки\n"
                                           "Будемо вдячні за вашу підтримку", chat_id=call.message.chat.id, message_id=call.message.id-1, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Declined'))
async def get_new(call):
    date = call.data.split('|')[1]
    change_status("Declined", date, photo=False)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    button = telebot.types.InlineKeyboardButton(url="https://www.buymeacoffee.com/Finerbot", text="Подяка")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button)
    await bot.edit_message_caption(
        caption="Дякуємо що скористались нашим ботом, ми повідомимо відправника про успішність його заявки\n"
                "Будемо вдячні за вашу підтримку", chat_id=call.message.chat.id, message_id=call.message.id - 1,
        reply_markup=keyboard)
#
# @bot.message_handler(commands=['start'])
# async def start(message):
#     inline_button = telebot.types.InlineKeyboardButton(text="Отримати нові порушення", callback_data="/get_new")
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     keyboard.add(inline_button)
#
#     await bot.send_message(chat_id=message.chat.id, text="В цей бот ви можете отримувати порушення і їхнє місцезнаходження", reply_markup=keyboard)
#
#
# @bot.callback_query_handler(func=lambda call: True)
# async def get_new(message):
#     if message.data == "/get_new":
#         await cleaning_chat(bot, message.data.id,10)
#         await get_data_from_bigdb(id=message.from_user.id, bot=bot, automate=True)
#
#     else:
#         raise Exception("Smth went wrong in get_new() inspector_side.py")



bot.add_custom_filter(telebot.asyncio_filters.TextMatchFilter())

# asyncio.run(bot.polling(non_stop=True))
#
asyncio.ensure_future(bot.polling(non_stop=True))
asyncio.ensure_future(app.run(host="127.0.0.1", port=5001, loop=loop))
loop.run_forever()



