import requests
from ZeMusic import app
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from MukeshAPI import api

@app.on_message(filters.command(["رون"],""))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            await message.reply_text(f"♪  اكتب <p>رون</p> واي شي تريد تسالة راح يجاوبك.")
        else:
            query = message.text.split(' ', 1)[1]
            response = api.chatgpt(query)["results"]
            await message.reply_text(f"<blockquote>{query}</blockquote>\n{response}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
