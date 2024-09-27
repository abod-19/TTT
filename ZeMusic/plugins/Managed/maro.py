import asyncio
import time
from pyrogram import Client, filters, enums
from strings.filters import command
from config import BANNED_USERS, OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from ZeMusic import app, Telegram
from datetime import date
from ZeMusic.utils.database import get_assistant

async def get_time_and_date():
    today = date.today().strftime('%d/%m/%Y')
    clock = time.strftime("%I:%M")
    return today, clock


@app.on_message(command(["المساعد", "الحساب المساعد"]) & ~BANNED_USERS)
async def assistant(c: Client, m: Message):
    userbot = await get_assistant(m.chat.id)
    BOT_USERNAME = app.username
    aname = userbot.name
    anamee = userbot.mention
    idd = userbot.id
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
            reply_markup=keyboard)



@app.on_message(
    command(["بوت حذف", "بوت الحذف"])
    & ~filters.edited
    & ~BANNED_USERS
)
async def d(c: Client, m: Message):
    dusr = await c.get_users("Qrhel_Bot")
    BOT_USERNAME = app.username
    duser = dusr.username
    dname = dusr.first_name
    did = dusr.id
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{dname}", user_id=did)],
        [InlineKeyboardButton("ضيـف البـوت لمجمـوعتـك ✅",
                              url=f"https://t.me/{BOT_USERNAME}?startgroup=new")],
    ])
    if not c.get_chat_photos(did, limit=1):
                 await m.reply_text(f"[فكر جيدا قبل الحذف .. !](https://t.me/def_Zoka)", reply_markup=keyboard),
    async for photo in c.get_chat_photos(did, limit=1):
         await m.reply_photo(photo.file_id, caption=f"[فكر جيدا قبل الحذف .. !](https://t.me/def_Zoka)",
                            reply_markup=keyboard)
