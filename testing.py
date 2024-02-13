import asyncio
from quart import Quart
from telebot import async_telebot


TOKEN = "6705971192:AAG3clo4bB9pn4JMNHdTvTqbIc0oDQT5Sek"
bot = async_telebot.AsyncTeleBot(TOKEN)
admin_chat = '-4017494691'
app = Quart(__name__)

loop = asyncio.get_event_loop()

@app.route('/new_data', methods=['POST'])
async def get_webhook():
    await bot.send_message(chat_id=admin_chat, text="webhook")
    return "Success", 200

@bot.message_handler(commands=['start'])
async def fer(message):
    await bot.send_message(chat_id=admin_chat, text="start")




asyncio.ensure_future(bot.polling())
asyncio.ensure_future(app.run(host="127.0.0.1", port=5001, loop=loop))
loop.run_forever()
