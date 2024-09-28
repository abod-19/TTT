import yt_dlp
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic.platforms.Youtube import cookie_txt_file
from ZeMusic import app
import config

# الإعدادات الخاصة بالبوت
lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = config.BOT_NAME + " ابحث"

# تعريف دالة التنزيل
@app.on_message(filters.command(["song", "/song", "بحث", Nem, "تنزيل"]))
async def song_downloader(client: Client, message: Message):
    # الحصول على رابط اليوتيوب من رسالة المستخدم
    if len(message.command) < 2:
        await message.reply_text("يرجى إدخال رابط اليوتيوب أو اسم الأغنية بعد الأمر.")
        return

    search_query = " ".join(message.command[1:])
    await message.reply_text("جارٍ البحث عن الأغنية وتنزيلها...")

    # إعداد yt-dlp لتنزيل الملف الصوتي
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,  # تأكد من عدم تنزيل قائمة تشغيل
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': cookie_txt_file(),  # وضع المسار إلى ملف cookies.txt هنا
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # البحث عن الفيديو وتنزيله
            info = ydl.extract_info(f"ytsearch:{search_query}", download=True)
            audio_file = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        # إرسال الملف الصوتي
        await message.reply_audio(audio_file)
        
        # حذف الملف بعد الإرسال
        os.remove(audio_file)

    except Exception as e:
        await message.reply_text(f"حدث خطأ أثناء التنزيل: {str(e)}")
