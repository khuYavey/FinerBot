from telebot import asyncio_filters
import telebot
from telebot import async_telebot
import asyncio
import datetime
import requests
from quart import Quart, request
import json
import locale

from photo_date_analyze import handle_photo
from location import analyze_location
from data_handling import photo_to_db, location_to_db, get_photo, confirmation, delete_from_db, upload_to_cloud
from universal_functions import cleaning_chat, get_data_from_bigdb

from api_data import client_bot_token as TOKEN, admin_chat_id


bot = async_telebot.AsyncTeleBot(TOKEN)
loop = asyncio.get_event_loop()

app = Quart(__name__)
locale.setlocale(locale.LC_TIME, 'uk_UA')
date_format = locale.nl_langinfo(locale.D_FMT)


@app.route('/approven', methods=['POST'])
async def approved():
    data = await request.get_json()
    time = data.get("date")
    id_ = await get_data_from_bigdb(date=time)
    time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    readable_time = time.strftime("%d %B %Y %H:%M")
    button = telebot.types.InlineKeyboardButton(url="https://www.buymeacoffee.com/Finerbot", text="Подяка")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button)
    await bot.send_message(chat_id=id_, text=f"Водія, авто якого ви зафіксували у {readable_time}, оштрафовано!\n"
                                             f"Дякуємо що скористались нашим рішенням", reply_markup=keyboard)
    return "Success", 200

@app.route('/non_valid', methods=['POST'])
async def non_valid():
    data = await request.get_json()
    time = data.get("date")
    id_ = await get_data_from_bigdb(date=time)
    time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    diference = datetime.datetime.now()-time
    if int(diference.seconds/60) < 60:
        button = telebot.types.InlineKeyboardButton(callback_data="/report_violation", text='Повторити')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(button)
        await bot.send_message(chat_id=id_, text=f"Ваш останній запит {int(diference.seconds/60)} хв тому не підійшов, можливо на фото не було видно порушення\nСпробуйте ще раз", reply_markup=keyboard)
    else:
        time = time.strftime("%d %B %Y %H:%M")
        await bot.send_message(chat_id=id_,
                               text=f"Ваш останній запит {time} нажаль не підійшов, скоріше за все на фото не було зафіксоване порушення")
    return "Success", 200

@app.route('/no_violation', methods=['POST'])
async def no_violation():
    data = await request.get_json()
    time = data.get("date")
    id_ = await get_data_from_bigdb(date=time)
    time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    time = time.strftime("%d %B %Y об %H:%M")
    await bot.send_message(chat_id=id_, text=f"Інспектор не виявив порушень правил парування на запиті, відправленому вами {time}")

def send_webhook():
    webhook_url = 'http://127.0.0.1:5001/new_data'
    data = {'name': 'This is an example for webhook'}
    requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
class ReportMode:
    report_mode = bool
    problem_mode = bool

    def __init__(self):
        self.report_mode = False
        self.problem_mode = False


    def report_set_True(self):
        self.report_mode = True
    def report_set_False(self):
        self.report_mode = False
    def report_get_status(self):
        return self.report_mode

    def problem_set_True(self):
        self.problem_mode = True
    def problem_set_False(self):
        self.problem_mode = False
    def problem_get_status(self):
        return self.problem_mode
state = ReportMode()

async def starting_menu(message, first_start=True):

    history_button = telebot.types.InlineKeyboardButton(text='Історія запитів', callback_data='/history')
    report_button = telebot.types.InlineKeyboardButton(text='Зафіксувати порушення', callback_data='/report_violation')
    problem_button = telebot.types.InlineKeyboardButton(text='Повідомити про помилку', callback_data='/report_problem')
    Menu_keyboard = telebot.types.InlineKeyboardMarkup().add(report_button).add(history_button).add(problem_button)
    if first_start:
        await bot.send_message(chat_id=message.chat.id, text="Для того щоб зафіксувати неправильно припарковане авто:\n\n1. Ввімкніть геолокацію\n2. Переконайтесь що на фото добре видно правопорушення\n3. Видно сам транспортний засіб", reply_markup=Menu_keyboard)  #TODO: написати інструкцію
        await cleaning_chat(bot, message, n=3)
    else:
        await bot.send_message(chat_id=message.chat.id, text="Меню", reply_markup=Menu_keyboard)

async def report_view(message):
    state.report_set_True()
    try:
        await bot.edit_message_text(chat_id=message.chat.id,
                     text='Користуючись вбудованою камерою в Telegram - сфотографуйте автомобіль дотримуючись інструкцій',message_id=message.id)
    except:
        await bot.send_message(chat_id=message.chat.id,
                                    text='Користуючись вбудованою камерою в Telegram - сфотографуйте автомобіль дотримуючись інструкцій')

async def report_problem(message):
    state.problem_set_True()
    await bot.send_message(chat_id=message.chat.id, text="Напишіть що вас турбує в роботі бота", reply_markup=telebot.types.ForceReply(
        input_field_placeholder="Опишіть свою проблему в полі"))  # TODO незнаю як зробити репорт проблем

async def history(id):
    await get_data_from_bigdb(id=id, bot=bot, user_history=True, automate=True)


'''для роботи команд з меню'''
@bot.message_handler(commands=['report_violation'])
async def nothing(message):
    try:
        delete_from_db(message.chat.id)
    except:
        pass
    await cleaning_chat(bot, message, n=1)
    await report_view(message)
@bot.message_handler(commands=['history'])
async def nothing_1(message):
    await history(message.chat.id)
@bot.message_handler(commands=['help'])
async def help(message):
    await starting_menu(message)
@bot.message_handler(commands=['report_problem'])
async def report1(message):
    await report_problem(message)



