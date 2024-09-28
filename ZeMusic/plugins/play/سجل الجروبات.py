import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from ZeMusic import app
from ZeMusic.utils.database import get_served_chats
from config import LOGGER_ID

photo = [
    "https://te.legra.ph/file/758a5cf4598f061f25963.jpg",
    "https://te.legra.ph/file/30a1dc870bd1a485e3567.jpg",
    "https://te.legra.ph/file/d585beb2a6b3f553299d2.jpg",
    "https://te.legra.ph/file/7df9e128dd261de2afd6b.jpg",
    "https://te.legra.ph/file/f60ebb75ad6f2786efa4e.jpg",
]

async def lul_message(chat_id: int, message: str):
    await app.send_message(chat_id=chat_id, text=message)


@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    if (await client.get_me()).id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.first_name if message.from_user else "مستخدم غير معروف"
        added_id = message.from_user.id

        matlabi_jhanto = message.chat.title
        served_chats = len(await get_served_chats())
        chat_id = message.chat.id

        chat = await client.get_chat(int(chat_id))
        cont = chat.members_count
        
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        lemda_text = (
            f"🌹 تمت إضافة البوت إلى مجموعة جديدة.\n\n"
            f"┏━━━━━━━━━━━━━━━━━┓\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃</b> › : {matlabi_jhanto}\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃 𝙸𝙳</b> › : {chat_id}\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃 𝚄𝙽𝙰𝙼𝙴</b> › : {chatusername}\n"
            f"┣★ <b>𝙲𝙾𝚄𝙽𝚃</b> › : {cont}\n"
            f"┣★ <b>𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂</b> › : {served_chats}\n"
            f"┣★ <b>𝙰𝙳𝙳𝙴𝙳 𝙱𝚈</b> › :\n"
            f"┗━━━ꪜ <a href='tg://user?id={added_id}'>{added_by}</a>"
        )
        await lul_message(LOGGER_ID, photo=random.choice(photo), lemda_text, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{added_by}", url=f"tg://openmessage?user_id={added_id}")
                    ]
                ]
            ))
