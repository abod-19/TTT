import os
import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic import app

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

W = [0]
lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = f"{config.BOT_NAME} ابحث"
Nam = f"{config.BOT_NAME} بحث"

@app.on_message(filters.command(["song", "يوت", "يو", Nem, Nam]))
async def song_downloader(client, message: Message):
    if message.text in ["song", "/song", "بحث", Nem, Nam]:
        return
    
    if message.command[0] in config.BOT_NAME:
        query = " ".join(message.command[2:])
    else:
        query = " ".join(message.command[1:])
    
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        # البحث عن الفيديو في YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
            return
        
        # البحث في القناة
        channel_id = "IC_l9"  # استبدل هذا بمعرف القناة الخاص بك
        search_text = results[0]['id']
        
        async for msg in client.search_messages(chat_id=channel_id, query=search_text):
            if msg.voice:  # تحقق إذا كانت الرسالة تحتوي على مقطع صوتي
                # إرسال المقطع الصوتي إلى المستخدم
                await client.send_voice(
                    chat_id=message.chat.id,
                    voice=msg.voice.file_id,
                    caption="🤍",
                    reply_to_message_id=message.id,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=config.CHANNEL_NAME, url=lnk
                                )
                            ],
                        ]
                    )
                )
                return  # إنهاء الوظيفة بعد إرسال الصوت

        # إذا لم يتم العثور على مقطع صوتي
        await m.edit("لم يتم العثور على أي مقاطع صوتية تحتوي على النص المطلوب.")
    
    except Exception as e:
        # التعامل مع الأخطاء
        await m.edit(f"حدث خطأ أثناء البحث: {e}")
