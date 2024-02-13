from quart import Quart

app = Quart(__name__)

@app.route('/new_data', methods=['POST'])
async def get_webhook():
    await get_data_from_bigdb(id=admin_chat_id, bot=bot, admin=True, automate=True)
    return "Success", 200
