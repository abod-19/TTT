from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from ZeMusic import app

@app.on_chat_member_updated(filters.group)
async def welcome_new_member(client: Client, chat_member_update: ChatMemberUpdated):
    if chat_member_update.new_chat_member.user.id == 5145609515 and chat_member_update.new_chat_member.status == "member":
        chat_id = chat_member_update.chat.id
        user_mention = chat_member_update.new_chat_member.user.mention
        await client.send_message(chat_id, f"مرحبًا بك يا {user_mention} في المجموعة!")
