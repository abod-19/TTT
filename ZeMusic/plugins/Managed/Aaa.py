import asyncio
from pyrogram import Client, filters
from ZeMusic.utils.database import get_client
from pyrogram.enums import ChatType

# نص الرد التلقائي
AUTO_REPLY_TEXT = "مرحبًا! أنا روبوت مساعد، كيف يمكنني مساعدتك؟"

async def start_auto_reply():
    from ZeMusic.core.userbot import assistants
    
    if not assistants:
        print("لا يوجد حسابات مساعدة متاحة.")
        return
    
    num = assistants[0]  # استخدام أول حساب فقط
    client = await get_client(num)
    
    @client.on_message(filters.private)  # استقبال جميع الرسائل الخاصة
    async def reply_auto(client, message):
        try:
            await message.reply_text(AUTO_REPLY_TEXT)
        except Exception as e:
            print(f"خطأ أثناء الرد التلقائي: {e}")
    
    print("تم تشغيل نظام الرد التلقائي.")
    await client.start()
    await asyncio.Event().wait()  # إبقاء الحساب قيد التشغيل

# تشغيل وظيفة الرد التلقائي عند بدء التشغيل
asyncio.create_task(start_auto_reply())
