import os
import asyncio
import yt_dlp
from pyrogram import Client
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

# إعدادات متقدمة لـ yt-dlp (بدون cookiefile هنا)
YDL_OPTS = {
    "format": "bestaudio[filesize<10M]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "noplaylist": True,
    "outtmpl": "dl/%(id)s.%(ext)s",
    "concurrent_fragment_downloads": 8,
    "external_downloader": "aria2c",
    "external_downloader_args": ["-x", "16", "-s", "16", "-k", "1M"],
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "128",
    }],
    "ffmpeg_location": "/usr/bin/ffmpeg"
}

@app.on_message(command(["song", "/song", "بحث"]))
async def song_downloader(client, message):
    # الحصول على الكوكيز داخل الدالة غير المتزامنة
    cookies_path = await cookies()
    
    # تحديث YDL_OPTS بإضافة cookiefile
    ydl_opts_updated = {
        **YDL_OPTS,
        "cookiefile": cookies_path
    }
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        # مرحلة البحث السريع بدون تحميل
        with yt_dlp.YoutubeDL({**ydl_opts_updated, "skip_download": True}) as ydl:
            info = await asyncio.to_thread(
                ydl.extract_info,
                f"ytsearch1:{query}",
                download=False
            )
            
            if not info.get('entries'):
                return await m.edit("لم يتم العثور على نتائج.")
            
            entry = info['entries'][0]
            url = entry['webpage_url']
            title = entry['title'][:64]

        # مرحلة التحميل المنفصلة
        with yt_dlp.YoutubeDL(ydl_opts_updated) as ydl:
            await asyncio.to_thread(ydl.download, [url])
            audio_file = f"dl/{entry['id']}.mp3"

        # الإرسال المباشر
        await m.edit("<b>جـارِ الإرسال ♪</b>")
        await message.reply_audio(
            audio=audio_file,
            caption=f"<b>{title}</b>",
            duration=entry.get('duration', 0),
            performer=entry.get('uploader', 'Unknown')[:32],
            thumb=await get_thumbnail(entry['id']) if 'id' in entry else None
        )

    except Exception as e:
        await m.edit(f"خطأ: {str(e)[:150]}")
    finally:
        if 'audio_file' in locals():
            await safe_delete(audio_file)

async def get_thumbnail(video_id):
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

async def safe_delete(path):
    try:
        for _ in range(3):
            if os.path.exists(path):
                os.remove(path)
                break
            await asyncio.sleep(0.5)
    except:
        pass
