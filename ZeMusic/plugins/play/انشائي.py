from ZeMusic import app
from pyrogram import Client, filters
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.raw.types import InputUserSelf
import datetime


@app.on_message(filters.command(["انشائي"],""))
async def account_creation(client, message):
    user_full_info = await client.invoke(GetFullUser(id=InputUserSelf()))
    user = user_full_info.users[0]
    creation_date = datetime.datetime.fromtimestamp(user.date)
    await message.reply(f"تم إنشاء حسابك في: {creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
