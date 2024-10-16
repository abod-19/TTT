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
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
]

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    chat = await app.get_chat(message.chat.id)
    gti = chat.title
    link = await app.export_chat_invite_link(message.chat.id)

    user_id = message.left_chat_member.id

    chat_id = message.chat.id
    async for member in client.get_chat_members(chat_id):
        if member.status == ChatMemberStatus.OWNER:  # جلب منشئ المجموعة فقط
            owner_id = member.user.id
            owner_name = member.user.first_name

    buttons = [
        [
            InlineKeyboardButton(f"{owner_name}", url=f"tg://openmessage?user_id={owner_id}")
        ],[
            InlineKeyboardButton(gti, url=f"{link}")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await app.send_message(user_id, f"<b>• في امان الله ياعيوني يا 〖 {message.left_chat_member.mention} ⁪⁬⁮⁮⁮⁮〗.\n</b>"
                                    f"<b>• اذا فكرت ترجع قروبنا {gti}\n</b>"
                                    f"<b>• اذا كان سبب مغادرتك ازعاج من مشرف\n</b>"
                                    f"<b>• يمكنك تقديم شكوه للمالك  والرجوع للجروب\n</b>"
                                    f"<b>• من خلال الازرار بالاسفل 🧚🏻‍♀️</b>"
                                    f"<a href='{link}'>ㅤ</a>",
                                    reply_markup=reply_markup)


########################################################################
########################################################################

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
