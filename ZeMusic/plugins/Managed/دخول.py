import asyncio
from pyrogram import Client, filters
from datetime import datetime
from ZeMusic import app

@app.on_message(filters.new_chat_members)
async def get_chat_info(client, message):
    chat = message.chat
    members = await client.get_chat_members_count(chat.id)
    await message.reply_text(f"""
● نورت يقمر ♥♡
{message.from_user.first_name}
● يجب احترام الادمنية
● الالتزام بالقوانين في الوصف
● الأعضاء: {members}
""")

@app.on_message(filters.left_chat_member)
async def leftmem(client, message):
    await message.reply_text(f"""
★ انت مش جدع يا «{message.left_chat_member.first_name}»
★ حد يكون في روم زي ده ويخرج 🥺❤️
★ ده حتى كلنا إخوات وأصحاب 🥺❤️
★ يلا بالسلامات 👋😂
""")

app.run()
