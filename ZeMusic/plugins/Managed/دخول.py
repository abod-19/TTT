import asyncio
from pyrogram import Client, filters
from datetime import datetime
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, Message
from ZeMusic import app
from config import OWNER_ID
import os

@app.on_message(filters.new_chat_members)
async def get_chat_info(client, message):
    chat = message.chat
    dev_id = OWNER_ID
    if message.from_user.id == dev_id:
        info = await app.get_chat(dev_id)
        name = info.first_name
        
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(name, user_id=dev_id)
                ]
            ]
        )
        # نستخدم async for للحصول على الصور
        photos = []
        async for photo in client.get_chat_photos(dev_id, limit=1):
            photos.append(photo)

        if not photos:
            # إذا لم يكن هناك صور
            await message.reply_text(f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",reply_markup=markup)
        else:
            # إذا كانت هناك صورة
            await message.reply_photo(
                photos[0].file_id,
                caption=f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",
                reply_markup=markup)


"""


@app.on_message(filters.left_chat_member)
async def leftmem(client, message):
    await message.reply_text(f"
★ انت مش جدع يا «{message.left_chat_member.first_name}»
★ حد يكون في روم زي ده ويخرج 🥺❤️
★ ده حتى كلنا إخوات وأصحاب 🥺❤️
★ يلا بالسلامات 👋😂")
"""
