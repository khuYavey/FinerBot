from telebot import asyncio_filters
import telebot
from telebot import async_telebot
import asyncio
import sqlite3
from quart import Quart
import requests
import json
import locale

from universal_functions import get_data_from_bigdb
from data_handling import change_status

from api_data import admin_bot_token as TOKEN, admin_chat_id


bot = async_telebot.AsyncTeleBot(TOKEN)
app = Quart(__name__)
loop = asyncio.get_event_loop()
locale.setlocale(locale.LC_TIME, 'uk_UA')
date_format = locale.nl_langinfo(locale.D_FMT)

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
    conn = sqlite3.connect("bigger.db")
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM inspectors')
    rows = cursor.fetchall()
    conn.close()
    for user_id in rows:
        if user_id[0] == call.message.chat.id:
            pass
        else:
            chat_to_delete = await bot.send_message(chat_id=user_id[0], text="Видалення")
            await bot.delete_message(chat_id=user_id[0], message_id=chat_to_delete.message_id, timeout=300)
            await bot.delete_message(chat_id=user_id[0], timeout=300,
                                         message_id=(chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2 - 1)))
            await bot.delete_message(chat_id=user_id[0], timeout=300,
                                         message_id=(chat_to_delete.message_id - ((len(rows) - rows.index(user_id)) * 2)))




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


asyncio.ensure_future(bot.polling(non_stop=True))
asyncio.ensure_future(app.run(host="127.0.0.1", port=5001, loop=loop))
loop.run_forever()



