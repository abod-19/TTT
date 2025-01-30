import os
import asyncio
import yt_dlp
from pyrogram import Client
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

# إعدادات متقدمة مع تحسينات السرعة القصوى
ULTRA_FAST_OPTS = {
    "format": "bestaudio[filesize<5M]/bestaudio",
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "noplaylist": True,
    "outtmpl": "dl/%(id)s.%(ext)s",
    "concurrent_fragment_downloads": 16,
    "external_downloader": "aria2c",
    "external_downloader_args": ["-x", "32", "-s", "32", "-k", "2M"],
    "postprocessor_args": ["-threads", "8"],
    "writethumbnail": True,
    "ffmpeg_location": "/usr/bin/ffmpeg",
    "socket_timeout": 10,
    "source_address": "0.0.0.0",
    "cachedir": False,
    "noprogress": True,
    "allow_multiple_audio_streams": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "96",
        },
        {
            "key": "FFmpegThumbnailsConvertor",
            "format": "jpg",
            "when": "before_dl"
        }
    ]
}

@app.on_message(command(["song", "/song", "بحث"]))
async def ultra_fast_downloader(client, message):
    cookies_path = await cookies()
    ydl_opts = {**ULTRA_FAST_OPTS, "cookiefile": cookies_path}
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>⚡ معالجة سريعة...</b>")
    
    try:
        # البحث الفوري مع التحميل المباشر
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(
                ydl.extract_info,
                f"ytsearch1:{query}",
                download=True
            )
            
            if not info.get('entries'):
                return await m.edit("⚠️ لم يتم العثور على النتائج")
            
            entry = info['entries'][0]
            video_id = entry['id']
            audio_file = f"dl/{video_id}.mp3"
            thumb_file = f"dl/{video_id}.jpg"

        # الإرسال الفوري مع التحميل المسبق
        await message.reply_chat_action("upload_audio")
        await m.edit("<b>🚀 جـارِ الإرسال الفوري...</b>")
        await message.reply_audio(
            audio=audio_file,
            caption=f"🎧 {entry['title'][:64]}",
            duration=entry.get('duration', 0),
            performer=entry.get('uploader', 'Unknown')[:32],
            thumb=thumb_file if os.path.exists(thumb_file) else None,
            file_name=entry['title'][:64] + ".mp3"
        )

    except Exception as e:
        await m.edit(f"❌ خطأ فوري: {str(e)[:100]}")
    finally:
        # تنظيف فوري للملفات
        for f in [audio_file, thumb_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
