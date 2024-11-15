import asyncio
from ZeMusic import app 
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_NAME

italy = [
         "قول <pre style='color: red;'>{BOT_NAME}</pre> غنيلي",  # اللون الأحمر
         "<pre style='color: blue;'>هلا</pre>\nلبيه وش اغني لك"  # اللون الأزرق
         ]

@app.on_message(filters.regex(r"^(بوت)$"))
async def Italymusic(client, message):
    if "بوت" in message.text:
        response = random.choice(italy)
        response = response.format(nameuser=message.from_user.first_name, BOT_NAME=BOT_NAME)
        await message.reply(response, parse_mode=ParseMode.HTML)  # تفعيل التنسيق باستخدام HTML
