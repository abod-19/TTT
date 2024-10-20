import random
from pyrogram import Client, filters
from ZeMusic.core.userbot import Userbot
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from config import LOGGER_ID as LOG_ID
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.decorators import AdminActual
from ZeMusic.utils.database import is_loge_enabled, enable_loge, disable_loge
from ZeMusic import app
from pyrogram.enums import ChatMemberStatus

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
    
    # جلب معلومات المالك
    async for member in client.get_chat_members(chat_id):
        if member.status == ChatMemberStatus.OWNER:
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

    if (await client.get_me()).id == message.left_chat_member.id:
        # إذا كان البوت هو الذي تم طرده
        remove_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = (f"@{message.chat.username}" if message.chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐂ʜᴀᴛ")
        rirurubye = f"✫ <b><u>ـ تم طرد البوت من المجموعه</u></b> :\n\nᴄʜᴀᴛ ɪᴅ : {chat_id}\nᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\nᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\nʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}"
        
        await app.send_photo(
            LOG_ID,
            photo=random.choice(photo),
            caption=rirurubye,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            message.from_user.first_name,
                            user_id=message.from_user.id
                        )
                    ]
                ]
            )
        )
        await userbot.one.start()
        
        try:
            await userbot.one.leave_chat(chat_id)
        except Exception as e:
            # تجاهل الخطأ إذا حدث أثناء مغادرة البوت للمحادثة
            print(f"Error leaving chat: {e}")
    else:
        try:
            chat_id = message.chat.id
            if not await is_loge_enabled(chat_id):
                return
            # إذا كان المستخدم العادي هو الذي غادر
            await app.send_message(user_id, 
                f"<b>• في امان الله ياعيوني يا 〖 {message.left_chat_member.mention} ⁪⁬⁮⁮⁮⁮〗.\n</b>"
                f"<b>• اذا فكرت ترجع قروبنا {gti}\n</b>"
                f"<b>• اذا كان سبب مغادرتك ازعاج من مشرف\n</b>"
                f"<b>• يمكنك تقديم شكوه للمالك والرجوع للجروب\n</b>"
                f"<b>• من خلال الازرار بالاسفل 🧚🏻‍♀️</b>"
                f"<a href='{link}'>ㅤ</a>",
                reply_markup=reply_markup
            )
        except Exception as e:
            # تجاهل الأخطاء إذا حدثت في else
            print(f"من غادر هو المالك او مستخدم غير معروف: {e}")


@app.on_message(command(["تعطيل المغادرة الذكي"]) & filters.group)
@AdminActual
async def disable_loge_command(client, message: Message, _):
    chat_id = message.chat.id  # الحصول على معرف الدردشة
    if not await is_loge_enabled(chat_id):
        await message.reply_text("<b>المغادرة الذكي معطل من قبل.</b>")
        return
    await disable_loge(chat_id)
    await message.reply_text("<b>تم تعطيل المغادرة الذكي بنجاح.</b>")

#######&&&&&&#######

#امر للتفعيل
@app.on_message(command(["تفعيل المغادرة الذكي"]) & filters.group)
@AdminActual
async def enable_loge_command(client, message: Message, _):
    chat_id = message.chat.id  # الحصول على معرف الدردشة
    if await is_loge_enabled(chat_id):
        await message.reply_text("<b>المغادرة الذكي مفعل من قبل.</b>")
        return
    await enable_loge(chat_id)
    await message.reply_text("<b>تم تفعيل المغادرة الذكي بنجاح.</b>")
