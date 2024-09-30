from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import ChatMemberUpdated
from ZeMusic import app

@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    for new_member in message.new_chat_members:
        if new_member.id == 5145609515:
            chat_id = message.chat.id
            user_mention = new_member.mention
            await client.send_message(chat_id, f"مرحبًا بك يا {user_mention} في المجموعة!")
