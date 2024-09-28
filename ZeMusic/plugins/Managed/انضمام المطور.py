import yt_dlp
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic.platforms.Youtube import cookie_txt_file
import config

# إعدادات البوت (افتراضياً)


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
    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

    await message.reply_text("جارٍ البحث عن الأغنية وتنزيلها...")

    # إعداد yt-dlp لتنزيل الملف الصوتي
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            'cookiefile': cookie_txt_file(),
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
