import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ZeMusic import app
from config import OWNER_ID, BOT_NAME
import config

lnk = "https://t.me/" + config.CHANNEL_LINK

@app.on_message(filters.regex(r"^(المطور|مطور)$"))
async def devid(c: Client, m: Message):
    usr = await client.get_users(OWNER_ID)
    name = usr.first_name
    usrnam = usr.username
    idd = usr.id
 
    info = await app.get_chat(idd)
    bioo = info.bio
    
    aname = f"<a href='tg://user?id={idd}'>{name}</a>"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
                InlineKeyboardButton(f"{name}", url=f"tg://openmessage?user_id={idd}")
            ]]
    )

    # نستخدم async for للحصول على الصور
    photos = []
    async for photo in c.get_chat_photos(idd, limit=1):
        photos.append(photo)

    if not photos:
        # إذا لم يكن هناك صور
        await m.reply_text(f"⟡ 𝙳𝚎𝚟 𝙱𝚘𝚝 ↦ {BOT_NAME}\n━━━━━━━━━━━━━\n• 𝙽𝚊𝚖𝚎 ↦ {aname}\n• 𝚄𝚜𝚎𝚛 ↦ @{usrnam}\n• 𝙱𝚒𝚘 ↦ {bioo}",reply_markup=keyboard)
    else:
        # إذا كانت هناك صورة
        await m.reply_photo(
            photos[0].file_id,
            caption=f"⟡ 𝙳𝚎𝚟 𝙱𝚘𝚝 ↦ {BOT_NAME}\n━━━━━━━━━━━━━\n• 𝙽𝚊𝚖𝚎 ↦ {aname}\n• 𝚄𝚜𝚎𝚛 ↦ @{usrnam}\n• 𝙱𝚒𝚘 ↦ {bioo}",
            reply_markup=keyboard
        )

    """
    await message.reply_photo(
        photo=photo_path,
        caption=f"<b>⌯ 𝙳𝚎𝚟 :</b> <a href='tg://user?id={OWNER_ID}'>{name}</a>\n\n<b>⌯ 𝚄𝚂𝙴𝚁 :</b> @{usrnam}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(name, url=f"tg://user?id={OWNER_ID}"),
                ],
                [
                    InlineKeyboardButton(
                        text=config.CHANNEL_NAME, url=lnk),
                ],
            ]
        ),)
    """
