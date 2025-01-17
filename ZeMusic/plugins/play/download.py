import os
import re
import yt_dlp
from pyrogram import Client
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

@app.on_message(command(["song", "/song", "بحث"]))
async def song_downloader(client, message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "quiet": True,
        "geo_bypass": True,
        "cookiefile": f"{await cookies()}",
    }

    try:
        # البحث وتنزيل الصوت
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if not info or 'entries' not in info or not info['entries']:
                await m.edit("لم يتم العثور على نتائج.")
                return
            
            first_entry = info['entries'][0]
            title = first_entry.get("title", "Unknown Title")
            duration = first_entry.get("duration", 0)

            # تنظيف اسم الملف وإعداد مسار الصوت
            audio_file = ydl.prepare_filename(first_entry).replace('.webm', '.mp3')
            
            # إرسال الملف الصوتي
            await m.edit("<b>جـارِ الإرسال ♪</b>")
            await message.reply_audio(
                audio=audio_file,
                caption=f"<b>{title}</b>",
                title=title,
                performer=first_entry.get("uploader", "Unknown"),
                duration=duration,
            )

    except Exception as e:
        await m.edit(f"حدث خطأ: {e}")
    finally:
        # حذف الملف الصوتي المؤقت بعد الإرسال
        if os.path.exists(audio_file):
            os.remove(audio_file)
