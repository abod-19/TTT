import os
import config
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch

# إعداد عميل Pyrogram
a = Client(
    name="ZeAss1",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=str(config.STRING1),
    no_updates=True,
)

GROUP_ID = -1002138912008  # معرف المجموعة

# تعريف دالة البحث عن الأغاني
@a.on_message(filters.command(["song", "بحث", "تحميل"]))
async def song_downloader(client: Client, message: Message):
    # استخراج استعلام البحث من الأمر
    query = " ".join(message.command[1:])
    if not query:
        await message.reply_text("❌ الرجاء إدخال اسم الأغنية للبحث.")
        return

    # إرسال رسالة انتظار
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")

    try:
        # البحث عن الفيديو في YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("❌ لم يتم العثور على نتائج في YouTube.")
            return

        video_id = results[0]['id']

        # البحث في المجموعة عن الرسائل التي تحتوي على مقطع صوتي
        async for msg in a.search_messages(chat_id=GROUP_ID, query=video_id):
            if msg.audio or msg.voice:  # تحقق من وجود ملف صوتي أو رسالة صوتية
                await a.send_voice(
                    chat_id=message.chat.id,
                    voice=msg.audio.file_id if msg.audio else msg.voice.file_id,
                    caption="🤍 تم العثور على الأغنية!",
                    reply_to_message_id=message.id
                )
                await m.delete()
                return

        # إذا لم يتم العثور على مقطع صوتي
        await m.edit("❌ لم يتم العثور على أي مقاطع صوتية تحتوي على النص المطلوب.")
    
    except Exception as e:
        # التعامل مع الأخطاء
        await m.edit(f"❌ حدث خطأ أثناء البحث: {e}")

# تشغيل العميل
a.run()
