import random
from pyrogram import Client, filters
from ZeMusic.core.userbot import Userbot
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from config import LOGGER_ID as LOG_ID
from ZeMusic import app

userbot = Userbot()

photo = [
    "https://graph.org/file/872dc8af2a36bed43b9b6.jpg",
    "https://graph.org/file/f4b34351a59061ba1c61b.jpg",
    "https://graph.org/file/3fb3f4c8a1250c6a50af1.jpg",
    "https://graph.org/file/eabab7e8a3e5df87a0b04.jpg",
    "https://graph.org/file/427f4869a158126957747.jpg",
]

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    if (await client.get_me()).id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = (f"@{message.chat.username}" if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ")
        chat_id = message.chat.id
        rirurubye = f"✫ <b><u>ـ تم طرد البوت من المجموعه</u></b> :\n\nᴄʜᴀᴛ ɪᴅ : {chat_id}\nᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\nᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\nʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}"
        #reply_markup = InlineKeyboardMarkup(
        #[[
            #InlineKeyboardButton(
            #message.from_user.first_name,
            #user_id=message.from_user.id)
        #]])
        
        await app.send_photo(
            LOG_ID,
            photo=random.choice(photo),
            caption=rirurubye,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            message.from_user.first_name,
                            user_id=message.from_user.id)
                    ]
                ]
            )
        )
        await userbot.one.start()
        await userbot.one.leave_chat(chat_id)
