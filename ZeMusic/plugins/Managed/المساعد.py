from pyrogram import Client
from strings.filters import command
from config import BANNED_USERS
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ZeMusic import app
from ZeMusic.utils.database import get_assistant

@app.on_message(command(["المساعد", "الحساب المساعد"]) & ~BANNED_USERS)
async def assistant(c: Client, m: Message):
    userbot = await get_assistant(m.chat.id)
    usern = userbot.username
    aname = userbot.name
    idd = userbot.id

    info = await app.get_chat(idd)
    name = info.first_name
    bioo = info.bio

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(f"{name}", user_id=idd)
            ]]
    )

    # نستخدم async for للحصول على الصور
    photos = []
    async for photo in c.get_chat_photos(idd, limit=1):
        photos.append(photo)

    if not photos:
        # إذا لم يكن هناك صور
        await m.reply_text(f"⟡ معلومات الحساب المساعد :\n━━━━━━━━━━━━━\n• 𝙽𝚊𝚖𝚎 ↦ {aname}\n• 𝚄𝚜𝚎𝚛 ↦ @{usern}\n• 𝙱𝚒𝚘 ↦ {bioo}",reply_markup=keyboard)
    else:
        # إذا كانت هناك صورة
        await m.reply_photo(
            photos[0].file_id,
            caption=f"⟡ معلومات الحساب المساعد :\n━━━━━━━━━━━━━\n• 𝙽𝚊𝚖𝚎 ↦ {aname}\n• 𝚄𝚜𝚎𝚛 ↦ @{usern}\n• 𝙱𝚒𝚘 ↦ {bioo}",
            reply_markup=keyboard
        )
