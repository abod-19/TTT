from ZeMusic import app
from pyrogram import Client, filters

@app.on_message(filters.command("account_creation"))
async def account_creation(client, message):
    user = await client.get_users(message.from_user.id)
    user_info = "\n".join([f"{attr}: {getattr(user, attr)}" for attr in dir(user) if not callable(getattr(user, attr)) and not attr.startswith("_")])
    await message.reply(f"معلومات المستخدم:\n{user_info}")
