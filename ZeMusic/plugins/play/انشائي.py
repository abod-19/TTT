from pyrogram import Client, filters
import datetime
from ZeMusic import app


@app.on_message(filters.command(["انشائي"],""))
async def account_creation(client, message):
    user = await client.get_users(message.from_user.id)
    creation_date = datetime.datetime.fromtimestamp(user.date)
    await message.reply(f"تم إنشاء حسابك في:\n{creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
