import locale
import asyncio
import threading

import admin_side
import client_side
import webhook_client_side
import webhook_admin_side

locale.setlocale(locale.LC_TIME, 'uk_UA')
date_format = locale.nl_langinfo(locale.D_FMT)

loop = asyncio.get_event_loop()

# async def all():


    # task2 = asyncio.create_task(webhook_client_side.app.run(host="127.0.0.1", port=5002))

if __name__ == "__main__":
    asyncio.run(client_side.bot.polling())



# if __name__ == "__main__":
#
#     asyncio.ensure_future()
#     asyncio.run_coroutine_threadsafe(client_side.bot.polling(), loop=loop)
#     # client_bot = threading.Thread(target=client_side.bot)
#     client_webserver = threading.Thread(target=webhook_client_side.app.run(host="127.0.0.1", port=5002))
#     # admin_bot = threading.Thread(target=asyncio.run(admin_side.bot.polling()))
#     # admin_webserver = threading.Thread(target=webhook_admin_side.app.run(host="127.0.0.1", port=5001))
#
#
#     #
#     # client_bot.start()
#     # admin_bot.start()
#     # admin_webserver.start()
#
#     print(client_webserver.isAlive())


