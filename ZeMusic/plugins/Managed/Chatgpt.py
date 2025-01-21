import requests
from ZeMusic import app
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from MukeshAPI import api
import json  # لإجراء تحويل JSON إذا لزم الأمر

@app.on_message(filters.command(["رون"], ""))
async def chat_gpt(bot, message):
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        if len(message.command) < 2:
            await message.reply_text("♪  اكتب <p>رون</p> واي شي تريد تسالة راح يجاوبك.")
        else:
            query = message.text.split(' ', 1)[1]
            
            # استدعاء الـ API
            response = api.chatbot(query)
            
            # التحقق من نوعية الرد
            if isinstance(response, str):  # إذا كان الرد سلسلة نصية، قم بتحويله
                response = json.loads(response)

            # تحقق إذا كانت النتيجة تحتوي على المفتاح المطلوب
            if "results" in response:
                result = response["results"]
                await message.reply_text(f"{result}", parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply_text("لا توجد نتائج متاحة في الرد.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
