from pyrogram import Client
from strings.filters import command
from config import BANNED_USERS
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ZeMusic import app
from ZeMusic.utils.database import get_assistant

@app.on_message(command(["المساعد", "الحساب المساعد"]) & ~BANNED_USERS)
async def assistant(c: Client, m: Message):
    userbot = await get_assistant(m.chat.id)
    print(type(userbot))
    BOT_USERNAME = app.username
    aname = userbot.name
    idd = userbot.id
    anamee = f"<a href='tg://user?id={idd}'>{aname}</a>"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
        [
            InlineKeyboardButton(
                f"{aname}", user_id=idd)
        ],[
            InlineKeyboardButton(
                "ضيـف البـوت لمجمـوعتـك ✅", url=f"https://t.me/{BOT_USERNAME}?startgroup=new")
        ],
    ])
    if not await c.get_chat_photos(idd, limit=1):
        await m.reply_text(f"• الحساب المساعد الخاص بالبوت:\n{anamee}\n√", reply_markup=keyboard),
    async for photo in c.get_chat_photos(idd, limit=1):
        await m.reply_photo(
            photo.file_id, caption=f"• الحساب المساعد الخاص بالبوت:\n{anamee}\n√",
            reply_markup=keyboard
        )
