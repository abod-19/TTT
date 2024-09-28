import random
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    if (await client.get_me()).id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.first_name if message.from_user else "مستخدم غير معروف"
        added_id = message.from_user.id if message.from_user else None

        matlabi_jhanto = message.chat.title
        served_chats = len(await get_served_chats())
        chat = message.chat
        cont = await app.get_chat_members_count(chat.id)
        chatusername = (message.chat.username if message.chat.username else "مجموعة خاصة")

        # إنشاء النص
        lemda_text = (
            f"🌹 تمت إضافة البوت إلى مجموعة جديدة.\n\n"
            f"┏━━━━━━━━━━━━━━━━━┓\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃</b> › : {matlabi_jhanto}\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃 𝙸𝙳</b> › : {chat.id}\n"
            f"┣★ <b>𝙲𝙷𝙰𝚃 𝚄𝙽𝙰𝙼𝙴</b> › : {chatusername}\n"
            f"┣★ <b>𝙲𝙾𝚄𝙽𝚃</b> › : {cont}\n"
            f"┣★ <b>𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂</b> › : {served_chats}\n"
        )

        if added_id:
            # إذا كان معرف المستخدم متوفر، أضف تفاصيل الشخص الذي أضاف البوت
            lemda_text += f"┣★ <b>𝙰𝙳𝙳𝙴𝙳 𝙱𝚈</b> › :\n┗━━━ꪜ <a href='tg://user?id={added_id}'>{added_by}</a>"
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{added_by}", user_id=added_id
                        )
                    ]
                ]
            )
        else:
            # إذا كان معرف المستخدم غير متوفر، أضف رسالة عامة
            lemda_text += "┗━━━ꪜ <b>𝙰𝙳𝙳𝙴𝙳 𝙱𝚈</b> › : مستخدم غير معروف"
            reply_markup = None

        # إرسال الرسالة مع الصورة
        await app.send_photo(
            LOGGER_ID,
            photo=random.choice(photo),
            caption=lemda_text,
            reply_markup=reply_markup
        )
