import requests
from PIL import Image
from io import BytesIO


async def handle_photo(message, bot, TOKEN):
    photos = message.photo

    # Get the last (largest) photo from the list
    photo = photos[-1]

    # Get the file ID of the photo
    file_id = photo.file_id

    # Get the photo information from Telegram servers
    file_info = await bot.get_file(file_id)

    # Construct the URL for the photo
    photo_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'

    # # Use the photo URL to download the photo (optional)
    photo_itself = requests.get(photo_url).content




    return file_info.file_id, photo_itself

async def handle_photo_for_db(file_info, TOKEN):

    # Construct the URL for the photo
    photo_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'

    # # Use the photo URL to download the photo (optional)
    photo_itself = requests.get(photo_url).content
    #
    # # Create an image object using Pillow


    return photo_itself