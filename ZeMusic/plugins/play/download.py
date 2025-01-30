import os
import re
import asyncio
import yt_dlp
from pyrogram import Client
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

# تخزين الكوكيز مرة واحدة بدلاً من استدعائها في كل مرة
COOKIES = None

async def get_cookies():
    global COOKIES
    if not COOKIES:
        COOKIES = await cookies()
    return COOKIES

@app.on_message(command(["song", "/song", "بحث"]))
async def song_downloader(client, message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    ydl_opts = {
        "format": "bestaudio/best",  # أفضل تنسيق متاح مباشرة
        "quiet": True,
        "no_warnings": True,
        "geo_bypass": True,
        "cookiefile": await get_cookies(),
        "noplaylist": True,  # تجنب معالجة القوائم
        "outtmpl": "%(title)s.%(ext)s",  # اسم ملف أبسط
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ffmpeg_location": "/usr/bin/ffmpeg"  # تأكد من المسار الصحيح
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # البحث السريع مع تحديد النتائج
            info = await asyncio.to_thread(
                ydl.extract_info,
                f"ytsearch:{query}",
                download=True
            )
            
            if not info.get('entries'):
                return await m.edit("لم يتم العثور على نتائج.")
            
            entry = info['entries'][0]
            audio_file = ydl.prepare_filename(entry).replace('.webm', '.mp3')

            # إرسال الملف مباشرة بعد التحميل
            await m.edit("<b>جـارِ الإرسال ♪</b>")
            await message.reply_audio(
                audio=audio_file,
                caption=f"<b>{entry['title']}</b>",
                title=entry['title'][:64],
                performer=entry.get('uploader', 'Unknown')[:32],
                duration=entry.get('duration', 0)
            )

    except Exception as e:
        await m.edit(f"حدث خطأ: {str(e)[:200]}")
    finally:
        # التنظيف الآمن للملفات
        if 'audio_file' in locals() and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass
