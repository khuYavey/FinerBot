from quart import Quart, request


app = Quart(__name__)
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

