import random
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from YukkiMusic import app
from YukkiMusic.utils.database import get_served_chats
from config import OWNER_ID, LOGGER_ID
from datetime import datetime, timedelta
from pyrogram.enums import ChatMemberStatus

photo_urls = [
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
]

@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    chat = message.chat
    dev_id = OWNER_ID
    for new_member in message.new_chat_members:
        if new_member.id == dev_id:
            chat_id = message.chat.id
            info = await app.get_chat(dev_id)
            name = info.first_name
            markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(name, user_id=dev_id)]
                ]
            )

            photos = []
            async for photo in client.get_chat_photos(dev_id, limit=1):
                photos.append(photo)

            if not photos:
                await message.reply_text(
                    f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",
                    reply_markup=markup
                )
            else:
                await message.reply_photo(
                    photos[0].file_id,
                    caption=f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",
                    reply_markup=markup
                )

    # جزء التعامل مع إضافة البوت إلى مجموعة جديدة
    if (await client.get_me()).id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.first_name if message.from_user else "مستخدم غير معروف"
        added_id = message.from_user.id
        matlabi_jhanto = message.chat.title
        served_chats = len(await get_served_chats())
        cont = await app.get_chat_members_count(chat.id)
        chatusername = message.chat.username if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜ𝑝"
        lemda_text = (
            f"🌹 تمت إضافة البوت إلى مجموعة جديدة.\n\n"
            f" <b>𝙲𝙷𝙰𝚃</b> › : {matlabi_jhanto}\n"
            f" <b>𝙲𝙷𝙰𝚃 𝙸𝙳</b> › : {chat.id}\n"
            f" <b>𝙲𝙷𝙰𝚃 𝚄𝙽𝙰𝙼𝙴</b> › : @{chatusername}\n"
            f" <b>𝙲𝙾𝚄𝙽𝚃</b> › : {cont}\n"
            f" <b>𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂</b> › : {served_chats}\n"
            f" <b>𝙰𝙳𝙳𝙴𝙳 𝙱𝚈</b> › :\n"
            f" <a href='tg://user?id={added_id}'>{added_by}</a>"
        )
        await app.send_photo(
            LOGGER_ID,
            photo=random.choice(photo_urls),
            caption=lemda_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(f"{added_by}", url=f"tg://openmessage?user_id={added_id}")]
                ]
            )
        )
    else:
        # التعامل مع الأعضاء الجدد الآخرين
        chat = await app.get_chat(message.chat.id)
        chat_name = chat.title
        chat_photo = chat.photo
        chat_id = message.chat.id
        async for member in client.get_chat_members(chat_id):
            if member.status == ChatMemberStatus.OWNER:
                owner_id = member.user.id
                owner_name = member.user.first_name

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f"{owner_name}", url=f"tg://openmessage?user_id={owner_id}")]
            ]
        )

        for new_member in message.new_chat_members:
            first_name = new_member.mention
            username = new_member.username
            now = datetime.utcnow() + timedelta(hours=3)
            join_time = now.strftime("%I:%M %p")
            join_date = now.strftime("%Y/%m/%d")

            welcome_text = f"""
𝐰𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩.🧸

__{chat_name}__

➥• Welcome  : {first_name} 
➥• User : @{username if username else 'No username'}  
➥• time : {join_time}
➥• date : {join_date}
"""
            if chat_photo:
                photo_file = await client.download_media(chat_photo.big_file_id)
                await message.reply_photo(
                    photo=photo_file,
                    caption=welcome_text,
                    reply_markup=keyboard
                )
            else:
                await message.reply_text(welcome_text, reply_markup=keyboard)
