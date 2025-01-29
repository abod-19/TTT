from ZeMusic import app
import os
from nsfw_model import classify
from pyrogram import Client, filters
from PIL import Image

def is_explicit_image(image_path):
    img = Image.open(image_path)
    result = classify(img)
    return result.get("porn", 0) > 0.7

@app.on_message(filters.photo & filters.group)
async def filter_explicit_images(client, message):
    photo = message.photo[-1]
    file_path = await client.download_media(photo.file_id)

    if is_explicit_image(file_path):
        await message.delete()
        await message.reply_text("🚫 تم حذف الصورة لأنها غير لائقة!")

    os.remove(file_path)