@bot.message_handler(commands=['start'])
async def send_welcome(message):

    Yes_button = telebot.types.KeyboardButton('Так')
    No_button = telebot.types.KeyboardButton('Ні')

    Permision_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    Permision_keyboard.add(Yes_button).add(No_button)

    await bot.send_message(chat_id=message.chat.id, text="Цей бот може аналізувати ТІЛЬКИ відправлені вами фото та геодані\n"
                          "Чи даєте ви на це дозвіл?",reply_markup=Permision_keyboard)


@bot.message_handler(text=['Ні'])
async def restart(message):

    if state.report_get_status() is False:
        restart_button = telebot.types.KeyboardButton('Перезавантажити')
        restart_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        restart_keyboard.add(restart_button)
        await bot.send_message(chat_id=message.chat.id,
                         text='Нажаль без дозволу на обробку даних ви не можете скористатись застосунком',
                         reply_markup=restart_keyboard)
    if state.report_get_status() is True:
        await cleaning_chat(bot, message, n=4)  # TODO визначити число n
        await starting_menu(message)
        delete_from_db(message.chat.id)
        state.report_set_False()

@bot.message_handler(text=['Перезавантажити'])
async def delete_all(message):
    if message.text == 'Перезавантажити':
        await cleaning_chat(bot, message, n=5)


@bot.message_handler(text=['Так'])
async def yes(message):
    await starting_menu(message)

@bot.callback_query_handler(func=lambda call: True) # для роботи кнопок на початковому екрані
async def menu_choise(call):
    if call.data == '/report_violation':
        await report_view(call.message)
    elif call.data == '/report_problem':
        await report_problem(call.message)
    elif call.data == '/help':
        await starting_menu(call.message)
    elif call.data == '/history':
        await history(call.message.chat.id)


@bot.message_handler(content_types=['photo'])
async def photo_analysys(message):
    if state.report_get_status() is True:
        send_button = telebot.types.KeyboardButton(text="Надіслати геолокацію", request_location=True)
        geo_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
        geo_keyboard.add(send_button)

        photo = await handle_photo(message, bot, TOKEN)
        photo_to_db(message.chat.id, photo[0], photo[1])
        # report_data.set_img_data(photo[0])#TODO тут тіко URL пікчі а не вона сама
        await bot.send_message(chat_id=message.chat.id, text="Для фіксації правопорушення потрібна геопозиція правопорушення",reply_markup=geo_keyboard)



        # await handle_photo(message, bot, TOKEN)  №TODO можливо зробити валідацію фото

    else:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.id)

        await bot.send_message(chat_id=message.chat.id, text="Для фіксації порушення натисніть /report_violation", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['location'])
async def location(message):
    if state.report_get_status():
        street_name = analyze_location(message.location.latitude, message.location.longitude)
        current_time = datetime.datetime.now()
        time_to_db = current_time.strftime("%Y-%m-%d %H:%M:%S")
        readable_time = current_time.strftime("%d %B %Y %H:%M")
        # readable_time = datetime.datetime.strptime(f"{current_time}", "%d %B %Y %H:%M")

        location_to_db(message.chat.id, message.location.latitude, message.location.longitude, time_to_db)


        await cleaning_chat(bot, message, n=3)
        if confirmation(message.chat.id) is True:
            button_yes = telebot.types.KeyboardButton(text="Підтверджую")
            button_no = telebot.types.KeyboardButton(text="Ні")
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(button_yes).add(button_no)


            await bot.send_message(chat_id=message.chat.id,text="Ви підтверджуєте сформований звіт?\n\n")
            await bot.send_photo(chat_id=message.chat.id, photo=get_photo(message.chat.id),
                                 caption=f"Місце порушення - {street_name}\n"
                                         f"Час фіксації - {readable_time}",
                                 reply_markup=keyboard)
        else:
            button = telebot.types.InlineKeyboardButton(text="Перезавантажити", callback_data="/report_violation")
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(button)
            await bot.send_message(chat_id=message.chat.id,text="Щось пішло не так...\n"
                                                                "Спробуйте ще раз", reply_markup=keyboard)
            delete_from_db(message.chat.id)


    else:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        await bot.send_message(chat_id=message.chat.id, text="Для фіксації порушення натисніть /report_violation")



@bot.message_handler(text=['Підтверджую'])
async def aproving_data(message):

    hide_keyboard = telebot.types.ReplyKeyboardRemove()
    await bot.send_message(chat_id=message.chat.id, text=f"Дякуємо, {message.from_user.first_name}, за вашу не байдужість\n\n"
                                                        "Ми повідомимо вам статус вашої заявки як тільки вона буде оброблена інспектором", reply_markup=hide_keyboard)
    await starting_menu(message, first_start=False)
    upload_to_cloud(message.chat.id)
    state.report_set_False()#TODO можливо виключення режиму правопорушення має бути не тут
    try:
        send_webhook()
    except:
        send_webhook()




@bot.message_handler(text=['Ні'])
async def start_over(message):
    if state.report_get_status() is True:
        await cleaning_chat(bot, message, n=4)#TODO визначити число n
        await starting_menu(message)
        delete_from_db(message.chat.id)
        state.report_set_False()

#для репорту проблем

@bot.message_handler(content_types=['text'])
async def problem(message):
    if state.problem_get_status() is True:
        await bot.forward_message(chat_id=admin_chat_id, from_chat_id=message.chat.id, message_id=message.id)
        await bot.send_message(chat_id=message.chat.id, text="Дякуємо,звернемо увагу")  # TODO зробити репорти в файл?
        state.problem_set_False()


bot.add_custom_filter(telebot.asyncio_filters.TextMatchFilter())


asyncio.ensure_future(bot.polling(none_stop=True))
asyncio.ensure_future(app.run(host="127.0.0.1", port=5002, loop=loop))
loop.run_forever()

