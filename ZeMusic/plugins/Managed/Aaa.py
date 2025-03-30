import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType

from ZeMusic import app
from ZeMusic.utils.database import get_client

# الرد التلقائي من الحسابات المساعدة عند استقبال رسالة في الخاص
async def auto_reply_assistants():
    from ZeMusic.core.userbot import assistants
    for num in assistants:
        client = await get_client(num)
        @client.on_message(filters.private & ~filters.me)
        async def auto_reply(client, message):
            try:
                await message.reply_text("هذا حساب مساعد وليس مستخدم وهذا #رد_تلقائي")
            except:
                pass

# تشغيل الرد التلقائي عند تشغيل الكود
asyncio.create_task(auto_reply_assistants())
