import os
import asyncio
import yt_dlp
from pyrogram import Client
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

BASE_YDL_OPTS = {
    "format": "bestaudio[filesize<10M]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "noplaylist": True,
    "outtmpl": "dl/%(id)s.%(ext)s",
    "concurrent_fragment_downloads": 8,
    "external_downloader": "aria2c",
    "external_downloader_args": ["-x", "16", "-s", "16", "-k", "1M"],
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        },
        {
            "key": "FFmpegThumbnailsConvertor",
            "format": "jpg",
        }
    ],
    "writethumbnail": True,
    "ffmpeg_location": "/usr/bin/ffmpeg"
}

@app.on_message(command(["song", "/song", "بحث"]))
async def song_downloader(client, message):
    cookies_path = await cookies()
    ydl_opts = {**BASE_YDL_OPTS, "cookiefile": cookies_path}
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        # مرحلة البحث
        with yt_dlp.YoutubeDL({**ydl_opts, "skip_download": True}) as ydl:
            info = await asyncio.to_thread(
                ydl.extract_info,
                f"ytsearch1:{query}",
                download=False
            )
            
            if not info.get('entries'):
                return await m.edit("⚠️ لم يتم العثور على نتائج")
            
            entry = info['entries'][0]
            video_id = entry['id']
            url = entry['webpage_url']

        # مرحلة التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.to_thread(ydl.download, [url])
            
        audio_file = f"dl/{video_id}.mp3"
        thumb_file = f"dl/{video_id}.jpg"

        # الإرسال
        await m.edit("<b>📤 جـارِ الإرسال...</b>")
        await message.reply_audio(
            audio=audio_file,
            caption=f"🎧 <b>{entry['title'][:64]}</b>",
            duration=entry.get('duration', 0),
            performer=entry.get('uploader', 'Unknown')[:32],
            thumb=thumb_file if os.path.exists(thumb_file) else None
        )

    except Exception as e:
        await m.edit(f"❌ خطأ: {str(e)[:150]}")
    finally:
        # تنظيف الملفات
        for file_path in [audio_file, thumb_file]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
